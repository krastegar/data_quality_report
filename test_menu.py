import os
import unittest
from unittest import mock
from menu import Menu

class TestGetInput(unittest.TestCase):

    def setUp(self):
        self.menu = Menu()


    def test_get_input_valid_path(self):
        
        # create a temporary directory and file for testing
        temp_dir = os.path.join(os.getcwd(), 'temp_dir')
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        
        temp_file = os.path.join(temp_dir, 'temp_file.accdb')
        open(temp_file, 'a').close()

        # test valid path
        with unittest.mock.patch('builtins.input', return_value=temp_dir):
            user_input = self.menu.get_input('Enter file path: ', str, self.menu.is_valid_folder_path)
            self.assertEqual(user_input, temp_dir)

        # test invalid path
        with unittest.mock.patch('builtins.input', return_value=r'C:\Users\krastega\OneDrive - County of San Diego\Desktop\MicrosfotAcessDB'):
            user_input = self.menu.get_input('Enter file path: ', str, self.menu.is_valid_folder_path)
            self.assertFalse(self.menu.is_valid_folder_path(user_input))

        # test type verification
        with unittest.mock.patch('builtins.input', return_value='123'):
            result = self.menu.get_input('Enter a string: ', str)
            self.assertEqual(result, '123')

        # clean up temporary files
        os.remove(temp_file)
        os.rmdir(temp_dir)
    
    
    def test_get_test_centers(self):
        with unittest.mock.patch('builtins.input', side_effect = ['test_center_1', 'y', 'test_center_2', 'n']):
            test_centers = self.menu.get_test_centers()

            # Check if the function returned the expected number of test centers
            self.assertEqual(len(test_centers), 2)
            
            # Check if the function returned the expected test centers
            self.assertListEqual(test_centers, ['test_center_1', 'test_center_2'])


if __name__ == '__main__':
    unittest.main()
