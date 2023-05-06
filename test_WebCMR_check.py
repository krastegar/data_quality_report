import unittest
import os
import pandas as pd
import numpy as np
import docx
from WebCMR_check import WebCMR_check
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,UnexpectedAlertPresentException
from collections import Counter


class TestWebCMRClass(unittest.TestCase):
    def setUp(self):
        self.test_instance = WebCMR_check(
            file_name= 'TST_DIE_04202023_05042023.accdb',
            lab_name='NameForFile',
            folder_path= '..\MicrosoftAcessDB',
            test_center_1='Palomar',
            test_center_2='Pomerado',
            username='krastegar',
            paswrd='Hamid&Mahasty2'
        )
        self.driver_path = 'chromedriver.exe'
    
    def test_login(self):
        
        obj : WebCMR_check = self.test_instance
        # make sure webdriver is in package environment
        self.assertTrue(os.path.isfile(self.driver_path), "Webdriver path is invalid.")

        # Create chrome webdriver object with the above options
        service : ChromeService = ChromeService(executable_path=self.driver_path)
        driver : webdriver = webdriver.Chrome(service=service)

        # Assert that the driver object is not None
        self.assertIsNotNone(driver)

        # Test sending of GET request through driver
        driver.get(obj.url)

        # Assert that the current URL of the driver is the expected URL
        expected_url : str = obj.url
        self.assertEqual(driver.current_url, expected_url)

        # Close the driver
        driver.close()
    
    def test_get_hl7(self):

        # Method call
        #self.test_instance.get_hl7()

        # check to see report is being produced 
        self.assertTrue(os.path.isfile('HL7_Error.docx'), "No word Doc Produced.")

        # checking to see if there is anything written in word doc
        doc : docx = docx.Document('HL7_Error.docx')
        self.assertTrue(any(len(p.text) > 0 for p in doc.paragraphs))

    def test_date_check(self):

        # creating test dataframe to make sure that my checks are working
        date_df : pd.DataFrame = pd.DataFrame({    # normal       2 < 1        3 < 2          normal      3<2, 3<1, 2<1       
            'SPECCOLLECTEDDATE' : ['04/05/2023', '04/06/2023', '05/05/2023', '05/02/2023', '04/25/2023'],
            'SPECRECEIVEDDATE' : ['04/06/2023', '04/04/2023', '05/07/2023', '05/06/2023', '04/20/2023'],
            'RESULTDATE' : ['04/08/2023', '04/10/2023', '05/06/2023', '05/11/2023', '04/19/2023'], 
            'RESULTTEXT' : ['A', 'B', 'C', 'D', 'E'], 
            'ACCESSIONNUMBER' : [1, 2, 3, 4, 5]
        })

        # getting results  
        date_errors : list = self.test_instance.date_check(date_df)

        # looking at all components of the results 
        acc_nums : list = []
        error_types : list  = []
        for errors in date_errors:
            acc_num : int = errors[1]
            error_type : str = errors[2][0]
            acc_nums.append(acc_num); error_types.append(error_type)
        
        # counting occurences of each unique value in these lists 
        acc_dict: dict = Counter(acc_nums); error_type_dict : dict = Counter(error_types)

        # checking to see if dicitonaries match expected values 
        expected_acc_dict = {5: 3, 2: 1, 3: 1}
        expected_error_type_dict = {
            'SpecCollectDate Error (w/Recieve Date)': 2, 
            'SpecRecieveDate Error (w/Result Date)': 2, # change to 1 to see how the error message looks
            'SpecCollectDate Error (w/Result Date)': 1
            }
        # testing correct number of accession number are found for each category
        self.assertEqual(acc_dict[5], expected_acc_dict[5])
        self.assertEqual(acc_dict[2], expected_acc_dict[2])
        self.assertEqual(acc_dict[3], expected_acc_dict[3])

        # testing correct number of error type are found for each category
        self.assertEqual(error_type_dict['SpecCollectDate Error (w/Recieve Date)'], expected_error_type_dict['SpecCollectDate Error (w/Recieve Date)'])
        self.assertEqual(error_type_dict['SpecRecieveDate Error (w/Result Date)'], expected_error_type_dict['SpecRecieveDate Error (w/Result Date)'])
        self.assertEqual(error_type_dict['SpecCollectDate Error (w/Result Date)'], expected_error_type_dict['SpecCollectDate Error (w/Result Date)'])
        
        # test to see amount of errors caught is correct 
        self.assertTrue(len(date_errors) == 5)

        # testing to see the correct amount of unique examples (acc_num):
        self.assertTrue(len(np.unique(acc_nums))==3)

    def test_threshold_search(self):
        
        # create a sample combined query dataframe for testing
        combined_query_df : pd.DataFrame = pd.DataFrame({
            'RESULTTEXT': ['result1', 'result2', 'result3', 'result4', 'result5'],
            'ACCESSIONNUMBER': ['accession1', 'accession2', 'accession3', 'accession4', 'accession5'],
            'demo_field1': [1, 2, np.nan, 4, 5],
            'demo_field2': [6, 7, 8, 9, np.nan],
            'lab_field1': [np.nan, 12, 13, 14, 15],
            'lab_field2': [16, 17, 18, np.nan, 20]
        })
        
        # create a mock object for completeness_report method that returns sample completeness reports
        demo_complete_df = pd.DataFrame({
            'Fields of Interest': ['demo_field1', 'demo_field2'],
            'Percent Complete': [40.0, 60.0]
        })
        lab_complete_df = pd.DataFrame({
            'Fields of Interest': ['lab_field1', 'lab_field2'],
            'Percent Complete': [80.0, 60.0]
        })
        
        # create an instance of MyTestClass and set the mock objects
        my_test_class = self.test_instance
        
        # run the method to be tested
        threshold_error = my_test_class.threshold_search(combined_query_df, demo_complete_df, lab_complete_df)
        
        # check the expected values (this check might change when I have real threshold values)
        self.assertEqual(len(threshold_error), 4) 
        self.assertIn(('result3', 'accession3', 'demo_field1'), threshold_error) 
        self.assertIn( ('result5', 'accession5', 'demo_field2'), threshold_error) 
        self.assertIn(('result1', 'accession1', 'lab_field1'), threshold_error) 
        self.assertIn(('result4', 'accession4', 'lab_field2'), threshold_error)
    





if __name__ == '__main__':
    unittest.main()
