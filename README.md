
# ELR Analysis Program
## Purpose
The ELR Analysis Program is designed to analyze the range export of ELR's in the TST environment. It determines the completeness of each specified field seen in the TST environment. After calculating the completions, it looks at the cross-tabulation of data for each column and their unique 'index's'. It then generates a report card in the form of an Excel workbook with multiple sheets.

The second part of the program is meant to look at the completeness scores for the specified fields and searches for HL7 examples on TST environment in WebCMR Incoming Message Monitor that do not have those specified fields filled out in their HL7 messages. It populates those examples in a Word document called hl7_error.docx. The program achieves this by utilizing Selenium WebDriver to navigate and extract data from the WebCMR Incoming Message Monitor.

## Algorithm
The program follows the following algorithm:

### 1. Calculate Completion Scores:

    Calculates completion scores for the specified fields of interest.
### 2. Search for HL7 Messages:

    Performs searches for HL7 messages that are part of the specified fields but do not meet the threshold criteria.
### 3. Handle Error'd HL7 Messages:

    Takes the first instance of the error'd HL7 messages and puts them under a header for that field error.
### 4. Generate Report Card:

    Prints the error'd HL7 messages as an example on a Word document.
### 5. Search for Missing Fields in WebCMR:

    Searches for HL7 examples in WebCMR Incoming Message Monitor that do not have specified fields filled out.
### 6. Populate hl7_error.docx:

    Populates examples of missing fields in a Word document named hl7_error.docx.
## Updates on Input / Usage
### HL7 Error Examples:

    The HL7_error examples come from a threshold of missing values. Refer to the threshold template discussed with Marjorie Richardson about completeness percentages allowed to be below 100%.
## Folder Structure:

    Have a separate folder that contains only the .accdb (range export file) in question. There are no date range variables in this program.
### Test Centers Variable:

    The TestCenters variable performs a regex operation on the HL7_filename column in Microsoft Access files. It looks for the lab name or testing center in the HL7 file name.
### Completeness_WebCMR.py:

    Completeness_WebCMR.py is the Python script that contains the main function.
## Usage
### 1. Installation:

    Ensure you have the required Python libraries installed. You can install them using pip install -r requirements.txt.
### 2. Folder Structure:

    Create a folder structure as described above.
### 3. Configuration:

    Open Completeness_WebCMR.exe and input the required configuration parameters.

### 4. Execution:

    Run Completeness_WebCMR.exe

## Troubleshooting
    If you encounter issues with the program, consider the following steps:

### 1. Python Environment:

    Ensure you are using the correct Python environment with the required dependencies.
### 2. Folder Permissions:

    Ensure the program has permission to read and write files in the specified directory.
### 3. File Existence:

    Double-check that the necessary files (.accdb, PROD, and TST IMM exports) are present in the designated folder.
### 4. Test Center Recognition:

    Verify that the TestCenters variable is correctly identifying the lab name or testing center in the HL7 file names.
### 5. Error Threshold:

    Confirm that the error threshold is set appropriately based on the discussed completeness percentages.

### 6. ChromeDriver Compatibility:
        Ensure the chromedriver in the script folder matches your Chrome version.
        Replace the chromedriver with a compatible version if needed.
    Can be located at this website: 
    Chrome for Testing availability (googlechromelabs.github.io)
