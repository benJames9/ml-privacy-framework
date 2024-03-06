import unittest
import os
import shutil
from backend.mia.datasets import calculate_dataset_statistics, DatasetStatistics
import numpy as np

# Test the calculate_dataset_statistics function
class TestDatasetStatistics(unittest.TestCase):
    def test_small_foldered_set(self):
        zip_file_path = 'small_foldered_set.zip'
        statistics = calculate_dataset_statistics(zip_file_path)
        
        # Verify that the statistics are calculated correctly
        self.assertIsInstance(statistics, DatasetStatistics)
        self.assertEqual(statistics.num_images, 350)
        self.assertEqual(statistics.num_classes, 7)
        self.assertTrue(np.allclose(statistics.mean, [0.30655779, 0.43363997, 0.4549895]))
        self.assertTrue(np.allclose(statistics.std, [0.18246345, 0.19011785, 0.18673244]))
        self.assertTrue(np.allclose(statistics.image_shape, [375, 500, 3]))
        
if __name__ == '__main__':
    unittest.main()