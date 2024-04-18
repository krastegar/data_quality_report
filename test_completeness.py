import os
import unittest
import pyodbc
import pandas as pd
import numpy as np
from Completeness import Completeness


class TestCompletenessClass(unittest.TestCase):
    def setUp(self):
        self.test_instance = Completeness(
            file_name= 'TST_DIE_04202023_05042023.accdb',
            lab_name='NameForFile',
            folder_path= '..\MicrosoftAcessDB',
            test_center_1='Palomar',
            test_center_2='Pomerado'
        )
        self.lab_query = self.test_instance.tstRangeQuery_lab()
        self.demographic_query = self.test_instance.tstRangeQuery_demographic()
    
    def test_database_connection(self):
        # Ensure that conn is a pyodbc Connection object
        expected_conn_type = pyodbc.Connection
        conn, cursor = self.test_instance.database_connection()
        self.assertIsInstance(conn, expected_conn_type)

        # Ensure that cursor is a cursor for a pyodbc Connection object
        expected_cursor_type = pyodbc.Cursor
        self.assertIsInstance(cursor, expected_cursor_type)
        self.assertEqual(cursor.connection, conn)

    def test_query_df(self):
        # going to make sure that sql query can make pandas dataframe 
        # this also is a check to make sure the query is structured properly 

        # checking to see what is returned is a pandas dataframe and is not empty 
        expected_datastructure = pd.DataFrame
        df = self.test_instance.query_df(self.lab_query)
        df2 = self.test_instance.query_df(self.demographic_query)
        self.assertIsInstance(df, expected_datastructure) # testing write df
        self.assertIsInstance(df2, expected_datastructure)
        self.assertIsNotNone(df) # testing return of dataframe object
        self.assertIsNotNone(df2)
        self.assertFalse(df.empty) # checking if dataframe is empty
        self.assertFalse(df2.empty)

    def test_range_query_df(self):

        # Checking that both queries produce percent complete columns that are not all null
        # Also checking if the columns are standard 
        lab_range_df = self.test_instance.range_export_df(self.lab_query)
        demo_range_df = self.test_instance.range_export_df(self.demographic_query)
        self.range_testing(lab_range_df)
        self.range_testing(demo_range_df)

    def range_testing(self, range_df):
        
        '''
        Helper test function for test_range_query_df(). Used so that I do not have to repeat logic
        for both queries 
        '''
        # checking to see if the columns are standard 
        self.assertTrue("Percent Complete" in range_df.columns)
        self.assertTrue("Fields of Interest" in range_df.columns)

        # checking to see if the percent column is not all nulls or nan's
         # Assert that the resulting dataframe is not empty
        self.assertFalse(range_df.empty, "Dataframe should not be empty")

        # Assert that the 'Percent Complete' column does not contain NaN or None values
        self.assertFalse(range_df['Percent Complete'].isna().any())
        self.assertFalse(range_df['Percent Complete'].isnull().any())

        # Check that Percent Column is float data type
        self.assertTrue(all(isinstance(val, float) for val in range_df['Percent Complete']), 'Not all types are floats')

        # Assert that 'Percent Complete' column has no values greater than 100 or negative values
        self.assertFalse((range_df['Percent Complete'] > 100).any())
        self.assertFalse((range_df['Percent Complete'] < 0).any())

    def test_completeness_report(self):
        
        # check if that both of the dataframes are pandas data frames 
        expected_structure = pd.DataFrame
        lab_df, demo_df = self.test_instance.completeness_report()
        self.assertIsInstance(lab_df, expected_structure)
        self.assertIsInstance(demo_df, expected_structure)
        
        # checking to see if the dataframes are empty 
        self.assertFalse(lab_df.empty)
        self.assertFalse(demo_df.empty)
    
    def test_cross_tab_df(self):
        df = pd.DataFrame(
            {
                'Ethnicity' : [
                    'hispanic or latino', 
                    'not hispanic or latino', 
                    'not hispanic or latino',
                    'hispanic or latino', 
                    'not hispanic or latino',
                    None,
                    np.nan,
                    np.nan
                    ],
                'Race' : ['white', 'white', 'asian', None, np.nan, None, np.nan, np.nan]
            }
        )
        # calling test function 
        result = self.test_instance.cross_tab_df(df, 'Ethnicity', 'Race')

        # test index name
        self.assertEqual(result.index.name, 'Ethnicity vs Race')

        # test total row
        self.assertEqual(result.loc['Total', 'Total'], 8)

        # test total column
        self.assertEqual(result.loc['asian','Total'], 1)

        # test count of unique pair
        self.assertEqual(result.loc['white','hispanic or latino'], 1)

        # test None type pairs 
        self.assertEqual(result.loc['N/A', 'N/A'], 3)

        # check if NaN or Null is in any of the index or column valuse
        self.assertFalse(result.index.isna().any()) # isinstance doesn't work on np.nan 
        self.assertFalse(result.columns.isna().any()) # np.nan is not a class or subclass 
        self.assertFalse(result.index.isnull().any())
        self.assertFalse(result.columns.isnull().any())
    
    def test_result_test(self):
        result_df = self.test_instance.result_test()

        # checking that none of the freq and cummalitive freq are less than 0
        self.assertFalse((result_df['Frequency'] < 0).any())
        self.assertFalse((result_df['Cummalitive Frequency'] < 0).any())

        # checking to make sure the column names stay the same
        allowed_columns = ['Frequency', 'Cummalitive Frequency']
        self.assertTrue(all(col in allowed_columns for col in result_df.columns))

        # test if dataframe is full of nan values or empty
        self.assertFalse(result_df.isna().all().all())
        self.assertFalse(result_df.isnull().all().all())
        

    def test_report_builder(self):
        
        # call method for testing
        report = self.test_instance
        report.report_builder()

        # Check if the Excel file was created
        assert os.path.isfile(f'{report.lab_name}_data_quality_reports.xlsx'), "Excel file not created"
    
        # Check if each sheet has at least one row of data
        with pd.ExcelFile(f'{report.lab_name}_data_quality_reports.xlsx') as reader:
            assert len(pd.read_excel(reader, sheet_name='CompletenessReport')) >= 1, "CompletenessReport sheet is empty"
            assert len(pd.read_excel(reader, sheet_name='Race_Ethnicity')) >= 1, "Race_Ethnicity sheet is empty"
            assert len(pd.read_excel(reader, sheet_name='ResultedOrganism_AbNormalFlag')) >= 1, "ResultedOrganism_AbNormalFlag sheet is empty"
            assert len(pd.read_excel(reader, sheet_name='Result_AbFlag')) >= 1, "Result_AbFlag sheet is empty"
            assert len(pd.read_excel(reader, sheet_name='Blank_ReferenceRange')) >= 1, "Blank_ReferenceRange sheet is empty"

    def test_combined_query(self):

        # calling method
        combined_df = self.test_instance.combined_query_df()

        # Checking to see if it contains all of the columns that I am expecting
        expected_columns = [
            'ACCESSIONNUMBER',
            'ORDERRESULTSTATUS', 
            'OBSERVATIONRESULTSTATUS',
            'SPECCOLLECTEDDATE',
            'SPECRECEIVEDDATE', 
            'RESULTDATE',
            'TESTCODE', 
            'RESULTTEXT', 
            'OrganismCode',
            'ResultedOrganism',
            'ABNORMALFLAG',
            'REFERENCERANGE',
            'SPECIMENSOURCE',
            'PROVIDERNAME',
            'PROVIDERADDRESS',
            'PROVIDERCITY',
            'PROVIDERSTATE',
            'PROVIDERZIP',
            'PROVIDERPHONE',
            'FACILITYADDRESS',
            'FACILITYCITY',
            'FACILITYSTATE',
            'FACILITYZIP',
            'FACILITYPHONE', 
            'FACILITYNAME',
            'PERFORMINGFACILITYID', 
            'IncidentID',
            'RESULT',
            'Last_Name',
            'First_Name', 
            'DOB', 
            'Street_Address',
            'City',
            'State',
            'Zip',
            'Home_Telephone', 
            'Race',
            'Ethnicity',
            'Sex',
            'Incident_ID'
        ]
        # testing to see if the columns are in expected columns
        self.assertTrue(all(col in expected_columns for col in combined_df.columns))
        
        # test if dataframe is full of nan values or empty
        self.assertFalse(combined_df.isna().all().all())
        self.assertFalse(combined_df.isnull().all().all())

    def tearDown(self) -> None:
        return super().tearDown()
    
if __name__ == '__main__':
    unittest.main()
