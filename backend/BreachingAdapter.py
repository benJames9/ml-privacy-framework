import torch
from common import AttackParameters, AttackProgress, AttackStatistics, WorkerQueue
from breaching.breaching.attacks.attack_progress import AttackProgress as BreachingAttackProgress
import breaching.breaching as breachinglib
from torchvision import models
import logging, sys
from threading import Thread
import base64
import zipfile
import os, shutil
import asyncio

class BreachingAdapter:
    def __init__(self, worker_response_queue):
        self._worker_response_queue = worker_response_queue

    def _construct_cfg(self, attack_params: AttackParameters, datasetSize: int, numClasses: int, dataset_path=None):
        match attack_params.modality:
            case "images":
                cfg = self._construct_images_cfg(attack_params)
            case "text":
                cfg = self._construct_text_cfg(attack_params)
            case _:
                raise TypeError(f"Data type of attack: {attack_params.modality} does not match anything.")

        assert(attack_params is not None)

        #setup all customisable parameters
        cfg.case.model = attack_params.model

        cfg.case.data.size = datasetSize
        cfg.case.data.classes = numClasses
        match attack_params.datasetStructure:
            case "CSV":
                cfg.case.data.name = "CustomCsv"
            case "Foldered":
                cfg.case.data.name = "CustomFolders"
            case _:
                print("Could not match dataset structure")
                match attack_params.modality:
                    case "images":
                        cfg.case.data = breachinglib.get_config(overrides=["case/data=CIFAR10"]).case.data
                        print("defaulted to CIFAR10")
                    case "text":
                        cfg.case.data = breachinglib.get_config(overrides=["case/data=wikitext"]).case.data
                        print("defaulted to wikitext")
                    case _:
                        raise TypeError(f"Data type of attack: {attack_params.modality} does not match anything.")

        match dataset_path:
            case None:
                cfg.case.data.path = 'dataset'
            case _:
                cfg.case.data.path = dataset_path

        if any(attack_params.means) and any(attack_params.stds):
            cfg.case.data.mean = attack_params.means
            cfg.case.data.std = attack_params.stds
            cfg.case.data.normalize = False
        
        cfg.case.data.batch_size = attack_params.batchSize
        cfg.attack.optim.step_size = attack_params.stepSize
        cfg.attack.optim.max_iterations = attack_params.maxIterations
        cfg.attack.optim.callback = 1
        cfg.case.user.user_idx = attack_params.user_idx
        cfg.case.data.default_clients = attack_params.number_of_clients
        cfg.attack.restarts.num_trials = attack_params.numRestarts

        return cfg

    def _construct_text_cfg(self, attack_params: AttackParameters):
        match attack_params.attack:
            case 'TAG':
                cfg = breachinglib.get_config(overrides=["attack=tag"])
            case _:
                raise TypeError(f'No text attack match; {attack_params.attack}')

        match attack_params.model:
            case "bert":
                cfg.case.model="bert-base-uncased"
            case "gpt2":
                cfg.case.model="gpt2"
            case "transformer3":
                cfg.case.model="transformer3"
            case _:
                try:
                    assert(attack_params.model in {
                        # ... list of all supported models
                    })
                    cfg.case.model=attack_params.model
                except AssertionError as a:
                    raise TypeError(f"no model match for text: {attack_params.model}")

        match attack_params.tokenizer:
            case "bert":
                cfg.case.data.tokenizer="bert-base-uncased"
                cfg.case.data.task= "masked-lm"
                cfg.case.data.vocab_size= 30522
                cfg.case.data.mlm_probability= 0.15
            case "gpt2":
                cfg.case.model="gpt2"
                cfg.case.data.task= "causal-lm"
                cfg.case.data.vocab_size= 50257
            case "transformer3":
                cfg.case.model="transformer3"
            case _:
                raise TypeError(f"no model match for tokenizer: {attack_params.model}")


        cfg.case.data.shape = attack_params.shape



    def _construct_images_cfg(self, attack_params: AttackParameters):
        match attack_params.attack:
            case 'invertinggradients':
                cfg = breachinglib.get_config()
                cfg.case.data.partition="unique-class"
                # default case.model=ResNet18
            case 'modern':
                cfg = breachinglib.get_config(overrides=["attack=modern"])
                cfg.case.data.partition="unique-class"
                cfg.attack.regularization.deep_inversion.scale=1e-4
            case 'fishing_for_user_data':
                cfg = breachinglib.get_config(overrides=["case/server=malicious-fishing", "attack=clsattack", "case/user=multiuser_aggregate"])
                cfg.case.user.user_range = [0, 1]
                cfg.case.data.partition = "random" # This is the average case
                cfg.case.user.num_data_points = 256
                cfg.case.data.default_clients = 32
                cfg.case.user.provide_labels = True # Mostly out of convenience
                cfg.case.server.target_cls_idx = 0 # Which class to attack?
            # Less important attacks
            case 'analytic':
                cfg = breachinglib.get_config(overrides=["attack=analytic", "case.model=linear"])
                cfg.case.data.partition="balanced"
                cfg.case.data.default_clients = 50
                cfg.case.user.num_data_points = 256 # User batch size
            case 'rgap':
                cfg = breachinglib.get_config(overrides=["attack=rgap", "case.model=cnn6", "case.user.provide_labels=True"])
                cfg.case.user.num_data_points = 1
            case 'april_analytic':
                cfg = breachinglib.get_config(overrides=["attack=april_analytic", "case.model=vit_small_april"])
                cfg.case.data.partition="unique-class"
                cfg.case.user.num_data_points = 1
                cfg.case.server.pretrained = True
                cfg.case.user.provide_labels = False
            case 'deepleakage':
                cfg = breachinglib.get_config(overrides=["attack=deepleakage", "case.model=ConvNet"])
                cfg.case.data.partition="unique-class"
                cfg.case.user.provide_labels=False

        return cfg

    def setup_attack(self, attack_params:AttackParameters=None, cfg=None, torch_model=None):

        print(f'~~~[Attack Params]~~~ {attack_params}')

        device = torch.device(f'cuda:0') if torch.cuda.is_available() else torch.device('cpu')
        
        # Limit the GPU memory usage based on user budget
        if torch.cuda.is_available():
            print(f'limiting cuda process memory')
            torch.cuda.set_per_process_memory_fraction(attack_params.budget / 100)

        if cfg == None:
            cfg = breachinglib.get_config()

        if torch_model is None:
            torch_model = self._buildUploadedModel(attack_params.model, attack_params.ptFilePath)
            
        extract_dir = "./dataset"

        # unzipped_directory = attack_params.zipFilePath.split('.')[0]
        print(os.listdir())
        if (os.path.exists(extract_dir)):
            shutil.rmtree(extract_dir)
        with zipfile.ZipFile(attack_params.zipFilePath, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        num_files = 0
        _, dirs, _ = next(os.walk("./dataset"))
        num_dirs = len(dirs)
        for _, dirs, files in os.walk(extract_dir):
            num_files += len(files)

        torch.backends.cudnn.benchmark = cfg.case.impl.benchmark
        setup = dict(device=device, dtype=getattr(torch, cfg.case.impl.dtype))
        print(setup)

        logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)], format='%(message)s')
        logger = logging.getLogger()

        cfg = self._construct_cfg(attack_params, num_files, num_dirs)

        print(cfg)

        user, server, model, loss_fn = breachinglib.cases.construct_case(cfg.case, setup, prebuilt_model=torch_model)
        attacker = breachinglib.attacks.prepare_attack(server.model, server.loss, cfg.attack, setup)
        breachinglib.utils.overview(server, user, attacker)


        if torch_model is not None:
            model = torch_model

        if not self._check_image_size(model, cfg.case.data.shape):
            raise ValueError("Mismatched dimensions")

        return cfg, setup, user, server, attacker, model, loss_fn

    def perform_attack(self, cfg, setup, user, server, attacker, model, loss_fn, request_token):
        server_payload = server.distribute_payload()
        shared_data, true_user_data = user.compute_local_updates(server_payload)
        breachinglib.utils.overview(server, user, attacker)

        response = request_token, self._worker_response_queue
        user.plot(true_user_data, saveFile="true_data")
        print("reconstructing attack")
        reconstructed_user_data, stats = attacker.reconstruct([server_payload], [shared_data], {},
                                                              dryrun=cfg.dryrun, token=request_token,
                                                              add_response_to_channel=self._add_progress_to_channel)
        user.plot(reconstructed_user_data, saveFile="reconstructed_data")
        return reconstructed_user_data, true_user_data, server_payload

    def get_metrics(self, reconstructed_user_data, true_user_data, server_payload, server, cfg, setup, response):
        metrics = breachinglib.analysis.report(reconstructed_user_data, true_user_data, [server_payload],
                                        server.model, order_batch=True, compute_full_iip=False,
                                        cfg_case=cfg.case, setup=setup, compute_lpips=False)
        print(metrics)
        # stats = AttackStatistics(MSE=0, SSIM=0, PSNR=0)
        stats = AttackStatistics(MSE=metrics.get('mse', 0), SSIM=0, PSNR=metrics.get('psnr', 0))
        token, channel = response

        with open("./reconstructed_data.png", 'rb') as image_file:
            image_data_rec = image_file.read()
        base64_reconstructed = base64.b64encode(image_data_rec).decode('utf-8')

        with open("./true_data.png", 'rb') as image_file:
            image_data_true = image_file.read()
        base64_true = base64.b64encode(image_data_true).decode('utf-8')

        iterations = cfg.attack.optim.max_iterations
        restarts = cfg.attack.restarts.num_trials
        channel.put(token, AttackProgress(current_iteration=iterations,
                                        current_restart=restarts,
                                        max_iterations=iterations,
                                        max_restarts=restarts,
                                        statistics=stats,
                                        true_image=base64_true,
                                        reconstructed_image=base64_reconstructed))
        return metrics

    def _check_image_size(self, model, shape):
        return True

    def _buildUploadedModel(self, model_type, state_dict_path):
        model = None
        model_type = model_type.replace('-', '').lower()

        if not hasattr(models, model_type):
            raise TypeError("given model type did not match any of the options")
        model = getattr(models, model_type)()

        if state_dict_path is not None:
            try:
                model.load_state_dict(torch.load(state_dict_path))
            except RuntimeError as r:
                print(f'''Runtime error loading torch model from file:
        {r}
        Model is loaded from default values.
        ''')
            except FileNotFoundError as f:
                print(f'''Runtime error loading torch model from file:
        {f}
        Model is loaded from default values.
        ''')
        model.eval()
        return model

    async def _forward_response_from_breaching(self):
        print("waiting for response from breaching")
        while True:
            request_token, response_data = await asyncio.to_thread(self._breaching_response_queue.get())
            if request_token is None:
                break

            print("forwarding response for " + request_token)

            progress = AttackProgress(
                message_type="AttackProgress",
                current_iteration=response_data.iteration,
                max_iterations=response_data.max_iterations,
                current_restart=response_data.restart,
                max_restarts=response_data.max_restarts,
                current_batch=response_data.batch,
                max_batches=response_data.max_batches
            )

            self._worker_response_queue.put(request_token, progress)

    # Callback to be passed into submodule to add progress to the channel
    def _add_progress_to_channel(self, request_token: str, response_data: BreachingAttackProgress):
        progress = AttackProgress(
                message_type="AttackProgress",
                current_iteration=response_data.current_iteration,
                max_iterations=response_data.max_iterations,
                current_restart=response_data.current_restart,
                max_restarts=response_data.max_restarts,
                current_batch=response_data.current_batch,
                max_batches=response_data.max_batches
        )

        self._worker_response_queue.put(request_token, progress)
