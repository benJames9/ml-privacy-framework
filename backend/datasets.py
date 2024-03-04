import os
import zipfile
import numpy as np
from PIL import Image

class DatasetStatistics:
    def __init__(self, image_shape, mean, std, num_images, num_classes):
        self.image_shape = image_shape
        self.mean = mean
        self.std = std
        self.num_images = num_images
        self.num_classes = num_classes

# Calculate information of a given dataset
def calculate_dataset_statistics(zip_file_path):
    # Extract the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall('temp_dataset')

    # Get the list of class folders
    class_folders = [f for f in os.listdir('temp_dataset') if os.path.isdir(os.path.join('temp_dataset', f))]
    num_classes = len(class_folders)

    # Assuming RGB images
    num_images = 0
    sum_mean = np.zeros(3)
    sum_std = np.zeros(3)
    image_shape = None

    # Calculate statistics for each class
    for class_folder in class_folders:
        class_path = os.path.join('temp_dataset', class_folder)
        class_images = [f for f in os.listdir(class_path) if f.endswith('.jpg') or f.endswith('.png')]

        num_images += len(class_images)

        for image_file in class_images:
            image_path = os.path.join(class_path, image_file)
            image = np.array(Image.open(image_path))

            if image_shape is None:
                image_shape = image.shape

            # Add pixel values for mean calculation
            sum_mean += np.mean(image, axis=(0, 1))

            # Add pixel values for std calculation
            sum_std += np.std(image, axis=(0, 1))

    # Calculate mean and std
    mean = sum_mean / num_images
    std = sum_std / num_images

    # Clean up temporary directory
    os.system('rm -rf temp_dataset')

    return DatasetStatistics(image_shape, mean, std, num_images, num_classes)