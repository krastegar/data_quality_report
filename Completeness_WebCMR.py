import sys
import pandas as pd
import numpy as np
from Completeness import Completeness
from WebCMR_check import WebCMR_check
from collections import Counter

def main():

    report_maker = WebCMR_check(
        file_name= 'TST_DIE_04202023_05042023',
        lab_name='Palomar_Pomerado_05042023',
        folder_path= '..\MicrosoftAcessDB',
        test_center_1='Palomar',
        test_center_2='Pomerado',
        username='krastegar',
        paswrd='Hamid&Mahasty2'
    )

    # function calls to generate quality report and error examples 
    report_maker.report_builder()
    report_maker.get_hl7()


    return

if __name__=='__main__':
    sys.exit(main())