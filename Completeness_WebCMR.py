import sys
import logging
import pyodbc
from menu import Menu
from WebCMR_check import WebCMR_check
from selenium.common.exceptions import (SessionNotCreatedException,
                                        NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException,
                                        WebDriverException)

"""
Purpose:
This program is designed to analyze the range export of ELR's in the TST environment. It determines 
the completeness of each specified field seen in the TST environment. After calculating the 
completions, it looks at the cross-tabulation of data for each column and their unique 'index's'. 
It then generates a report card in the form of an Excel workbook with multiple sheets.

Algorithm:
1. Calculate the completion scores for the specified fields of interest.
2. Perform searches for HL7 messages that are part of the specified fields but do not meet the threshold criteria.
3. Take the first instance of the error'd HL7 messages and put them under a header for that field error.
4. Print the error'd HL7 messages as an example on a Word document.
"""

def main():
    
    """
    The main function of the program. It performs the following tasks:
    1. Sets up logging for the process.
    2. Gets user input for various parameters.
    3. Checks if there are any test centers saved.
    4. Creates an instance of the WebCMR_check class based on the number of test centers.
    5. Calls functions to generate a quality report and retrieve error examples.
    6. Handles various exceptions that may occur during the execution of the program.
    7. Logs the completion of the program.
    """

    # Logging process
    logging.basicConfig(filename='Completeness_Log.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

    # calling my menu object
    menu = Menu()

    logging.info('Getting user input ')
    # getting the inputs for the program
    file_name = menu.get_input("Enter TST range export file w/.accdb extension: ", str)
    lab_name = menu.get_input("Enter name for data quality report card: ", str) 
    folder_path = menu.get_input("Enter complete folder_path to TST range exports and IMM exports: ", 
                                 str, 
                                 lambda x: menu.is_valid_folder_path(x))
    test_centers = menu.get_test_centers()
    username = menu.get_input("Enter TST username: ", str)
    password = menu.get_input("Enter TST password: ", str)

    try:
        assert len(test_centers) > 0
    except AssertionError as assert_error:
        logging.exception('There were not any test centers saved %s', assert_error)

    logging.info(
        f'''
        Successfully grabbed user input!

        ------ User Parameters ------ 
        USER_NAME : {username}
        PASSWORD : {password}
        FILE_NAME : {file_name}
        FOLDER_PATH : {folder_path}
        TEST_CENTERS : {test_centers}
        # OF TEST_CENTERS : {len(test_centers)}
        ----------------------------- 
        '''
    )
    try: 
        if len(test_centers) == 1:
            report_maker = WebCMR_check(
                file_name = file_name, 
                lab_name = lab_name,
                folder_path = folder_path,
                test_center_1 = test_centers[0], 
                username = username, 
                paswrd = password
                )
        elif len(test_centers) == 2:
            report_maker = WebCMR_check(
            file_name = file_name, 
            lab_name = lab_name,
            folder_path = folder_path,
            test_center_1 = test_centers[0], 
            test_center_2 = test_centers[1],
            username = username, 
            paswrd = password
            )
        elif len(test_centers) == 3:
            report_maker = WebCMR_check(
            file_name = file_name, 
            lab_name = lab_name,
            folder_path = folder_path,
            test_center_1 = test_centers[0], 
            test_center_2 = test_centers[1],
            test_center_3 = test_centers[2],
            username = username, 
            paswrd = password
            )
        elif len(test_centers) == 4:
            report_maker = WebCMR_check(
            file_name = file_name, 
            lab_name = lab_name,
            folder_path = folder_path,
            test_center_1 = test_centers[0], 
            test_center_2 = test_centers[1],
            test_center_3 = test_centers[2],
            test_center_4 = test_centers[3],
            username = username, 
            paswrd = password
            )
        elif len(test_centers) == 5:
            report_maker = WebCMR_check(
            file_name = file_name, 
            lab_name = lab_name,
            folder_path = folder_path,
            test_center_1 = test_centers[0], 
            test_center_2 = test_centers[1],
            test_center_3 = test_centers[2],
            test_center_4 = test_centers[3],
            test_center_5 = test_centers[4],
            username = username, 
            paswrd = password
            )

        # function calls to generate quality report and error examples 
        logging.info('Building Excel Report Card, with all of the reports on each tab...')
        report_maker.report_builder()
        logging.info('Starting webscraping for examples that did not meet threshold or have date errors')
        report_maker.get_hl7()
    except NoSuchElementException as ne:
        # Log the error traceback
        logging.exception("An error occurred, check Log_info.log: %s", ne)
        input('Check log info...press enter after complete')
    except StaleElementReferenceException as se:
        logging.exception("An error occurred, check Log_info.log: %s", se)
        input('Check log info...press enter after complete')
    except TimeoutException as te:
        logging.exception("An error occurred, check Log_info.log: %s", te)
        input('Check log info...press enter after complete.')
    except SessionNotCreatedException as noSession: 
        logging.exception("Incompatibility with Chromedriver and Chromebrowser: %s", noSession)
    except WebDriverException as sessionIncompatible:
        logging.exception("Incompatibility with Chromedriver and Chromebrowser: %s", sessionIncompatible)
    except pyodbc.Error as e:
        logging.exception('Not a valid path to Microsoft Access file folder. Check VPN connection...just in case %s', e)
    logging.info('Program Complete...')

    return

if __name__=='__main__':
    sys.exit(main())