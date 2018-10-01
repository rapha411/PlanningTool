# this is for adding the "external" folder to the system path, because the QGIS python is only looking in the system path for python packages
# you can see that this works by doing import sys, sys.path inside the QGIS python console
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "external"))

import openpyxl
import win32com.client
import io
import xlwings as xw

from datetime import datetime
startTime = datetime.now()




# change cell P21 from 0 to 1 (and vice versa), and the value in E2 should change
# P21 = 1 -> E2 = 0.0031
# P21 = 0 -> E2 = 0.0021




def saveValue(filename, sheet, cell, val):
    # # run Excel with xlwings
    # # this does not work on windows yet, but the only reason is probably that it cannot access the sheet because Excel opens
    # # with a put in Product Key Window. So maybe it is actually better to use win32com.client solution as this seems to work better here

    # app = xw.App(visible=False)  # not necessary
    # book = app.books.open(filename)
    book = xw.Book(filename)
    app = xw.apps.active

    # set new value
    book.sheets[sheet].range(cell).value = val

    book.close()  # Ya puedo cerrar el libro.
    # app.kill()

    # return value
    return 0


def getValue(filename, sheet, cell):
    # # run Excel with xlwings
    # # this does not work on windows yet, but the only reason is probably that it cannot access the sheet because Excel opens
    # # with a put in Product Key Window. So maybe it is actually better to use win32com.client solution as this seems to work better here

    # app = xw.App(visible=False) # not necessary
    # book=app.books.open(excel_file)
    book = xw.Book(filename)
    app = xw.apps.active

    # get new value based on UDF (user defined function)
    val = book.sheets[sheet].range(cell).value

    book.close()  # Ya puedo cerrar el libro.
    # app.kill()

    # return value
    return val




def saveValue2(filename, sheet, cell, val):
    # openpyxl, save new data to file
    srcfile = openpyxl.load_workbook(filename, read_only=False, keep_vba=True)
    sheet_input = srcfile.get_sheet_by_name(sheet)  # get sheetname from the file

    sheet_input[cell] = val
    # this saves and closes the excel file
    srcfile.save(filename)
    return 0

def getValue2(filename, sheet, cell):
    # run Excel with win32com.client,
    # this needs to be used in combination with, e.g. openpyxl for saving and getting values
    xl=win32com.client.Dispatch("Excel.Application")
    xl.Visible = 1
    xl.Workbooks.Open(Filename=filename,ReadOnly=0)
    #xl.Application.Run("macrohere")
    xl.Workbooks(1).Close(SaveChanges=1)
    xl.Application.Quit()
    xl=0

    ## openpyxl, get value
    with open(filename, "rb") as f:
        in_mem_file = io.BytesIO(f.read())
    srcfile = openpyxl.load_workbook(in_mem_file, read_only=True, keep_vba=True, data_only=True)

    #srcfile = openpyxl.load_workbook(filename, read_only=False, keep_vba=True, data_only=True)
    sheet_output = srcfile.get_sheet_by_name(sheet)  # get sheetname from the file
    val = sheet_output[cell].value
    #srcfile.save(filename)

    return val



excel_file = "D:\Users\Raphael\.qgis2\python\plugins\PlanningTool\data\excel_data.xlsm"
#excel_file = "/Users/Raphael/.qgis2/python/plugins/PlanningTool/data/excel_data.xlsm"

sheet_input = 'INPUT - Infra Projects'
cell_input = 'P21'
val = 0
saveValue2(excel_file, sheet_input, cell_input, val)


sheet_output = 'Indicator 1 Accessibility'
cell_output = 'E2'
print getValue2(excel_file, sheet_output, cell_output)







# timing
print datetime.now() - startTime

a=5