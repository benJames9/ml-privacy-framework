import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import norm

class MembershipInferenceAttack:
    def __init__(self, target_model, target_point, N):
        self._target_model = target_model
        self._target_point = target_point
        self._N = N
        self._in_models = []
        self._out_models = []
    
    @abstractmethod
    def _train_model(data):
        """
        Train a shadow model on the given data.
        
        Parameters:
            data (numpy.ndarray): The dataset.
            
        Returns:
            model: Trained shadow model.
        """
       pass
   
    @abstractmethod
    def _transform(self, image):
        """
        Transform image to the format expected by the model.
        
        Parameters:
            image: Image to transform.
        
        Returns:
            image: Transformed image.
        """
        pass
        
    def _train_shadow_models(self, data, n):
        """
        Train N shadow models on random samples from the data distribution D.
        
        Parameters:
            data (numpy.ndarray): The dataset.
            n (int): The amount of data points to train each model on
            
        Returns:
            in_models (list): List of models trained on the target point.
            out_models (list): List of models not trained on the target point.
        """
        
        # Half of the models are trained on the target point, and half are not
        for i in range(self._N):
            sampled_data = np.random.choice(data, n, replace=True)
            if i < N // 2:
                sampled_data = np.append(sampled_data, [self._target_point], axis=0)
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
        
        # Load and preprocess the image
        image = Image.open(target_point[0])
        image = self._transform(image)
        
        # Reshape the image for model input
        image = image.unsqueeze(0)

        # Make prediction
        model.eval()
        with torch.no_grad():
            logits = model(image)
        
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
    def run_inference(self, data, n):
        self._train_shadow_models(data, n)
        in_gaussian, out_gaussian = self._fit_gaussians()
        target_model_confidence = self._model_confidence(self._target_model, self._target_point)
        return self._likelihood_ratio_test(target_model_confidence, in_gaussian, out_gaussian)
    
    class Resnet18MIA (MembershipInferenceAttack):
        def _train_model(self, data):
            # Train a ResNet18 model on the given data
            pass
        
        def _transform(self, image):
            # Transform image to the format expected by the model
            pass

