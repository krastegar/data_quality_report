#-------------------------------------------------------------------------------------------
# 
#   Purpose:
#   Creating a 'Completeness Report' based on Range Exports from TST environment. This class 
#   will look at specific fields in the TST.accdb file and calculate the percentage of how many 
#   non-null / total entries seen in these specific fields. These fields are similar to what we see 
#   on the demographic and lab tabs of WebCMR. 
#   
#   Algorithm:
#       1. Create a database connection to .accdb file
#       2. Construct 2 queries. One to get information related to Demographic tab 
#          and another for information from Laboratory tab
#       3. Calculate the total of non_missing values over the complete total for that specific field
#          for all fields
#       4. Put values into a dataframe with percentages and export it as a .xlsx file
#       5. Done 
#
#   Author: Kiarash Rastegar
#   Date: 4/19/23
#-------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import logging 
import pyodbc
import re 

class Completeness:
    def __init__(
            self,
            lab_name,
            file_name,
            folder_path,
            test_center_1, 
            test_center_2 = None,
            test_center_3 = None,
            test_center_4 = None,
            test_center_5 = None
    ):
        self.lab_name = lab_name
        self.file_name = file_name
        self.folder_path = folder_path
        self.test1 = test_center_1
        self.test2 = test_center_2
        self.test3 = test_center_3
        self.test4 = test_center_4
        self.test5 = test_center_5

    def database_connection(self):
        """
        Establishes a connection to the database using the provided folder path and file name.

        :return: A tuple containing the connection object and the cursor object.
        :rtype: tuple
        """

        pyodbc.lowercase = False
        conn = pyodbc.connect(
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" +
            fr"Dbq={self.folder_path}\{self.file_name}")
        cursor = conn.cursor()
        return conn, cursor
    
    def tstRangeQuery_lab(self):
        """
        Generates a SQL query to retrieve specific fields from the 'Laboratory Information (system)'
        table based on the provided HL7 filenames.

        Returns:
            str: The SQL query string.
        """

        query = f'''
        SELECT 
            ACCESSIONNUMBER,
            ORDERRESULTSTATUS, 
            OBSERVATIONRESULTSTATUS,
            SPECCOLLECTEDDATE,
            SPECRECEIVEDDATE, 
            RESULTDATE,
            TESTCODE, 
            RESULTTEXT, 
            OrganismCode,
            ResultedOrganism,
            ABNORMALFLAG,
            REFERENCERANGE,
            SPECIMENSOURCE,
            PROVIDERNAME,
            PROVIDERADDRESS,
            PROVIDERCITY,
            PROVIDERSTATE,
            PROVIDERZIP,
            PROVIDERPHONE,
            FACILITYADDRESS,
            FACILITYCITY,
            FACILITYSTATE,
            FACILITYZIP,
            FACILITYPHONE, 
            FACILITYNAME,
            PERFORMINGFACILITYID, 
            IncidentID,
            RESULT
        FROM 
            [Laboratory Information (system)]
        WHERE 
            HL7FILENAME LIKE '%{self.test1}%' 
            OR HL7FILENAME LIKE '%{self.test2}%'
            OR HL7FILENAME LIKE '%{self.test3}%'
            OR HL7FILENAME LIKE '%{self.test4}%'
            OR HL7FILENAME LIKE '%{self.test5}%'
        '''
        return query
    
    def tstRangeQuery_demographic(self):
        """
        The function executes a SQL query to select the above fields from the 'Disease Incident Export' 
        table.The query filters the results based on the laboratory information provided through the 
        parameters.The laboratory information is used to perform partial string matching on the 
        'Laboratory' column.If any of the laboratory keywords (self.test1, self.test2, self.test3, 
        self.test4, self.test5) are found in the 'Laboratory' column, the corresponding 
        disease incident record is included in the result set.
        
        Returns:
            query (str): The SQL query string for the range query on demographic information.
        """

        
        query = f'''
        SELECT 
            Last_Name,
            First_Name, 
            DOB, 
            Street_Address,
            City,
            State,
            Zip,
            Home_Telephone, 
            Reported_Race as Race,
            Ethnicity,
            Sex,
            Incident_ID
        FROM 
            [Disease Incident Export]
        WHERE 
            Laboratory LIKE '%{self.test1}%' 
            OR Laboratory LIKE '%{self.test2}%'
            OR Laboratory LIKE '%{self.test3}%'
            OR Laboratory LIKE '%{self.test4}%'
            OR Laboratory LIKE '%{self.test5}%'
            '''
        return query

    def completeness_report(self):
        """
        After generating queries used to grab information from the .accdb files that are related to 
        WebCMR Lab and Demographics tab, we create a dataframe from them using range_export() method.
        The dataframe contains percent completeness of each desired field. Finally we combine both 
        dataframes into one excel sheet, which results in our final completeness summary report
        
        :return: A tuple containing two dataframes: lab_df and demo_df.
        :rtype: tuple
        """


        # generating queries for both Laboratory data and Demographic data 
        lab_query = self.tstRangeQuery_lab()
        demo_query = self.tstRangeQuery_demographic()

        # Creating dataframes from query results 
        lab_df = self.range_export_df(lab_query)
        demo_df = self.range_export_df(demo_query)

        return lab_df, demo_df

    def range_export_df(self, query):
        """
        Generates a DataFrame containing the percentage of complete information for each field of 
        interest. The Percent Completeness is done by looking at the total amount of 
        NonNull values / total (NonNull + Null) for each specified field in the query that is passed 
        to this method

        Args:
            query (str): The SQL query to retrieve the data from the database.
            
        Returns:
            pandas.DataFrame: A DataFrame with two columns: 'Fields of Interest' and 'Percent Complete'.
                The 'Fields of Interest' column contains the names of the fields in the dataset.
                The 'Percent Complete' column contains the percentage of complete information for each field.
        """

        df = self.query_df(query)

        # going to drop unwanted columns
        unwanted_columns = ['Incident_ID', 'IncidentID']
        for col in df.columns:
            if col in unwanted_columns:
                df.drop(col, axis=1)

        # Getting counts of Null and not Null values
        null_counts = df.isna().sum()
        nonNullCounts = df.count()
        
        # Calculating Percentage of complete information from those values. 
        difCounts = np.absolute(nonNullCounts.values) # this is a difference of arrays (might just want a ratio of )
        total_num = null_counts.values+nonNullCounts.values
        percent_complete = (difCounts/total_num)*100

        # Lab df done 
        lab_df = pd.DataFrame(
            {
            'Fields of Interest': list(df.columns),
            'Percent Complete' : percent_complete
            }
        )
        # formatting percent column
        lab_df['Percent Complete'] = lab_df['Percent Complete'].map('{:,.2f}'.format)
        lab_df['Percent Complete'] = lab_df['Percent Complete'].astype(float)

        return lab_df

    def query_df(self, query):
        """
        Executes a SQL query on a database and returns the result as a pandas DataFrame.
        
        Args:
            query (str): The SQL query to be executed.
            
        Returns:
            pandas.DataFrame: The result of the query as a DataFrame.
        """

        # need to establish database connection
        conn, _ = self.database_connection()
        df = pd.read_sql_query(query, conn)
        return df
    
    def report_builder(self):
        """
        Generates a report that includes completeness and cross-tabulation analyses for the 
        given query data.

        This function performs the following steps:
        1. Reads in a query for the demographics table and the lab table.
        2. Calculates the completeness for each field in the query data.
        3. Generates cross-tabulation dataframes for specific columns of interest.
        4. Checks if any of the generated dataframes are empty.
        5. Builds an Excel workbook with multiple sheets, including:
           - A sheet for the completeness report, containing both demographic and lab information.
           - A sheet for the cross-tabulation of ethnicity vs race.
           - A sheet for the cross-tabulation of abnormal flag vs resulted organism.
           - A sheet for the cross-tabulation of abnormal flag vs result.
           - A sheet for the frequency of blank reference range calculations in result tests.

        Parameters:
        - self: The current instance of the class.

        Returns:
        - None
        """
    
        # Read in a query for demographics table
        demo_query_df, lab_query_df = self.demo_lab_df()

        # generating all dataframes that are necessary for 
        logging.info('Calculating Completeness for each field in query DF')
        lab_complete_report_df, demo_complete_report_df = self.completeness_report()
        logging.info('Looking at the cross tab of Ethnicity vs Race')
        race_ethnicity_cross_df = self.cross_tab_df(demo_query_df, 'Ethnicity', 'Race')
        logging.info('Cross tab of Abnormal Flag vs ResultedOrganism')
        resultedOrganism_abflag_df = self.cross_tab_df(lab_query_df, 'ABNORMALFLAG','ResultedOrganism')
        logging.info('Cross tab of Abnormal Flag vs Result')
        result_abflag_df = self.cross_tab_df(lab_query_df, 'ABNORMALFLAG', 'RESULT')
        logging.info('Calculating how many ResultTest have blank reference range calculations')
        result_freq_df = self.result_test()

        # Check if any of the dataframes are empty
        dfs = [
            lab_complete_report_df, 
            demo_complete_report_df, 
            race_ethnicity_cross_df,
            resultedOrganism_abflag_df, 
            result_abflag_df, 
            result_freq_df
            ]
        # check to make sure the dataframes are not empty
        try:
            for i, df in enumerate(dfs):
                assert not df.empty, f"Dataframe {i+1} is empty! Check query construction"
        except AssertionError:
            logging.exception('Dataframe is empty! Check query construction')

        # Going to make one excel sheet with completeness reports from both demographic 
        # and lab information
        logging.info('Report Card is being built...')
        lab_name = re.sub(r'[^\w\s]+', '_',self.lab_name)
        writer = pd.ExcelWriter(f'{lab_name}_data_quality_reports.xlsx', engine='xlsxwriter')
        demo_complete_report_df.to_excel(
            writer, 
            sheet_name='CompletenessReport', 
            startcol=0, 
            index=False
            )
        lab_complete_report_df.to_excel(
            writer, 
            sheet_name='CompletenessReport', 
            startcol = len(demo_complete_report_df.columns)+1, 
            index=False
            )
        race_ethnicity_cross_df.to_excel(
            writer,
            sheet_name='Race_Ethnicity'
        )
        resultedOrganism_abflag_df.to_excel(
            writer,
            sheet_name='ResultedOrganism_AbNormalFlag'
        )
        result_abflag_df.to_excel(
            writer,
            sheet_name='Result_AbFlag'
        )
        result_freq_df.to_excel(
            writer,
            sheet_name = 'Blank_ReferenceRange'
        )
        # close writer object
        writer.close()

        
        return 

    def demo_lab_df(self):
        """
        Pulls queries from the demographic tab and the laboratory information tab.
        Transforms the query results into Pandas DataFrames.
        
        Returns:
            demo_query_df (DataFrame): The DataFrame containing the query results from the 
                                        demographic tab.
            lab_query_df (DataFrame): The DataFrame containing the query results from the 
                                        laboratory information tab.
        """

        logging.info('Pulling queries from demographic tab')
        demo_query = self.tstRangeQuery_demographic()

        logging.info('Getting query results for laboratory information')
        lab_query  = self.tstRangeQuery_lab()

        # generating query dataframes to be used later on in creating the crosstab
        logging.info('Tranforming Query results into Pandas Dataframe')
        demo_query_df = self.query_df(demo_query)
        lab_query_df = self.query_df(lab_query)
        return demo_query_df,lab_query_df
    
    def cross_tab_df(self, df : pd.DataFrame, index : str, column : str) -> pd.DataFrame:
        '''

        We are using a nested dictionary to store the count values for each unique pair b/w the 
        2 columns. Afterwards, we transform the nested dictionary into a dataframe that looks similar
        to a crosstab in pandas 

        Generates a cross-tabulation DataFrame based on the specified index and column values.

        This function takes in a pandas DataFrame and two column names: 'index' and 'column'. 
        It creates a cross-tabulation DataFrame that shows the count of unique values from the 
        'index' column and the 'column' column that are seen together.
            i.e)
                Race            Ethnicity
            White            Hispanic or Latino
            Asian            Not Hispanic or Latino
        Parameters:
            df (pd.DataFrame): The input DataFrame.
            index (str): The name of the column to be used as the index.
            column (str): The name of the column to be used as the column.

        Returns:
            pd.DataFrame: The cross-tabulation DataFrame.

        Algorithm Steps:
        1. Initialize an empty dictionary called 'counts' to store the counts of unique value pairs.
        2. Iterate over each row in the input DataFrame.
        3. Extract the values from the 'index' and 'column' columns for the current row.
        4. If any of the values is NaN or None, replace it with the string 'N/A'.
        5. Check if the value from the 'index' column already exists as a key in the 'counts' dictionary.
        - If it does not exist, create a new nested dictionary for that value.
        - The nested dictionary will be used to store counts of the 'index' value with each unique value from the 'column' column.
        6. Check if the value from the 'column' column already exists as a key in the nested dictionary.
        - If it exists, increment the count for that value pair by 1.
        - If it does not exist, create a new key-value pair with the count initialized to 1.
        7. After iterating over all rows, create a new DataFrame 'new_df' using the 'counts' dictionary.
        8. Replace any NaN values in the index and column names of 'new_df' with None.
        9. Add a new column called 'Total' to 'new_df' that sums up the row values.
        10. Add a new row to 'new_df' that contains the column-wise totals.
        11. Set the index name of 'new_df' to '{index} vs {column}'.

        Example usage:
        df = pd.DataFrame(...)
        result = cross_tab_df(df, 'index_column', 'column_column')
        print(result)
        '''
        
        counts = {}
        # creating count table of unique values from col 1 and 2 that are seen together

        for _, row in df.iterrows():
            col1_val = row[index]
            col2_val = row[column]
            
            # changing all NaN values into Null values 
            if col1_val in (np.nan, None): 
                col1_val = 'N/A'
            
            if col2_val in (np.nan, None): 
                col2_val = 'N/A'

            # looking at every value in the first column and making a dictionary for its 
            # pairs with every other value in col 2 
            if col1_val not in counts: # create dictionary for each value in col 1
                counts[col1_val] = {} # dictionary will be used to store counts of col 1 val with a specific col 2 val
            
            if col2_val in counts[col1_val]: # if a col 2 val already exists in nested dictionary add another count to that pair 
                counts[col1_val][col2_val] += 1
            else:
                counts[col1_val][col2_val] = 1 # if it doesn't exist create an instance of it and give it a count of 1

        # Now going to look at the the dictionary values and look inside the nested dictionary 
        # for counts and which ever counts is the most for that value pair I will use that as a match
        new_df = pd.DataFrame(counts)
        new_df.index = new_df.index.fillna(None)
        new_df.columns = new_df.columns.fillna(None)
        # adding totals column
        # Add a new column that sums up the row values
        new_df['Total'] = new_df.sum(axis=1)
        new_df.loc['Total'] = new_df.sum(axis=0) # code for new row of totals

        # adding name for crosstab data frame 
        new_df.index.name = f'{index} vs {column}'
        return new_df
    
    def result_test(self):
        """
        Generates a summary dataframe of the frequency and cumulative frequency of each lab result
        that had a blank 'RESULTTEXT' section, along with the name of the resulted test.
        
        Returns:
            result_freq_df (pandas.DataFrame): A dataframe with two columns: 
            'Frequency' and 'Cumulative Frequency'.
        """
        # Getting lab information data frame
        lab_query = self.tstRangeQuery_lab()
        lab_query_df = self.query_df(lab_query)
        no_ref_range_df = lab_query_df[
            lab_query_df['REFERENCERANGE'].isnull() | lab_query_df['REFERENCERANGE'].isna()
            ]
        # Get frequency and cumalitive frequency
        val_counts = no_ref_range_df['RESULTTEXT'].value_counts()
        cummal_sum = val_counts.cumsum(skipna=False)
        
        # Creating summary dataframe 
        result_freq_df = pd.DataFrame(
            {
            'Frequency': val_counts,
            'Cummalitive Frequency': cummal_sum
            }
        )
        return result_freq_df

    def combined_query_df(self):
        """
    	Combines the query dataframes and returns a new dataframe.

    	Returns:
    	    combined_df (pandas.DataFrame): The combined dataframe containing the joined 
                                            data from the demo and lab dataframes.
        """

        # grab both query df 
        demo_df, lab_df = self.demo_lab_df()
        lab_df.rename(columns={'IncidentID': 'Incident_ID'}, inplace=True)

        # Join the Tables of Disease Incident ID 
        combined_df = pd.merge(
        demo_df,
        lab_df,
        on=['Incident_ID'],
        how='inner'
        )

        return combined_df