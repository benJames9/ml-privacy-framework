import torch
from common import AttackParameters, AttackProgress, AttackStatistics, WorkerQueue
from breaching.breaching.attacks.attack_progress import (
    AttackProgress as BreachingAttackProgress,
)
import breaching.breaching as breachinglib
from torchvision import models as visionModels
import transformers as textModels
import logging, sys
import base64
import zipfile
import os, shutil
from ConfigBuilder import ConfigBuilder
import tempfile
import time
from functools import partial
from dataclasses import dataclass
import zipfile


@dataclass
class BreachingCache:
    true_b64_image = ""
    true_user_data = None
    true_user_text = ""
    reconstructed_user_data = None
    reconstructed_user_text = ""
    stats = None
    attack_start_time_s = 0

    server_payload = None
    server = None
    user = None
    cfg = None
    setup = None


class BreachingAdapter:
    def __init__(self, worker_response_queue):
        self._worker_response_queue = worker_response_queue
        self.attack_cache = BreachingCache()

    def setup_text_attack(self, attack_params: AttackParameters = None, cfg=None):

        print(f"~~~[Attack Params]~~~ {attack_params}")

        device = (
            torch.device(f"cuda:0")
            if torch.cuda.is_available()
            else torch.device("cpu")
        )

        # Limit the GPU memory usage based on user budget
        if torch.cuda.is_available():
            print(f"limiting cuda process memory")
            torch.cuda.set_per_process_memory_fraction(
                attack_params.breaching_params.budget / 100
            )

        if cfg == None:
            cfg = breachinglib.get_config()

        extract_dir = "./dataset"

        # unzipped_directory = attack_params.zipFilePath.split('.')[0]
        print(os.listdir())
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        if attack_params.zipFilePath is not None:
            with zipfile.ZipFile(attack_params.zipFilePath, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
        elif attack_params.breaching_params.modality != "text":
            attack_params.breaching_params.datasetStructure = "test"
        torch.backends.cudnn.benchmark = cfg.case.impl.benchmark
        setup = dict(device=device, dtype=getattr(torch, cfg.case.impl.dtype))
        print(setup)

        logging.basicConfig(
            level=logging.INFO,
            handlers=[logging.StreamHandler(sys.stdout)],
            format="%(message)s",
        )
        logger = logging.getLogger()

        cfg = ConfigBuilder(attack_params).build()

        print(cfg)

        user, server, model, loss_fn = breachinglib.cases.construct_case(
            cfg.case, setup, prebuilt_model=None
        )

        if cfg.case.data.modality == "vision":
            model = self._getTorchModelFromSet(cfg.case.model, cfg.case.data.modality)

        if attack_params.ptFilePath is not None:
            model = self._buildUserModel(model, attack_params.ptFilePath)

        attacker = breachinglib.attacks.prepare_attack(
            server.model, server.loss, cfg.attack, setup
        )
        breachinglib.utils.overview(server, user, attacker)

        if not self._check_image_size(model, cfg.case.data.shape):
            raise ValueError("Mismatched dimensions")

        return cfg, setup, user, server, attacker, model, loss_fn

    def setup_image_attack(
        self, attack_params: AttackParameters = None, cfg=None, torch_model=None
    ):
        print(f"~~~[Attack Params]~~~ {attack_params}")

        device = (
            torch.device(f"cuda:0")
            if torch.cuda.is_available()
            else torch.device("cpu")
        )

        # Limit the GPU memory usage based on user budget
        if torch.cuda.is_available():
            print(f"limiting cuda process memory")
            torch.cuda.set_per_process_memory_fraction(
                attack_params.breaching_params.budget / 100
            )

        if cfg == None:
            cfg = breachinglib.get_config()

        extract_dir = "./dataset"

        # unzipped_directory = attack_params.zipFilePath.split('.')[0]
        print(os.listdir())
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        if attack_params.zipFilePath is not None:
            with zipfile.ZipFile(attack_params.zipFilePath, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
        elif attack_params.breaching_params.modality != "text":
            attack_params.breaching_params.datasetStructure = "test"
        torch.backends.cudnn.benchmark = cfg.case.impl.benchmark
        setup = dict(device=device, dtype=getattr(torch, cfg.case.impl.dtype))
        print(setup)

        logging.basicConfig(
            level=logging.INFO,
            handlers=[logging.StreamHandler(sys.stdout)],
            format="%(message)s",
        )
        logger = logging.getLogger()
        builder = ConfigBuilder(attack_params)
        cfg = builder.build(16)

        if torch_model is None:
            # modelset = (
            #     textModels
            #     if attack_params.breaching_params.modality == "text"
            #     else visionModels
            # )
            torch_model = self._getTorchModelFromSet(
                attack_params.model, attack_params.breaching_params.modality
            )
            torch_model = self._buildUserModel(torch_model, attack_params.ptFilePath)
        print(torch_model)

        permutation_arr = [
            None
        ]  # array[0] acting like a pointer to a permutation which is set in construct_dataloader

        # get permutation array
        _, _, model, _ = breachinglib.cases.construct_case(
            cfg.case, setup, prebuilt_model=torch_model, permutation_arr=permutation_arr
        )

        print(permutation_arr)

        return setup, model, permutation_arr, builder

    def perform_batches(
        self,
        builder: ConfigBuilder,
        setup,
        torch_model,
        request_token,
        reconstruction_frequency,
        permutation_arr,
    ):
        reconstructed_arr, true_arr, metrics_arr = [], [], []
        for user_idx in range(builder.get_max_clients()):
            cfg = builder.update_user_idx(user_idx)
            user, server, model, loss_fn = breachinglib.cases.construct_case(
                cfg.case,
                setup,
                prebuilt_model=torch_model,
                permutation_arr=permutation_arr,
            )
            attacker = breachinglib.attacks.prepare_attack(
                server.model, server.loss, cfg.attack, setup
            )

            print(f"CURRENT USER IDX{user.user_idx}")

            reconstructed_user_data, true_user_data, server_payload = (
                self.perform_attack(
                    cfg,
                    setup,
                    user,
                    server,
                    attacker,
                    model,
                    loss_fn,
                    request_token,
                    reconstruction_frequency,
                )
            )
            reconstructed_arr.append(reconstructed_user_data)
            true_arr.append(true_user_data)
            metrics_arr.append(self.attack_cache.stats)

            # user.plot(reconstructed_user_data, saveFile=f"reconstructed_data")
        return len(reconstructed_arr), metrics_arr, cfg

    def perform_attack(
        self,
        cfg,
        setup,
        user,
        server,
        attacker,
        model,
        loss_fn,
        request_token,
        reconstruction_frequency,
    ):
        server_payload = server.distribute_payload()
        shared_data, true_user_data = user.compute_local_updates(server_payload)

        self.attack_cache.server = server
        self.attack_cache.user = user
        self.attack_cache.cfg = cfg
        self.attack_cache.server_payload = server_payload
        self.attack_cache.setup = setup

        self.attack_cache.attack_start_time_s = time.time()

        response = request_token, self._worker_response_queue

        if cfg.case.data.modality == "vision":
            user.plot(true_user_data, saveFile=f"true_data_{user.user_idx}")

            with open(
                f"./attack_images/true_data_{user.user_idx}.png", "rb"
            ) as image_file:
                image_data_true = image_file.read()
            self.attack_cache.true_b64_image = base64.b64encode(image_data_true).decode(
                "utf-8"
            )
            self.attack_cache.true_user_data = true_user_data
        else:
            self.attack_cache.true_user_text = user.decode_text(true_user_data)
            user.print(true_user_data)

        print("reconstructing attack")
        reconstructed_user_data, stats = attacker.reconstruct(
            [server_payload],
            [shared_data],
            {},
            dryrun=cfg.dryrun,
            token=request_token,
            add_response_to_channel=partial(self._add_progress_to_channel, user),
            reconstruction_frequency=reconstruction_frequency,
        )

        if cfg.case.data.modality == "vision":
            user.plot(
                reconstructed_user_data, saveFile=f"reconstructed_data_{user.user_idx}"
            )
        else:
            self.attack_cache.reconstructed_user_text = user.decode_text(
                reconstructed_user_data
            )
            print(
                self.attack_cache.reconstructed_user_text,
                " ->>>>>>>>>>>>>>>>> is the reconstructed_user_text",
            )
            user.print(reconstructed_user_data, saveFile="./reconstructed_data.txt")

        return reconstructed_user_data, true_user_data, server_payload

    def get_text_metrics(
        self,
        reconstructed_user_data,
        true_user_data,
        server_payload,
        server,
        cfg,
        setup,
        response,
    ):
        metrics = breachinglib.analysis.report(
            reconstructed_user_data,
            true_user_data,
            [server_payload],
            server.model,
            order_batch=True,
            compute_full_iip=False,
            cfg_case=cfg.case,
            setup=setup,
            compute_lpips=False,
        )

        stats = AttackStatistics(
            MSE=metrics.get("mse", 0),
            SSIM=metrics.get("ssim", 0),
            PSNR=metrics.get("psnr", 0),
            GBLEU=metrics.get("google_bleu", 0),
            FMSE=metrics.get("feat_mse", 0),
            ACC=metrics.get("accuracy", 0),
        )
        token, channel = response

        base64_reconstructed = None
        text_reconstructed = None

        text_reconstructed = self.attack_cache.reconstructed_user_text
        print(text_reconstructed, cfg.case.data.modality)

        iterations = cfg.attack.optim.max_iterations
        restarts = cfg.attack.restarts.num_trials
        channel.put(
            token,
            AttackProgress(
                attack_type="tag",
                current_iteration=iterations,
                current_restart=restarts,
                max_iterations=iterations,
                max_restarts=restarts,
                statistics=stats,
                true_image=self.attack_cache.true_b64_image,
                true_text=self.attack_cache.true_user_text,
                reconstructed_image=base64_reconstructed,
                reconstructed_text=text_reconstructed,
                attack_start_time_s=self.attack_cache.attack_start_time_s,
            ),
        )
        return metrics

    def get_metrics(self, num_batches, metrics_arr, cfg, response):
        iterations = cfg.attack.optim.max_iterations
        restarts = cfg.attack.restarts.num_trials
        token, channel = response
        
        attack_dir = "./attack_images"
        
        for i in range(num_batches):
            file_path = os.path.join(attack_dir, f"reconstruction_metrics_{i}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(metrics_arr[i].json(indent=4))

        with tempfile.TemporaryDirectory() as temp_dir:
            # Path for the temporary zip file
            tempfile_path = os.path.join(temp_dir, "reconstruction.zip")

            with zipfile.ZipFile(tempfile_path, 'w') as zipf:
                for root, dirs, files in os.walk(attack_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), arcname=file)
                    
            with open(tempfile_path, "rb") as zip_file:
                reconstructed_images_archive = base64.b64encode(zip_file.read()).decode('utf-8')
            
        with open(
            f"./attack_images/reconstructed_data_0.png", "rb"
        ) as image_file:
            image_data_rec = image_file.read()
        sample_base64_reconstructed = base64.b64encode(image_data_rec).decode("utf-8")

        with open(f"./attack_images/true_data_0.png", "rb") as image_file:
            image_data_rec = image_file.read()
        sample_true_base64_reconstructed = base64.b64encode(image_data_rec).decode("utf-8")

        sample_metrics = metrics_arr[i]

        channel.put(
            token,
            AttackProgress(
                attack_type="invertinggradients",
                current_iteration=iterations,
                current_restart=restarts,
                max_iterations=iterations,
                max_restarts=restarts,
                statistics=sample_metrics,
                true_image=sample_true_base64_reconstructed,
                reconstructed_image=sample_base64_reconstructed,
                reconstructed_images_archive=reconstructed_images_archive,
                attack_start_time_s=self.attack_cache.attack_start_time_s,
            ),
        )

    def _check_image_size(self, model, shape):
        return True

    def _getTorchModelFromSet(self, model_name, modality):
        if modality == "vision" or modality == "images":
            model_name = model_name.replace("-", "").lower()
            if not hasattr(visionModels, model_name):
                print("no torch model found")
                raise TypeError("given model type did not match any of the options")
            model = getattr(visionModels, model_name)()
        elif modality == "text":
            config_name = model_name.replace("Model", "Config")
            if not (
                hasattr(textModels, model_name) and hasattr(textModels, config_name)
            ):
                print("hugging face model or config not found")
                raise TypeError("given model type did not match any of the options")
            config = getattr(textModels, config_name)()
            model = getattr(textModels, model_name)(config)

        return model

    def _buildUserModel(self, model, state_dict_path):
        if state_dict_path is not None:
            try:
                model.load_state_dict(torch.load(state_dict_path))
            except RuntimeError as r:
                print(
                    f"""Runtime error loading torch model from file:
        {r}
        Model is loaded from default values.
        """
                )
            except FileNotFoundError as f:
                print(
                    f"""Runtime error loading torch model from file:
        {f}
        Model is loaded from default values.
        """
                )
        model.eval()
        return model

    def _convert_candidate_to_base64(self, user, best_candidate):
        tmp = tempfile.NamedTemporaryFile()
        tmp_name = tmp.name
        tmp_img_name = f"{tmp_name}.png"
        print(tmp_name, tmp_img_name)
        user.plot(best_candidate, saveFile=tmp_name)
        with open(tmp_img_name, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    # Callback to be passed into submodule to add progress to the channel
    def _add_progress_to_channel(
        self, user, request_token: str, response_data: BreachingAttackProgress
    ):
        if self.attack_cache.cfg.case.data.modality == "vision":
            attack_type = "invertinggradients"
        elif self.attack_cache.cfg.case.data.modality == "text":
            attack_type = "tag"

        progress = AttackProgress(
            message_type="AttackProgress",
            attack_type=attack_type,
            current_iteration=response_data.current_iteration,
            max_iterations=response_data.max_iterations,
            current_restart=response_data.current_restart,
            max_restarts=response_data.max_restarts,
            current_batch=response_data.current_batch,
            max_batches=response_data.max_batches,
            attack_start_time_s=self.attack_cache.attack_start_time_s,
        )

        if (
            self.attack_cache.cfg.case.data.modality == "vision"
            and response_data.reconstructed_image
        ):
            self.attack_cache.reconstructed_b64_image = (
                self._convert_candidate_to_base64(
                    user, response_data.reconstructed_image
                )
            )

            metrics = breachinglib.analysis.report(
                response_data.reconstructed_image,
                self.attack_cache.true_user_data,
                server_payload=[self.attack_cache.server_payload],
                model_template=self.attack_cache.server.model,
                order_batch=True,
                compute_full_iip=False,
                cfg_case=self.attack_cache.cfg.case,
                setup=self.attack_cache.setup,
                compute_lpips=False,
            )
            self.attack_cache.stats = AttackStatistics(
                MSE=metrics.get("mse", 0),
                SSIM=metrics.get("ssim", 0),
                PSNR=metrics.get("psnr", 0),
            )

            progress.reconstructed_image = self.attack_cache.reconstructed_b64_image
            progress.true_image = self.attack_cache.true_b64_image
            progress.statistics = self.attack_cache.stats
        elif self.attack_cache.cfg.case.data.modality == "text":
            progress.true_text = self.attack_cache.true_user_text

        self._worker_response_queue.put(request_token, progress)
