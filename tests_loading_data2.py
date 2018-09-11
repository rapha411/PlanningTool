import os
import pandas as pd
import openpyxl
import xlrd
import xlwt
import numpy as np


excel_file = os.path.join(os.path.dirname(__file__), 'data', 'excel_data.xlsm')
sheet_name = 'INPUT - Infra Projects'
cell = 'P3'



def getValue(filepath=None, sheetname=None, col=None, row_start=0, row_end=1):
    excel_file = openpyxl.load_workbook(filepath,read_only=True, keep_vba=True) # to open the excel sheet and if it has macros
    sheet = excel_file.get_sheet_by_name(sheetname)
    data=[]
    for i in range(row_start,row_end+1):
        val = float(sheet[col+str(i)].value)
        data.append(val)
    return np.array(data)

## Transit accesibility
c=[]
af = getValue(filepath=excel_file, sheetname=sheet_name, col='AF', row_start=3, row_end=40)
aj = getValue(filepath=excel_file, sheetname=sheet_name, col='AJ', row_start=3, row_end=40)
ak = aj*0.01
p = getValue(filepath=excel_file, sheetname=sheet_name, col='P', row_start=3, row_end=40)
ar = p*af*ak
c.append(sum(ar))
#c4
ag = getValue(filepath=excel_file, sheetname=sheet_name, col='AG', row_start=3, row_end=40)
as1 = p*ag*ak
c.append(sum(as1))
#c5
ah = getValue(filepath=excel_file, sheetname=sheet_name, col='AH', row_start=3, row_end=40)
at = p*ah*ak
c.append(sum(at))
#c6
ai = getValue(filepath=excel_file, sheetname=sheet_name, col='AI', row_start=3, row_end=40)
au = p*ai*ak
c.append(sum(au))
#c7
c7=np.mean(c)


## Car accesibility
d=[]
#d3
aa = getValue(filepath=excel_file, sheetname=sheet_name, col='AA', row_start=3, row_end=40)
aj = getValue(filepath=excel_file, sheetname=sheet_name, col='AJ', row_start=3, row_end=40)
ak = aj*0.01
p = getValue(filepath=excel_file, sheetname=sheet_name, col='P', row_start=3, row_end=40)
aw = p*aa*ak
d.append(sum(aw))
#d4
ab = getValue(filepath=excel_file, sheetname=sheet_name, col='AB', row_start=3, row_end=40)
ax = p*ab*ak
d.append(sum(ax))
#d5
ac = getValue(filepath=excel_file, sheetname=sheet_name, col='AC', row_start=3, row_end=40)
ay = p*ac*ak
d.append(sum(ay))
#d6
ad = getValue(filepath=excel_file, sheetname=sheet_name, col='AD', row_start=3, row_end=40)
az = p*ad*ak
d.append(sum(az))
#c7
d7=np.mean(d)

cd = np.add(c,d)
accesibility = np.append(cd,np.mean(cd))

print accesibility

####

srcfile = openpyxl.load_workbook(excel_file, read_only=False,keep_vba=True)  # to open the excel sheet and if it has macros
sheet = srcfile.get_sheet_by_name(sheet_name)  # get sheetname from the file

sheet['Q15'] = 0.8 # write to row 1,col 1 explicitly, this type of writing is useful to write something in loops

srcfile.save(excel_file)  # save it to srcfile






a = 5