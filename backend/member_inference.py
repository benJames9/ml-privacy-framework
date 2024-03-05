import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import norm
from backend.datasets import calculate_dataset_statistics
from abc import ABC, abstractmethod
import zipfile
from PIL import Image
import torch
from torchvision import models, transforms
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

class MembershipInferenceAttack(ABC):
    def __init__(self, target_model, target_point, N):
        self._target_model = target_model
        self._target_point = [Image.open(target_point[0]), target_point[1]]
        self._N = N
        self._in_models = []
        self._out_models = []
    
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
   
    def _infer_image_data(self, path_to_data):
        """
        Infer the image data from the target point.
        
        Parameters:
            path_to_data: The path to dataset.
        """
        statistics = calculate_dataset_statistics(path_to_data)
        self._image_stats = statistics
        
        # Normalise the target point
        transformer = self._transform()
        self._target_point[0] = transformer(self._target_point[0]).unsqueeze(0)
        
    def _load_data(self, path_to_data):
        """
        Load the data from the given path.
        
        Parameters:
            path_to_data: The path to dataset.
            
        Returns:
            data: PyTorch dataset.
        """
        # Extract the data from zip file
        extract_folder = 'temp_folder'
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
            
        # Load data into dataset
        return ImageFolder(root=extract_folder, transform=self._transform())

    def _transform(self):
        """
        Transformation to be applied to images to the format expected by the model.
        
        Returns:
            Transformation: Transformed to apply to image.
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
        
    def _train_shadow_models(self, data, n):
        """
        Train N shadow models on random samples from the data distribution D.
        
        Parameters:
            data: PyTorch dataset.
            n (int): The amount of data points to train each model on
            
        Returns:
            in_models (list): List of models trained on the target point.
            out_models (list): List of models not trained on the target point.
        """
        # Half of the models are trained on the target point, and half are not
        for i in range(self._N):
            sampled_data = np.random.choice(data, n, replace=True)
            if i < N // 2:
                sampled_data = np.append(sampled_data, self._target_point, axis=0)
                model = self._train_model(sampled_data)
                self._in_models.append(model)
            else:
                model = self._train_model(sampled_data)
                self._out_models.append(model)

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
        for i in range(self._N):
            in_confidence = self._model_confidence(self._in_models[i], self._target_point)
            out_confidence = self._model_confidence(self._out_models[i], self._target_point)
            in_confidences.append(in_confidence)
            out_confidences.append(out_confidence)
        
        # Fit Gaussians to the confidences
        in_gaussian = GaussianMixture(n_components=2)
        in_gaussian.fit(np.log(in_confidences).reshape(-1, 1))
        out_gaussian = GaussianMixture(n_components=2)
        out_gaussian.fit(np.log(out_confidences).reshape(-1, 1))
        
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
            logits = model(self._target_point[0])
        
        # Apply softmax to get probabilities
        probabilities = torch.softmax(logits, dim=1)
        
        # Get the predicted probability for the true label
        predicted_probability = probabilities[:, target_point[1]].item()
        
        # Apply logit transformation
        logit_scaled_confidence = torch.log(predicted_probability / (1 - predicted_probability)).item()
        
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
        
        # Calculate likelihoods of the target model under the two Gaussians
        in_likelihood = np.exp(in_gaussian.score_samples(np.log(target_model_confidence).reshape(1, -1)))
        out_likelihood = np.exp(out_gaussian.score_samples(np.log(target_model_confidence).reshape(1, -1)))
        
        # Return ratio of likelihoods
        return in_likelihood / out_likelihood
    
    # Carry out an attack given an initialised MembershipInferenceAttack object
    def run_inference(self, path_to_data, n, epochs, batch_size, lr):
        self._infer_image_data(path_to_data)
        data = self._load_data(path_to_data, n)
        self._train_shadow_models(data, n, epochs, batch_size, lr)
        in_gaussian, out_gaussian = self._fit_gaussians()
        target_model_confidence = self._model_confidence(self._target_model, self._target_point)
        return self._likelihood_ratio_test(target_model_confidence, in_gaussian, out_gaussian)
    
class Resnet18MIA(MembershipInferenceAttack):
    def _train_model(self, data, epochs, batch_size, lr):
        # Define the model
        model = models.resnet18(pretrained=False)
        model.fc = nn.Linear(model.fc.in_features, self._image_stats.num_classes)

        # Define loss function and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=lr)

        # Define data loader
        batch_size = batch_size
        data_loader = DataLoader(data, batch_size=batch_size, shuffle=True)

        # Train the model
        model.train()
        for epoch in range(epochs):
            running_loss = 0.0
            for images, labels in data_loader:
                optimizer.zero_grad()

                # Forward pass
                outputs = model(images)
                loss = criterion(outputs, labels)

                # Backward pass and optimization
                loss.backward()
                optimizer.step()

                running_loss += loss.item() * images.size(0)

            epoch_loss = running_loss / len(data)

        return model
        
if __name__ == '__main__':
    target_model = models.resnet18(pretrained=True)
    target_point = ['shark.jpg', 'n01440764']
    attack = Resnet18MIA(target_model, target_point, N=24)
    print(attack.run_inference('small_foldered_set.zip', n=100, epochs=10, batch_size=32, lr=0.001))

