# this is for adding the "external" folder to the system path, because the QGIS python is only looking in the system path for python packages
# you can see that this works by doing import sys, sys.path inside the QGIS python console
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "external"))

import openpyxl
import win32com.client
import io
import xlwings as xw


#excel_file = "D:\Users\Raphael\.qgis2\python\plugins\PlanningTool\data\excel_data.xlsm"
excel_file = "/Users/Raphael/.qgis2/python/plugins/PlanningTool/data/excel_data.xlsm"

filename = excel_file


# # save value
sheet = 'INPUT - Infra Projects'
cell = 'P21'
val = 1
# # openpyxl, save new data to file
# srcfile = openpyxl.load_workbook(filename, read_only=False, keep_vba=True)
# sheet_input = srcfile[sheet]  # get sheetname from the file
#
# sheet_input[cell] = val
# # this saves and closes the excel file
# srcfile.save(filename)




# get value
sheet = 'Indicator 1 Accessibility'
cell = 'E2'
# run Excel with win32com.client,
# this needs to be used in combination with, e.g. openpyxl for saving and getting values
xl = win32com.client.Dispatch("Excel.Application")
#xl.Visible = 1
wb = xl.Workbooks.Open(Filename=filename,ReadOnly=1)
ws = wb.Worksheets(sheet)
val = ws.Range(cell).Value
#xl.Application.Run("macrohere")
xl.Workbooks(1).Close(SaveChanges=0)
xl.Application.Quit()
wb=None
ws=None
xl=None


print val


a=5