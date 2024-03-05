import torch
from common import AttackParameters, AttackProgress, AttackStatistics, WorkerQueue
from breaching.breaching.attacks.attack_progress import AttackProgress as BreachingAttackProgress
import breaching.breaching as breachinglib
from torchvision import models as visionModels
import logging, sys
from threading import Thread
import base64
import zipfile
import os, shutil
import asyncio
import random
from ConfigBuilder import ConfigBuilder
from breaching.breaching.cases.models.model_preparation import VisionContainer

class BreachingAdapter:
    def __init__(self, worker_response_queue):
        self._worker_response_queue = worker_response_queue


    def setup_attack(self, attack_params:AttackParameters=None, cfg=None):

        print(f'~~~[Attack Params]~~~ {attack_params}')

        device = torch.device(f'cuda:0') if torch.cuda.is_available() else torch.device('cpu')
        
        # Limit the GPU memory usage based on user budget
        if torch.cuda.is_available():
            print(f'limiting cuda process memory')
            torch.cuda.set_per_process_memory_fraction(attack_params.budget / 100)

        

        extract_dir = "./dataset"
        
        num_classes = 0
        dataset_size = 0

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

        if cfg == None:
            cfg = breachinglib.get_config()
            
        cfg = ConfigBuilder(attack_params).build(num_dirs, num_files)
        torch.backends.cudnn.benchmark = cfg.case.impl.benchmark
        setup = dict(device=device, dtype=getattr(torch, cfg.case.impl.dtype))
        if cfg.case.model == "ResNet-18":
            cfg.case.model = cfg.case.model.replace('-', '')

        model = self._getTorchVisionModel(cfg.case.model)
        user, server, model, loss_fn = breachinglib.cases.construct_case(cfg.case, setup, premade_model=model)
        print(os.listdir())
        if attack_params.ptFilePath is not None:
            model = self._buildUserModel(model, attack_params.ptFilePath)
        
        logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)], format='%(message)s')
        logger = logging.getLogger()

        print(cfg)

        attacker = breachinglib.attacks.prepare_attack(server.model, server.loss, cfg.attack, setup)
        breachinglib.utils.overview(server, user, attacker)

        if not self._check_image_size(model, cfg.case.data.shape):
            raise ValueError("Mismatched dimensions")

        return cfg, setup, user, server, attacker, model, loss_fn

    def perform_attack(self, cfg, setup, user, server, attacker, model, loss_fn, request_token):
        print("performing")
        server_payload = server.distribute_payload()
        shared_data, true_user_data = user.compute_local_updates(server_payload)
        print("local updates")
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
    
    def _getTorchVisionModel(self, model_name):
        model_name = model_name.replace('-', '').lower()
        print("visioning")
        if not hasattr(visionModels, model_name):
            print("no torch model found")
            raise TypeError("given model type did not match any of the options")
        model = VisionContainer(getattr(visionModels, model_name)())
        model.name = model_name
        return model
        

    def _buildUserModel(self, model, state_dict_path):
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
