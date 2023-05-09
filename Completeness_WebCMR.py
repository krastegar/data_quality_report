import sys
import logging
from menu import Menu
from WebCMR_check import WebCMR_check


def main():

    # Logging process
    logging.basicConfig(filename='Completeness_Log.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

    # calling my menu object
    menu = Menu()

    logging.info('Getting user input ')
    # getting the inputs for the program
    file_name = menu.get_input("Enter TST Microsoft Access file_name: ", str)
    lab_name = menu.get_input("Enter lab_name: ", str)
    folder_path = menu.get_input("Enter folder_path: ", str, lambda x: menu.is_valid_folder_path(x))
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

    logging.info('Program Complete...')

    return

if __name__=='__main__':
    sys.exit(main())

'''
        file_name= 'TST_DIE_04202023_05042023.accdb',
        lab_name='Palomar_Pomerado_05042023',
        folder_path= '..\MicrosoftAcessDB',
        test_center_1='Palomar',
        test_center_2='Pomerado',
        username='krastegar',
        paswrd='Hamid&Mahasty2'
'''