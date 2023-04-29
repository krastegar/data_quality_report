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
        '''
        Creating database connection to run sql queries and extract necessary
        information from Microsoft Access files
        '''
        pyodbc.lowercase = False
        conn = pyodbc.connect(
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" +
            fr"Dbq={self.folder_path}\{self.file_name}.accdb")
        cursor = conn.cursor()

        return conn, cursor
    
    def tstRangeQuery_lab(self):
        '''
        Query string that is meant to extract relative information for looking at TST WebCMR data
        in bulk. In this example I am only using two test centers. If we are looking at 3 or more then
        I can make the requirements for the function a list or something.
        '''
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
            FACILITYNAME LIKE '%{self.test1}%' 
            OR FACILITYNAME LIKE '%{self.test2}%'
            OR FACILITYNAME LIKE '%{self.test3}%'
            OR FACILITYNAME LIKE '%{self.test4}%'
            OR FACILITYNAME LIKE '%{self.test5}%'
        '''
        return query
    
    def tstRangeQuery_demographic(self):
        '''
        Similar objective to tstRangeQuery_lab, but the select statement is meant
        to get different information from the disease incident table from the .accdb file
        '''
        
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
        '''
        After generating queries used to grab information from the .accdb files that are related to 
        WebCMR Lab and Demographics tab, we create a dataframe from them using range_export() method.
        The dataframe contains percent completeness of each desired field. Finally we combine both 
        dataframes into one excel sheet, which results in our final completeness summary report
        '''

        # generating queries for both Laboratory data and Demographic data 
        lab_query = self.tstRangeQuery_lab()
        demo_query = self.tstRangeQuery_demographic()

        # Creating dataframes from query results 
        lab_df = self.range_export_df(lab_query)
        demo_df = self.range_export_df(demo_query)

        return lab_df, demo_df

    def range_export_df(self, query):
        '''
        After constructing the query and making the connection to the database. We create 
        a dataframe that summarize the results of the bulk exports. The summary is done by looking
        at the total amount of NonNull values / total (NonNull + Null) for each specified field in 
        the query that is passed to this method 
        '''
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
        lab_df['Percent Complete'] = lab_df['Percent Complete'].map('{:,.2f}'.format)
        return lab_df

    def query_df(self, query):
        '''
        Helper function to create a pandas dataframe from an sql query 
        '''
        # need to establish database connection
        conn, _ = self.database_connection()
        df = pd.read_sql_query(query, conn)
        return df
    
    def report_builder(self):
        # Steps to producing cross tab
        # 1. look into the table the query produce
        # 2. use pandas.crosstab() for the two columns of interest 
    
        # Read in a query for demographics table
        demo_query_df, lab_query_df = self.demo_lab_df()

        # generating all dataframes that are necessary for 
        lab_complete_report_df, demo_complete_report_df = self.completeness_report()
        race_ethnicity_cross_df = self.cross_tab_df(demo_query_df, 'Ethnicity', 'Race')
        resultedOrganism_abflag_df = self.cross_tab_df(lab_query_df, 'ABNORMALFLAG','ResultedOrganism')
        result_abflag_df = self.cross_tab_df(lab_query_df, 'ABNORMALFLAG', 'RESULT')
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
        for i, df in enumerate(dfs):
            assert not df.empty, f"Dataframe {i+1} is empty! Check query construction"

        # Going to make one excel sheet with completeness reports from both demographic 
        # and lab information
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
            sheet_name = 'Frequency_ResultTest'
        )
        # close writer object
        writer.close()

        
        return 

    def demo_lab_df(self):
        '''
        Method that produces both demographics dataframe and lab info dataframe, from 
        the query strings produced from tstRangeQuery
        '''
        demo_query = self.tstRangeQuery_demographic()
        lab_query  = self.tstRangeQuery_lab()

        # generating query dataframes to be used later on in creating the crosstab
        demo_query_df = self.query_df(demo_query)
        lab_query_df = self.query_df(lab_query)
        return demo_query_df,lab_query_df
    
    def cross_tab_df(self, df, index, column):
        '''
        The function loops through two columns and sees how frequently each column pairs are 
        seen next to each other
        i.e)
            Race            Ethnicity
        White            Hispanic or Latino
        Asian            Not Hispanic or Latino
        We are using a nested dictionary to store the count values for each unique pair b/w the 
        2 columns. Afterwards, we transform the nested dictionary into a dataframe that looks similar
        to a crosstab in pandas 
        '''
        
        counts = {}
        # creating count table of unique values from col 1 and 2 that are seen together

        for _, row in df.iterrows():
            col1_val = row[index]
            col2_val = row[column]
            
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

        # adding totals column
        # Add a new column that sums up the row values
        new_df['Total'] = new_df.sum(axis=1)
        new_df.loc['Total'] = new_df.sum(axis=0) # code for new row of totals

        # adding name for crosstab data frame 
        new_df.index.name = f'{index} vs {column}'
        return new_df
    
    def result_test(self):

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
        '''
        Joining both Demographics Information and Lab Information into one dataframe. Dataframe
        will be used to check fields in completeness report and Dates, which will be used to check 
        '''
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