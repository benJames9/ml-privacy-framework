from torchvision import models
import torch
import csv

from .mia.member_inference import MembershipInferenceAttack, Resnet18MIA
from .common import AttackParameters, MiaParams

def perform_attack(attack_parameters: AttackParameters): 
    # Get MIA parameters
    mia_params = attack_parameters.mia_params
    if mia_params is None:
        raise ValueError("MIA parameters not provided")
    
    # Create dict of label names to label ids
    label_dict = {}
    with open(mia_params.path_to_label_csv, newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            label_name, label_id = row
            label_dict[label_name.strip()] = int(label_id.strip())

    # Get the target label
    model = get_model(attack_parameters.model, attack_parameters.ptFilePath)
    
    # Define target point and initialise attack
    target_point = (mia_params.target_image_path, mia_params.target_label)
    attack = Resnet18MIA(model, target_point, mia_params.N, label_dict)

    # Perform the attack
    ratio = attack.run_inference(attack_parameters.zipFilePath, mia_params.data_points, 
                                 mia_params.epochs, mia_params.batch_size, mia_params.lr)
    
    print(f'ratio: {ratio}')

def get_model(model_type, path_to_pt):
    match model_type:
        case 'resnet18':
            model = models.resnet18(pretrained=False)
        case other: 
            raise ValueError("Model type not supported")
        
    # Load the state dict from path
    pt = torch.load(path_to_pt)
    model.load_state_dict(pt)
    model.eval()

    return model
    
if __name__ == '__main__':
    perform_attack(AttackParameters(
        model='resnet18',
        attack='mia',
        modality='images',
        datasetStructure='foldered',
        csvPath='path_to_csv',
        batchSize=32,
        numRestarts=5,
        stepSize=0.1,
        maxIterations=1000,
        ptFilePath='examples/resnet18_pretrained.pt',
        zipFilePath='examples/small_foldered_set.zip',
        budget=100,
        reconstruction_frequency=100,
        mia_params=MiaParams(
            N=4,
            data_points=3,
            epochs=3,
            batch_size=32,
            lr=0.01,
            target_label='shark',
            target_image_path='examples/shark.JPEG',
            path_to_label_csv='examples/labels.csv'
        )
    ))