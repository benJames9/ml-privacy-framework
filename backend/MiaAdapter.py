from torchvision import models
import torch
import csv

from mia.member_inference import Resnet18MIA
from common import (
    AttackParameters,
    MiaParams,
    MiaStatistics,
    WorkerCommunication,
    AttackProgress,
)


class MiaAdapter:
    def __init__(self, worker_response_queue):
        self._worker_response_queue = worker_response_queue

    def perform_attack(self, attack_parameters: AttackParameters, request_token):
        # Get MIA parameters
        mia_params = attack_parameters.mia_params
        if mia_params is None:
            raise ValueError("MIA parameters not provided")

        # Create dict of label names to label ids
        label_dict = {}
        num_classes = 0
        with open(mia_params.path_to_label_csv, newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                num_classes += 1
                label_name, label_id = row
                label_dict[label_name.strip()] = int(label_id.strip())

        # Get the target label
        model = self._get_model(
            attack_parameters.model, attack_parameters.ptFilePath, num_classes
        )

        # Define target point and initialise attack
        target_point = (mia_params.target_image_path, mia_params.target_label)
        attack = Resnet18MIA(model, target_point, mia_params.N, label_dict)
        
        print("Running inference")

        # Perform the attack
        ratio = attack.run_inference(
            attack_parameters.zipFilePath,
            mia_params.data_points,
            mia_params.epochs,
            mia_params.batch_size,
            mia_params.lr,
            request_token,
            self._add_progress_to_channel,
        )

        print(f"ratio: {ratio}")

    def _get_model(self, model_type, path_to_pt, num_classes):
        if model_type == "ResNet-18":
            model = models.resnet18(pretrained=False)
            model.fc = torch.nn.Linear(in_features=512, out_features=num_classes)
        else:
            raise ValueError("Model type not supported")

        # Load the state dict from path
        pt = torch.load(path_to_pt)
        model.load_state_dict(pt)
        model.eval()

        return model

    def _add_progress_to_channel(
        self, request_token, max_epochs, current_epoch, start_time, result=None
    ):
        # Construct progress type to update user
        progress = AttackProgress(
            message_type="AttackProgress",
            attack_type="mia",
            current_iteration=current_epoch,
            max_iterations=max_epochs,
            attack_start_time_s=start_time,
        )

        # Add final result
        if result is not None:
            mia_stats = MiaStatistics(likelihood_ratio=result)
            progress.mia_stats = mia_stats

        self._worker_response_queue.put(request_token, progress)


if __name__ == "__main__":
    worker_communication = WorkerCommunication()
    mia = MiaAdapter(worker_communication.response_channel)
    request_token = "hi"

    mia.perform_attack(
        AttackParameters(
            model="resnet18",
            attack="mia",
            modality="images",
            datasetStructure="foldered",
            csvPath="path_to_csv",
            batchSize=32,
            numRestarts=5,
            stepSize=0.1,
            maxIterations=1000,
            ptFilePath="examples/resnet18_model_mia.pt",
            zipFilePath="examples/small_foldered_set.zip",
            budget=100,
            reconstruction_frequency=10,
            mia_params=MiaParams(
                N=4,
                data_points=6,
                epochs=5,
                batch_size=3,
                lr=0.1,
                target_label="shark",
                target_image_path="examples/shark.JPEG",
                path_to_label_csv="examples/labels.csv",
            ),
        ),
        request_token,
    )
