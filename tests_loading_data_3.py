import win32com.client
xl=win32com.client.Dispatch("Excel.Application")
xl.Workbooks.Open(Filename="D:\Users\Raphael\.qgis2\python\plugins\PlanningTool\data\excel_data.xlsm",ReadOnly=0)
#xl.Application.Run("macrohere")
xl.Workbooks(1).Close(SaveChanges=1)
xl.Application.Quit()
xl=0




# change cell P21 from 0 to 1 (and vice versa), and the value in E2 should change
# P21 = 1 -> E2 = 0.0031
# P21 = 0 -> E2 = 0.0021
