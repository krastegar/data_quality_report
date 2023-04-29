import sys

from Completeness import Completeness
from WebCMR_check import WebCMR_check

def main():

    report_maker = WebCMR_check(
    file_name= 'TST_DIE_04112023_04192023',
    lab_name='NameForFile',
    folder_path= '..\MicrosoftAcessDB',
    test_center_1='Palomar',
    test_center_2='Pomerado',
    username='krastegar',
    paswrd='Hamid&Mahasty2'
    )
    #report_maker.threshold_search()
    #report_maker.report_builder()
    report_maker.get_hl7()
    return

if __name__=='__main__':
    sys.exit(main())