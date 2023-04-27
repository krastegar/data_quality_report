import sys

from Completeness import Completeness

def main():
    report_maker = Completeness(
        file_name= 'TST_DIE_04112023_04192023',
        lab_name='NameForFile',
        folder_path= '..\MicrosoftAcessDB',
        test_center_1='Palomar',
        test_center_2='Pomerado')
    report_maker.report_builder()
    return

if __name__=='__main__':
    sys.exit(main())