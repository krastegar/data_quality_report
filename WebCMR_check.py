import pandas as pd
import numpy as np
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,UnexpectedAlertPresentException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Completeness import Completeness
from typing import Union
from docx import Document

class WebCMR_check(Completeness):
    def __init__(
        self, 
        username, 
        paswrd, 
        url = 'https://test-sdcounty.atlasph.com/TSTWebCMR/pages/login/login.aspx',
        *args,
        **kwargs
        ):
        super().__init__(*args, **kwargs)
        self.url = url 
        self.username = username
        self.paswrd = paswrd

    def login(self): 

        '''
        Function is meant to go to specified url for webcmr, i.e)
        TSTWebCMR
        TRNWebCMR
        WebCMR (Production)
        '''
        # create chrome webdriver object with the above options
        service : ChromeService = ChromeService(executable_path="chromedriver.exe")
        driver : webdriver = webdriver.Chrome(service=service)

        # go to TST website
        driver.get(self.url)

        # Find the username and password elements and enter login credentials
        # time.sleep(1)
        username = driver.find_element(By.ID, value="txtUsername")
        username.send_keys(self.username)
        password = driver.find_element(By.ID, value="txtPassword")
        password.send_keys(self.paswrd)
        # time.sleep(.5)
        password.send_keys(Keys.RETURN)
        
        return driver
    
    def acc_test_search(self, acc_num, driver,resultTest=None):

        # navigate to IMM menu
        _ = self.nav2IMM(driver) 

        acc_box = self.multiFind(
            driver=driver,
            element_id= 'txtAccession',
            xpath='/html/body/form/div[3]/div/div/table[3]/tbody/tr[2]/td/table/tbody/tr[1]/td[8]/input'
        )
        acc_box.clear()
        acc_box.send_keys(str(acc_num))

        search_id : str = 'ibtnSearch'
        search_btn : webdriver = self.multiFind(
            driver=driver,
            element_id= search_id,
            xpath='/html/body/form/div[3]/div/div/table[3]/tbody/tr[2]/td/table/tbody/tr[4]/td/div/input[1]'
        )
        search_btn.click()
        return driver
    
    def get_hl7(self):
        '''
        Method to go into IMM menu and conduct a search based on accession number and ResultTest.
        The program grabs example HL7 messages that have failed either date value checks or our examples
        of regions where they have 
        '''
        
        # Creating word document object for hl7 reports
        doc : Document = Document()
        doc.add_heading('HL7 Error Examples')

        # calling combined query
        combined_query_df : pd.DataFrame = self.combined_query_df()
        demo_complete_df ,lab_complete_df = self.completeness_report()

        # Get the list of Accession numbers from both date_check and threshold_search
        date_accession : list = self.date_check(combined_query_df)
        threshold_accession : list = self.threshold_search(
            master_table=combined_query_df,
            demo_complete_df=demo_complete_df,
            lab_complete_df=lab_complete_df
        )
        accession_search : list = date_accession + threshold_accession

        # get driver: 
        driver = self.login()

        for index, search_params in enumerate(accession_search):
            try:
            
                result_test : str = search_params[0]
                acc_num : int = search_params[1]
                distinguifier : Union[str, list] = search_params[2] # union is a method to type hint two types

                if isinstance(distinguifier, str):
                    self.hl7_extraction(
                        doc, 
                        accession_search, 
                        index, 
                        result_test, 
                        acc_num, 
                        heading='THRESHOLD ERROR', 
                        driver=driver
                    )  
                    #time.sleep(2)
                if isinstance(distinguifier, list):
                    # Need to tailor accession search variable to give a good header 
                    accession_search : list = [accession_search[0], accession_search[1], accession_search[2][1]]
                    self.hl7_extraction(
                        doc, 
                        accession_search,
                        index, 
                        result_test, 
                        acc_num, 
                        heading='DATE ERROR', 
                        driver=driver
                    )
                    #time.sleep(2)
            except UnexpectedAlertPresentException:
                continue
        doc.save("HL7_Error.docx")
        return

    def hl7_extraction(self, doc, accession_search, index, result_test, acc_num, heading , driver):
        driver : webdriver = self.acc_test_search(
                    acc_num=acc_num, resultTest=result_test, driver=driver
                    )
        table : str = driver.find_element(By.ID, "divContentsArea").text       
        doc.add_heading(f'{heading}: {accession_search[index][2]}')
        doc.add_paragraph(table)
        pass 

    def multiFind(self, driver, element_id, xpath=None, field_name=None ):
        
        '''
        Function is meant to locate regions on html web page, 
        using the elements ID as a identifier. If element is not found 
        by ID, function will attempt to find it by XPath.
        '''
        wait = WebDriverWait(driver, 2)
        try: 
            element_btn = wait.until(EC.presence_of_element_located((By.ID, element_id)))
        except NoSuchElementException:
            if xpath:
                # this is the full or relative xpath 
                element_btn = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            elif field_name: 
                # field name is a fail-safe to find element if the id by itself is not working
                # typing in the filed name will remind me which section to look at if it breaks
                # this is using a partial xpath to find element
                element_btn = wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(@id, {element_id})]")))
            else:
                raise NoSuchElementException(f"Element with ID {element_id} and XPath {xpath} not found.")
        
        return element_btn
    
    def go_home(self, driver):
        '''
        Method is meant to navigate back home, using home icon button
        to get there
        '''
        # Clicking home button 
        home_btn = self.multiFind(
            driver = driver, 
            element_id='FragTop1_lbtnHome',
            xpath= '/html/body/form/table[2]/tbody/tr/td[1]/div/a'
            )
        home_btn.click()

        # Clicking Search button (this is the investigators equivalent of my home button)
        investigators_search = self.multiFind(
            driver=driver,
            element_id='FragTop1_mnuMain-menuItem002',
            xpath='/html/body/form/table[2]/tbody/tr/td[2]/table[36]/tbody/tr/td[1]'
        )
        investigators_search.click()
        return
    
    def nav2IMM(self, driver):
        '''
        Only works if you are at the home page and want to navigate to IMM menu
        '''
        # Navigating back to home page
        self.go_home(driver)

        # Looking at Administrator dropdown menu
        wait = WebDriverWait(driver, 8)
        #dropdown_menu = wait.until(EC.presence_of_element_located((By.ID, "FragTop1_mnuMain-menuItem017")))
        dropdown_menu = self.multiFind(
            driver=driver,
            element_id= "FragTop1_mnuMain-menuItem017",
            xpath='/html/body/form/table[2]/tbody/tr/td[2]/table[36]/tbody/tr/td[6]'
        )
        dropdown_menu.click()

        # Hopefully clicking on incoming message monitor options
        # Wait for the second level dropdown to be present and then click on it
        #second_menu = "FragTop1_mnuMain-menuItem017-subMenu-menuItem009"
        second_level_dropdown = self.multiFind(
            driver, 
            element_id= "FragTop1_mnuMain-menuItem017-subMenu-menuItem009",
            xpath='/html/body/form/table[2]/tbody/tr/td[2]/table[16]/tbody/tr[9]/td'
        )
        second_level_dropdown.click()

        # Wait for the desired option to be present and then click on it
        imm = 'FragTop1_mnuMain-menuItem017-subMenu-menuItem009-subMenu-menuItem003'
        desired_option = self.multiFind(
            driver=driver,
            element_id=imm,
            xpath='/html/body/form/table[2]/tbody/tr/td[2]/table[5]/tbody/tr[3]/td'
        )
        desired_option.click()
        return
    
    def date_check(self, combined_query_df) -> list:

        '''
        Method to find all combinations of dates that violate logical lense.
        i.e) breaks this logic
                collection_date < received_date < result_date
        where '<' signifies earlier date
        '''

        # call combinded query df
        # combined_query_df = self.combined_query_df()

        # Array of accession for date errors
        date_errors = []
        # looking at every row and checking date conditions
        for _, row in combined_query_df.iterrows():
            # get timestamp variables
            spec_col_date = row['SPECCOLLECTEDDATE']
            spec_rec_date = row['SPECRECEIVEDDATE']
            result_date = row['RESULTDATE']

            # running checks on valid time combinations 
            if spec_col_date > spec_rec_date:
                date_errors.append(
                    (
                        row['RESULTTEXT'],
                        row['ACCESSIONNUMBER'],
                        ['SpecCollectDate Error (w/Recieve Date)',f'SpecCollectDate Error (w/Recieve Date) : {spec_col_date} > {spec_rec_date}']
                    )
                )
            if spec_rec_date > result_date:
                date_errors.append(
                    (
                        row['RESULTTEXT'],
                        row['ACCESSIONNUMBER'],
                        ['SpecRecieveDate Error (w/Result Date)',f'SpecRecieveDate Error (w/Result Date) : {spec_rec_date} > {result_date}']
                    )
                )
            if spec_col_date > result_date:
                date_errors.append(
                    (
                        row['RESULTTEXT'],
                        row['ACCESSIONNUMBER'], 
                        ['SpecCollectDate Error (w/Result Date)',f'SpecCollectDate Error (w/Result Date) : {spec_col_date} > {result_date}']
                    )
                )
            
        return date_errors
    
    def threshold_search(self, master_table, demo_complete_df ,lab_complete_df) -> list:

        '''
        This method is meant to look at the completeness report of both lab and demographics data, and
        compare it to a standard threshold that has been predetermined an hardcoded into the program. If 
        a field has a percent complete value less than the threshold, the program grabs one specific combo
        of Accession Number and Result Test where that field has a blank entry 
        '''

        # making sure index's are not an issue in later analysis
        master_table.reset_index(inplace=True)
        
        
        # Going to concatenate into one df
        combined_complete_df : pd.DataFrame 
        combined_complete_df = pd.concat([demo_complete_df, lab_complete_df])
        combined_complete_df.reset_index(inplace=True)
        combined_complete_df['Percent Complete'] : pd.Series
        combined_complete_df['Percent Complete'] = combined_complete_df['Percent Complete'].astype(float)
        print(combined_complete_df)
        # building a dictionary that has the threshold value for every specific field of interest
        # At the same time checking if the threshold value is less than the percent complete
        # and then trying to find the accession numbers for one of the blank fields in the that category
        threshold_key_pair : dict = {}
        threshold_vals : list = [
            100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,
            100,100,100,100,100,100,100,100,100,100,100,100,100,95,95,95,95,95,
            100,100,100,100
            ] # need marjorie to give me a list of thresholds similar to this 
        
        threshold_error : list = []
        for i, row in combined_complete_df.iterrows():
            col : str = row['Fields of Interest']
            pc : float = row['Percent Complete']
            threshold_key_pair[col] = threshold_vals[i]

            # if Percent complete is lower than threshold we need to look at a subset of master table
            # and pull out a accession number of a field where there is a nan value. We will look at 
            # only the first occurrence of nan value for this search 
            
            if pc < float(threshold_vals[i]):
                # filtering table on missing values using both NaN and Null for missing
                master_subset : pd.DataFrame = master_table[master_table[col].isna() | master_table[col].isnull()]

                assert len(master_subset) > 0
                
                # grabbing first row that contains NaN value of columns that 
                master_subset_row: pd.DataFrame = master_subset.iloc[0]

            # Appending the accession numbers that do not meet threshold criteria  
                threshold_error.append(
                    (
                    master_subset_row['RESULTTEXT'],
                    master_subset_row['ACCESSIONNUMBER'],
                    col
                    )
                )
        # there are 40 fields of interest, want to make sure we only grab 1 from each field that fails
        # Percent Complete threshold set by marjorie, So there couldn't be more than 40 elements total
        # in threshold_error list 
        assert len(threshold_error) < 41
        
        return threshold_error