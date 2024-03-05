import unittest
import os
import shutil
from backend.datasets import calculate_dataset_statistics, DatasetStatistics

# Test the calculate_dataset_statistics function
class TestDatasetStatistics(unittest.TestCase):
    def test_small_foldered_set(self):
        zip_file_path = 'small_foldered_set.zip'
        statistics = calculate_dataset_statistics(zip_file_path)
        
        # Verify that the statistics are calculated correctly
        self.assertIsInstance(statistics, DatasetStatistics)
        self.assertEqual(statistics.num_images, 350)
        self.assertEqual(statistics.num_classes, 7)
        self.assertEqual(statistics.mean, [0.46, 0.56, 0.57])
        self.assertEqual(statistics.std, [0.32, 0.28, 0.27])
        
if __name__ == '__main__':
    unittest.main()
        
        
        