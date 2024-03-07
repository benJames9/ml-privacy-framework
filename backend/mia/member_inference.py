import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import norm
from abc import ABC, abstractmethod
import zipfile
from PIL import Image
import torch
from torchvision import models, transforms
from torchvision.datasets import ImageFolder
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
import torch.nn.functional as F
import os
import math

from .datasets import calculate_dataset_statistics

class MembershipInferenceAttack(ABC):
    def __init__(self, target_model, target_point, N, class_dict):
        # Check if N is even or >= 4
        if N % 2 != 0 or N < 4:
            raise ValueError("Number of shadow models must be even and larger than 4")
        
        # Initialise values
        self._target_model = target_model
        self._target_image = Image.open(target_point[0])
        self._target_label = target_point[1]
        self._N = N
        self._in_models = []
        self._out_models = []
        
        # Set the target label value from the class dictionary
        self._load_classes(class_dict)
    
    @abstractmethod
    def _train_model(self, data):
        """
        Train a shadow model on the given data.
        
        Parameters:
            data: PyTorch dataset.
            
        Returns:
            model: Trained shadow model.
        """
        pass
    
    def _load_classes(self, class_dict):
        """
        Sets the target label value from the class dictionary.

        Parameters:
            class_dict (dict): Dictionary of class names to class indices.

        """
        if self._target_label not in class_dict:
            raise ValueError("Target label not in target model classes")
        
        self._target_label_val = class_dict[self._target_label]
   
    def _infer_image_data(self, path_to_data):
        """
        Infer the image data from the target point.
        
        Parameters:
            path_to_data: The path to dataset.
        """
        statistics = calculate_dataset_statistics(path_to_data)
        self._image_stats = statistics
        
        if statistics.num_classes != self._target_model.fc.out_features:
            raise ValueError("Number of classes in the dataset does not match target model")
        
        # Normalise the target image
        transformer = self._transform()
        
        # Define the target point for training
        self._target_point = (transformer(self._target_image), self._target_label_val)
        print(f'target point: {self._target_point}')
        
    def _load_data(self, path_to_data, extract_folder):
        """
        Load the data from the given path.
        
        Parameters:
            path_to_data: The path to dataset.
            extract_folder: The folder to extract the data to.
            
        Returns:
            data: PyTorch dataset.
        """
        # Extract the data from zip file
        with zipfile.ZipFile(path_to_data, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
            
        # Load data into dataset
        return ImageFolder(root=extract_folder, transform=self._transform())

    def _transform(self):
        """
        Transformation to be applied to images to the format expected by the model.
        
        Returns:
            Transformation: Transform to apply to image.
        """
        if self._image_stats is None:
            raise ValueError("Image statistics not set")
        
        stats = self._image_stats
        
        # Define the transformations
        return transforms.Compose([
            transforms.Resize((self._image_stats.image_shape[0], self._image_stats.image_shape[1])),
            transforms.ToTensor(),
            transforms.Normalize(mean=self._image_stats.mean, std=self._image_stats.std)
        ])
        
    def _train_shadow_models(self, data, n, epochs, batch_size, lr, request_token, progress_callback):
        """
        Train N shadow models on random samples from the data distribution D. 
        Saved as class property. 
        
        Parameters:
            data: PyTorch dataset.
            n (int): The amount of data points to train each model on.
            epochs (int): The number of epochs to train each model for.
            batch_size (int): The batch size to use for training.
            lr (float): The learning rate to use for training.
            request_token: The token to use for progress updates.
            progress_callback: The callback to use for progress updates.
            
        """
        # Check n is valid input
        if n > len(data):
            raise ValueError("Shadow model training points larger than dataset")
                
        # Half of the models are trained on the target point, and half are not
        for i in range(self._N):
            num_samples = len(data)
            sampled_indices = np.random.choice(num_samples, n, replace=True)
            sampled_data = Subset(data, sampled_indices)         

            if i % 2 == 0:
                sampled_data = torch.utils.data.ConcatDataset([sampled_data, [self._target_point]])
                model = self._train_model(sampled_data, epochs, batch_size, lr, current_model=i, 
                                          request_token=request_token, progress_callback=progress_callback)
                self._in_models.append(model)
            else:
                model = self._train_model(sampled_data, epochs, batch_size, lr, current_model=i, 
                                          request_token=request_token, progress_callback=progress_callback)
                self._out_models.append(model)
            print(f'model {i} trained\n')

    def _fit_gaussians(self):
        """
        Fit two Gaussians to the confidences of the models on the target point.
            
        Returns:
            in_gaussian (GaussianMixture): Gaussian fitted to IN models.
            out_gaussian (GaussianMixture): Gaussian fitted to OUT models.
        """
        in_confidences = []
        out_confidences = []
        
        # Generate list of confidences for the target point
        for i in range(self._N // 2):
            print('calculating in confidence...')
            in_confidence = self._model_confidence(self._in_models[i], self._target_point)
            print('calculating out confidence...') 
            out_confidence = self._model_confidence(self._out_models[i], self._target_point)
            in_confidences.append(in_confidence)
            out_confidences.append(out_confidence)
            
        print(f'in confs: {in_confidences}')
        print(f'out confs: {out_confidences}')
        
        # Fit Gaussians to the confidences
        in_gaussian = GaussianMixture(n_components=2)
        in_gaussian.fit(np.asarray(in_confidences).reshape(-1, 1))
        out_gaussian = GaussianMixture(n_components=2)
        out_gaussian.fit(np.asarray(out_confidences).reshape(-1, 1))
        
        return in_gaussian, out_gaussian

    def _model_confidence(self, model, target_point):
        """
        Query the confidence of the model on the target point.
        
        Parameters:
            model: The model to query.
            target_point: The point to query the model on.
            
        Returns:
            confidence: Confidence of the model on the target point.
        """

        # Make prediction
        model.eval()
        with torch.no_grad():
            logits = model(self._target_point[0].unsqueeze(0))
            
        print(f'logits: {logits}')
            
        # One hot encode the target label
        target_index = self._target_point[1]
        target_label = torch.zeros(self._image_stats.num_classes)
        target_label[target_index] = 1
        
        # Reshape target for calculating CE
        target_label = target_label.view(1, -1)

        print(f'one hot: {target_label}')
            
        criterion = nn.CrossEntropyLoss()
        loss = criterion(logits, target_label)
        
        print(f'loss: {loss}')
        
        confidence = math.exp(-loss)
        
        print(f'confidence: {confidence}')
        
        # Convert 0s and 1s from rounding errors
        confidence = self._add_epsilon(confidence)
        
        print(f'confidence after conversion: {confidence}')
        
        # Apply logit transformation
        logit_scaled_confidence = math.log(confidence / (1 - confidence))
        
        print(f'logit scaled conf: {logit_scaled_confidence}')
        
        return logit_scaled_confidence

    def _likelihood_ratio_test(self, target_model_confidence, in_gaussian, out_gaussian):
        """
        Perform a parametric likelihood-ratio test.
        
        Parameters:
            target_model_confidence: Confidence of the target model on the target point.
            in_gaussian (GaussianMixture): Gaussian fitted to IN models.
            out_gaussian (GaussianMixture): Gaussian fitted to OUT models.
            
        Returns:
            result: Result of the likelihood-ratio test.
        """
        
        # Reshape logit scaled confidence
        target_conf = np.asarray([target_model_confidence]).reshape(1, -1)
        
        # Calculate likelihoods of the target model under the two Gaussians
        in_likelihood = np.exp(in_gaussian.score_samples(target_conf)).item()
        in_likelihood = self._add_epsilon(in_likelihood)
        print(f'in likelihood: {in_likelihood}')
        out_likelihood = np.exp(out_gaussian.score_samples(target_conf)).item()
        out_likelihood = self._add_epsilon(out_likelihood)
        print(f'out likelihood: {out_likelihood}')
        
        # Return ratio of likelihoods
        return in_likelihood / out_likelihood
    
    # For values bounded by [0, 1], prevent values of 1 and 0
    def _add_epsilon(self, value):
        epsilon = 1e-6
        if value < epsilon:
            return epsilon
        elif 1 - value < epsilon:
            return 1 - epsilon
        
        return value
    
    # Carry out an attack given an initialised MembershipInferenceAttack object
    def run_inference(self, path_to_data, n, epochs, batch_size, lr, request_token, progress_callback):
        self._max_epochs = n * self._N
        self._infer_image_data(path_to_data)
        
        # Load data to pytorch image folder
        extract_folder = 'temp_folder'
        data = self._load_data(path_to_data, extract_folder)
        self._train_shadow_models(data, n, epochs, batch_size, lr, request_token, progress_callback)
        os.system(f'rm -rf {extract_folder}')
        
        # Fit Gaussians for shadow and target models
        in_gaussian, out_gaussian = self._fit_gaussians()
        target_model_confidence = self._model_confidence(self._target_model, self._target_point)
        
        # Perform likelihood ratio test
        ratio = self._likelihood_ratio_test(target_model_confidence, in_gaussian, out_gaussian)
        
        # Update final progress
        progress_callback(request_token, self._max_epochs, self._max_epochs, ratio)
        return ratio
    
class Resnet18MIA(MembershipInferenceAttack):
    def _train_model(self, data, epochs, batch_size, lr, current_model, request_token, progress_callback):
        # Define the model
        model = models.resnet18(pretrained=False)
        model.fc = nn.Linear(model.fc.in_features, self._image_stats.num_classes)

        # Define loss function and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=lr)

        # Define data loader
        batch_size = batch_size
        data_loader = DataLoader(data, batch_size=batch_size, shuffle=True)
        
        print('training new model...')

        # Train the model
        model.train()
        for epoch in range(epochs):
            print(f'epoch {epoch}')
            running_loss = 0.0
            for images, labels in data_loader:
                optimizer.zero_grad()

                # Forward pass
                outputs = model(images)
                loss = criterion(outputs, labels)

                # Backward pass and optimization
                loss.backward()
                optimizer.step()
                
                progress_callback(request_token, self._max_epochs, current_model * epochs + epoch)

        print('model trained')
        return model
        
if __name__ == '__main__':
    class_dict = {'n01440764': 0, 'n01443537': 1, 'n01484850': 2, 'n01491361': 3, 'n01494475': 4, 'n01496331': 5, 'n01498041': 6}
    target_model = models.resnet18(pretrained=True)
    target_point = ('shark.JPEG', 'n01440764')
    attack = Resnet18MIA(target_model, target_point, N=4, class_dict=class_dict)
    print(attack.run_inference('small_foldered_set.zip', n=10, epochs=2, batch_size=10, lr=0.001))