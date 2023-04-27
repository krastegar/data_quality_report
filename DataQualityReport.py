import sys
import pyodbc
import time

from Completeness import Completeness

def main():

    # calling Completeness object 
    try: 
        report_maker = Completeness(
            file_name= 'TST_DIE_04112023_04192023',
            lab_name='Point Loma Nazarene University Wellness Center',
            folder_path= '..\MicrosoftAcessDB',
            test_center_1='Point Loma',
            test_center_2='Wellness Medical Center')
        report_maker.completeness_report()
    except pyodbc.Error as e:
        print('Not a valid path. Check VPN connection...just in case')
        time.sleep(2)
    _ = None
    return

if __name__=="__main__":
    sys.exit(main())