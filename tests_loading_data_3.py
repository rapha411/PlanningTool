# this is for adding the "external" folder to the system path, because the QGIS python is only looking in the system path for python packages
# you can see that this works by doing import sys, sys.path inside the QGIS python console
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "external"))

import openpyxl
import win32com.client
import io


excel_file = "D:\Users\Raphael\.qgis2\python\plugins\PlanningTool\data\excel_data.xlsm"






# change cell P21 from 0 to 1 (and vice versa), and the value in E2 should change
# P21 = 1 -> E2 = 0.0031
# P21 = 0 -> E2 = 0.0021

input = 'INPUT - Infra Projects'
srcfile = openpyxl.load_workbook(excel_file, read_only=False, keep_vba=True)  # to open the excel sheet and if it has macros
sheet_input = srcfile.get_sheet_by_name(input)  # get sheetname from the file

sheet_input['P21'] = 0
# this saves and closes the excel file
srcfile.save(excel_file)


# run Excel
xl=win32com.client.Dispatch("Excel.Application")
xl.Workbooks.Open(Filename=excel_file,ReadOnly=0)
#xl.Application.Run("macrohere")
xl.Workbooks(1).Close(SaveChanges=1)
xl.Application.Quit()
xl=0


with open(excel_file, "rb") as f:
    in_mem_file = io.BytesIO(f.read())

srcfile = openpyxl.load_workbook(in_mem_file, read_only=False, keep_vba=True, data_only=True)  # to open the excel sheet and if it has macros
output = 'Indicator 1 Accessibility'
sheet_output = srcfile.get_sheet_by_name(output)  # get sheetname from the file

val = sheet_output['E2'].value
print val


a=5