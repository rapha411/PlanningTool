# this is for adding the "external" folder to the system path, because the QGIS python is only looking in the system path for python packages
# you can see that this works by doing import sys, sys.path inside the QGIS python console
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "external"))

import openpyxl
#import win32com.client
import io
import xlwings as xw

from datetime import datetime
startTime = datetime.now()




# change cell P21 from 0 to 1 (and vice versa), and the value in E2 should change
# P21 = 1 -> E2 = 0.0021
# P21 = 0 -> E2 = 0.0011




def saveValue(app, filename, sheet, cells, vals):
    # # run Excel with xlwings
    # # this does not work on windows yet, but the only reason is probably that it cannot access the sheet because Excel opens
    # # with a put in Product Key Window. So maybe it is actually better to use win32com.client solution as this seems to work better here

    #app = xw.App(visible=False)  # not necessary
    book = app.books.open(filename)
    # book = xw.Book(filename)
    # app = xw.apps.active

    # set new value
    for i,cell in enumerate(cells):
        book.sheets[sheet].range(cell).value = val[i]
    book.save()
    # book.close()  # Ya puedo cerrar el libro.
    # # app.kill()

    # return value
    return 0


def getValue(app, filename, sheet, cells):
    # # run Excel with xlwings
    # # this does not work on windows yet, but the only reason is probably that it cannot access the sheet because Excel opens
    # # with a put in Product Key Window. So maybe it is actually better to use win32com.client solution as this seems to work better here

    # app = xw.App(visible=False)  # not necessary
    book = app.books.open(filename)
    # book = xw.Book(filename)
    # app = xw.apps.active


    # get new value based on UDF (user defined function)
    vals = []
    for cell in cells:
        vals.append(book.sheets[sheet].range(cell).value)

    book.close()
    # app.kill()

    # return value
    return vals




def saveValue2(filename, sheet, cells, vals):
    # openpyxl, save new data to file
    srcfile = openpyxl.load_workbook(filename, read_only=False, keep_vba=True)
    sheet_input = srcfile[sheet]  # get sheetname from the file

    for i,cell in enumerate(cells):
        sheet_input[cell] = vals[i]
    # this saves and closes the excel file
    srcfile.save(filename)
    return 0


# def getValue2(filename, sheet, cells):
#     # run Excel with win32com.client,
#     # this needs to be used in combination with, e.g. openpyxl for saving and getting values
#     xl = win32com.client.Dispatch("Excel.Application")
#     #xl.Visible = 1
#     wb = xl.Workbooks.Open(Filename=filename,ReadOnly=1)
#     ws = wb.Worksheets(sheet)
#     vals = []
#     for cell in cells:
#         vals.append(ws.Range(cell).Value)
#     #xl.Application.Run("macrohere")
#     xl.Workbooks(1).Close(SaveChanges=0)
#     xl.Application.Quit()
#     wb=None
#     ws=None
#     xl=None
#
#     return vals



#excel_file = "D:\Users\Raphael\.qgis2\python\plugins\PlanningTool\data\excel_data.xlsm"
excel_file = "/Users/Raphael/.qgis2/python/plugins/PlanningTool/data/excel_data.xlsm"

app = xw.App(visible=False)  # not necessary
#book = app.books.open(excel_file)

sheet_input = 'INPUT - Infra Projects'
cell_input = ['P21']
val = [0]
saveValue2(excel_file, sheet_input, cell_input, val)


sheet_output = 'Indicator 1 Accessibility'
cell_output = ['E2']
# get value is now done with xlwings,
# because openpyxl obviously doesn't refresh data, and win32com doesn't work on OSX
print getValue(app, excel_file, sheet_output, cell_output)





# timing
print datetime.now() - startTime

app.kill()

# # run this if excel doesn't open
# app = xw.apps.active
# app.kill()


a=5