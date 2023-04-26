import sys
import pyodbc

from Completeness import Completeness

def main():

    # calling Completeness object 
    try: 
        report_maker = Completeness(
            file_name= 'TST_04212023_EISBDisease',
            lab_name='Point Loma Nazarene University Wellness Center',
            folder_path= 'S:\PHS\EPI\EPIRESTRICTED\BEACON\EPI_BEACON_ELR\Point Loma Nazarene University Wellness',
            test_center_1='Point Loma',
            test_center_2='Wellness Medical Center')
        report_maker.completeness_report()
    except pyodbc.Error as e:
        print('Not a valid path. Check VPN connection...just in case')
    return

if __name__=="__main__":
    sys.exit(main())