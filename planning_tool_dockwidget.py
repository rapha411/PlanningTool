# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanningToolClassDockWidget
                                 A QGIS plugin
 The Storm Help plugin provides help in case of a storm
                             -------------------
        begin                : 2017-01-07
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Raphael Sulzer
        email                : raphaelsulzer@gmx.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


from PyQt4 import QtGui, QtCore, uic

from qgis.core import *
from qgis.gui import *
from qgis.gui import QgsMapTool
from qgis.networkanalysis import *

from PyQt4.QtCore import Qt, pyqtSignal, QPoint

from . import utility_functions as uf

# this is for adding the "external" folder to the system path, because the QGIS python is only looking in the system path for python packages
# you can see that this works by doing import sys, sys.path inside the QGIS python console
import os, sys
#sys.path.append(os.path.join(os.path.dirname(__file__), "external"))
#sys.path.append("/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/aeosa")


import numpy as np

# matplotlib for the charts
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure




FORM_BASE, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PlanningTool_dockwidget_base_3.ui'))


################################################################################################################
###################################################### PLUGIN WIDGET ###########################################
################################################################################################################
class IndicatorsChartDocked(QtGui.QDockWidget, FORM_BASE, QgsMapTool):

    closingPlugin = pyqtSignal()
    # canvasDoubleClicked = pyqtSignal(object, object)

    def __init__(self, iface, parent=None, book=None):

        super(IndicatorsChartDocked, self).__init__(parent)

        # initialisation
        self.setupUi(self)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.book = book

        # define row height for tables and comboBox here
        self.height = 24
        self.barHeight = 0.25

        # TODO: what should maybe be done is to implement my own data structure from the layer
        # and excel data, e.g. a pandas table, and use that for loading and saving data.
        # When the plugin is closed or changes are saved with saving button then this data structure is pushed to the
        # layers and excel sheet. This also means that the OK button only saves in my own data structure, and the
        # populate table function gets its values from that.

        # load project file
        self.loadProjectFile()

        self.infraLayer = uf.getCanvasLayerByName(self.canvas, "Infrastructure Projects")
        self.housingLayer = uf.getCanvasLayerByName(self.canvas, "Housing Plans")

        # populate box and table
        #self.populateComboBox()
        self.populateTablePackage()
        self.packageSelected()


        # connect signal/slot
        # table
        self.housingTable.cellClicked.connect(self.housingRowSelected)
        self.infraTable.cellClicked.connect(self.infraRowSelected)
        # comboBox
        #self.packageComboBox.currentIndexChanged.connect(self.packageSelected)
        self.packageTable.cellClicked.connect(self.packageSelected)
        # layers
        self.infraLayer.selectionChanged.connect(self.infraLayerSelectionChanged)
        self.housingLayer.selectionChanged.connect(self.housingLayerSelectionChanged)
        # sliders
        self.housingSlider.valueChanged.connect(self.housingSliderChanged)

        # maptool changed
        #self.currentMapTool = self.canvas.mapTool()
        #self.currentMapTool.canvasDoubleClickEvent = self.testExe
        #self.canvas.mapToolSet.connect(self.testExe)

        # toolBox
        #self.toolBox.currentChanged.connect(self.plot)
        self.plot()


        # buttons
        # signal slots for buttons should simly save all the current percentages to the excel sheet and then update the plot
        # in this way the plot is only update from the OK button and not from moving the slider, which obviously would be terrible
        #self.okHousing.clicked.connect(self.saveHousingTableData)
        self.okInfra.clicked.connect(self.saveData)



        # description text
        self.descriptionText.setFontPointSize(10)
        self.descriptionText.viewport().setAutoFillBackground(False)




    ############################################################
    ################## SLIDERS #################################
    ############################################################
    def housingSliderChanged(self):
        #print self.housingSlider.value()
        if self.housingTable.selectedItems():
            # set current slider value in the housing table (works dynamic)
            row = self.housingTable.currentRow()
            # slider value returns an integer, so convert it to a float, divide by 10, round, and multiply by 10
            val10 = int(round(float(self.housingSlider.value())/10)*10)
            percentItem = QtGui.QTableWidgetItem(str(val10))
            percentItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.housingTable.setItem(row, 5, percentItem)
            #self.housingTable.setItem(row, 1, QtGui.QTableWidgetItem(str(self.housingSlider.value())))

        #TODO put the value in a numpy array with ID same as project ID, save it as self.housingPercentage, and push it to excel when data is saved

    ############################################################
    ################## COMBOBOX ################################
    ############################################################
    def populateTablePackage(self):

        table = self.packageTable
        table.clear()
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(['Package'])
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setRowCount(6)
        table.setItem(0,0,QtGui.QTableWidgetItem("All Packages"))
        table.setItem(0,1,QtGui.QTableWidgetItem("Package 1 - Noordoever Noordzeekanaal"))
        table.setItem(0,2,QtGui.QTableWidgetItem("Package 2 - Zaandam - Noord"))
        table.setItem(0,3,QtGui.QTableWidgetItem("Package 3 - Purmerend: BBG of A7"))
        table.setItem(0,4,QtGui.QTableWidgetItem("Package 4 - Hoorn"))
        table.setItem(0,5,QtGui.QTableWidgetItem("Package 5 - Ring A10 oost - Waterland"))
        table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)

        # select the "All Packages" row
        table.selectRow(0)
        table.verticalHeader().setDefaultSectionSize(self.height)




    def testExe(self, event1, event2):
        print("here")



    def packageSelected(self):

        #package = self.packageComboBox.currentIndex()
        package = self.packageTable.currentRow()

        ## if "all packages" selected
        if package == 0:
            #populate table with all packages
            expressionHousing = "Package IS 'p1' or Package IS 'p2' or Package IS 'p3' or Package IS 'p4' or Package IS 'p5'"
            expressionInfra = "Package IS 'P1' or Package IS 'P2' or Package IS 'P3' or Package IS 'P4' or Package IS 'P5'"
        else:
            expressionHousing = "Package IS " + "'p"+str(package)+"'"
            expressionInfra = "Package IS " + "'P"+str(package)+"'"

        ### HOUSING ###
        # request only projects within the selected package
        request = QgsFeatureRequest().setFilterExpression(expressionHousing)
        housingFeatureIterator = self.housingLayer.getFeatures(request)
        # get the feature name and ID for the first feature
        feat = QgsFeature()
        housingFeatureIterator.nextFeature(feat)
        housingBox = feat.geometry().boundingBox()
        housingNames = [feat.attribute('NameShort')]
        housingID = [feat.id()]
        # get the feature name and ID for the rest
        while housingFeatureIterator.nextFeature(feat):
            housingBox.combineExtentWith(feat.geometry().boundingBox())
            housingNames.append(feat.attribute('NameShort'))
            housingID.append(feat.id())

        ### INFRA ###
        request = QgsFeatureRequest().setFilterExpression(expressionInfra)
        infraFeatureIterator = self.infraLayer.getFeatures(request)
        feat = QgsFeature()
        infraFeatureIterator.nextFeature(feat)
        infraBox = feat.geometry().boundingBox()
        infraNames = [feat.attribute('ShortName')]
        # get the feature name and ID for the rest
        infraID = [feat.id()]
        while infraFeatureIterator.nextFeature(feat):
            infraBox.combineExtentWith(feat.geometry().boundingBox())
            infraNames.append(feat.attribute('ShortName'))
            infraID.append(feat.id())

        # print housingID
        # print infraID

        # populate the tables
        self.populateTableHousing(shortName=housingNames, id=housingID)
        self.populateTableInfra(shortName=infraNames, id=infraID)


        # zoom to package - bookmarks
        if package == 0:
            extent = self.infraLayer.extent()
            #extent = QgsRectangle(105719,486317,148566,526584)
        if package == 1:
            extent = QgsRectangle(114177,490653,122483,497105)
        elif package == 2:
            extent = QgsRectangle(107662,494165,120349,504020)
        elif package == 3:
            #extent = QgsRectangle(118401,496246,129810,505108)
            extent = QgsRectangle(118370,490064,131057,505361)
        elif package == 4:
            extent = QgsRectangle(124656,510813,139329,522787)
        elif package == 5:
            extent = QgsRectangle(122776, 489456, 138727, 504447)

        self.canvas.setExtent(extent)
        self.canvas.refresh()


    ############################################################
    ################## TABLE ###################################
    ############################################################
    ### populate housing table ###
    def populateTableHousing(self, shortName=None, id=None):

        # get cell string for Rent percent data column
        cellList1 = self.getCellString(data=id, column='K', skip=3)
        cellList2 = self.getCellString(data=id, column='J', skip=3)
        # BBG
        cellList3 = self.getCellString(data=id, column='D', skip=3)
        # TOD
        cellList4 = self.getCellString(data=id, column='F', skip=3)

        # get percent values from excel sheet
        BBG = self.getValue_xlwings(book=self.book, sheet='BASIS - Accessiblity of plans', cells=cellList3)
        TOD = self.getValue_xlwings(book=self.book, sheet='BASIS - Accessiblity of plans', cells=cellList4)
        percents = self.getValue_xlwings(book=self.book, sheet='INPUT - Housing per plan ', cells=cellList1)
        maxAmount = self.getValue_xlwings(book=self.book, sheet='INPUT - Housing per plan ', cells=cellList2)

        table = self.housingTable
        table.clear()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['ID','Housing Plan', "BBG", "TOD", "MAX", "%"])
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        #table.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        table.setRowCount(len(shortName))
        # i is the table row, items mus tbe added as QTableWidgetItems
        for i, att in enumerate(shortName):
            # hidden excel id column (necessary for saving data to the excel file)
            idItem = QtGui.QTableWidgetItem(str(id[i]+1))
            #idItem.setBackground(QtGui.QColor("grey"))
            idItem.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            #table.setItem(i,0,QtGui.QTableWidgetItem(str(id[i]+1)))
            table.setItem(i,0,idItem)

            # set the short name in the table
            table.setItem(i,1,QtGui.QTableWidgetItem(att))

            # BBG
            if int(BBG[i]) == 0:
                bbgItem = QtGui.QTableWidgetItem('BBG')
            else:
                bbgItem = QtGui.QTableWidgetItem('not')
            bbgItem.setTextAlignment(QtCore.Qt.AlignCenter)
            table.setItem(i, 2, bbgItem)


            # TOD
            if int(TOD[i]) == 0:
                todItem = QtGui.QTableWidgetItem('TOD')
            else:
                todItem = QtGui.QTableWidgetItem('not')
            todItem.setTextAlignment(QtCore.Qt.AlignCenter)
            table.setItem(i, 3, todItem)


            # set the maxAmount value from the excel data in the table
            maxAmountItem = QtGui.QTableWidgetItem(str(int(maxAmount[i])))
            maxAmountItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            table.setItem(i, 4, maxAmountItem)

            # set the maxAmount value from the excel data in the table
            percentItem = QtGui.QTableWidgetItem(str(int(percents[i])))
            percentItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            table.setItem(i, 5, percentItem)

        table.setStyleSheet("QTableWidget::item { padding: 3px}")

        # horizontal
        table.hideColumn(0)
        #table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        table.horizontalHeader().setResizeMode(1,QtGui.QHeaderView.ResizeToContents)

        table.horizontalHeader().setSizePolicy(1,QtGui.QSizePolicy.MinimumExpanding)
        table.horizontalHeader().setSizePolicy(2,QtGui.QSizePolicy.MinimumExpanding)
        table.horizontalHeader().setSizePolicy(3,QtGui.QSizePolicy.MinimumExpanding)
        table.horizontalHeader().setSizePolicy(4,QtGui.QSizePolicy.MinimumExpanding)
        table.horizontalHeader().setSizePolicy(5,QtGui.QSizePolicy.MinimumExpanding)

        # vertical
        table.resizeRowsToContents()
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(self.height)




    ### populate infra table ###
    def populateTableInfra(self, shortName=None, id=None):


        cellList = self.getCellString(data=id, column='R', skip=3)

        checkBoxValues = self.getValue_xlwings(book=self.book, sheet='INPUT - Infra Projects', cells=cellList)


        table = self.infraTable
        table.clear()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['ID','y/n', 'Infrastructure Project'])
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        #table.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        table.setRowCount(len(shortName))
        # i is the table row, items mus tbe added as QTableWidgetItems
        # TODO: here is need to get the previous value of this row, instead of just setting it to a constant value
        for i, att in enumerate(shortName):
            # hidden excel id column (necessary for saving data to the excel file)
            table.setItem(i, 0, QtGui.QTableWidgetItem(str(id[i]+1)))

            #### checkbox y/n per project
            # setup chechbox so it can be used as qtablewidgetitem
            checkBoxWidget = QtGui.QWidget()
            checkBox = QtGui.QCheckBox()
            layoutCheckBox = QtGui.QHBoxLayout(checkBoxWidget)
            layoutCheckBox.addWidget(checkBox)
            layoutCheckBox.setAlignment(QtCore.Qt.AlignCenter)
            layoutCheckBox.setContentsMargins(0,0,0,0)
            # get value for checkbox from the excel data
            if int(checkBoxValues[i]) == 1:
                checkBox.setChecked(True)
            else:
                checkBox.setChecked(False)
            # insert checkbox in the table
            table.setCellWidget(i,1,checkBoxWidget)

            #### short name of the project
            table.setItem(i,2,QtGui.QTableWidgetItem(att))

        table.setStyleSheet("QTableWidget::item { padding: 3px}")

        table.hideColumn(0)

        # horizontal
        table.setColumnWidth(1, 40)
        table.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
        #table.horizontalHeader().setResizeMode(1,QtGui.QHeaderView.ResizeToContents)

        table.horizontalHeader().setSizePolicy(1,QtGui.QSizePolicy.MinimumExpanding)
        table.horizontalHeader().setSizePolicy(2,QtGui.QSizePolicy.MinimumExpanding)

        # #table.setColumnWidth(0, 28)                                                     # id column
        # #table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.MinimumExpanding)
        # table.horizontalHeader().setSizePolicy(1,QtGui.QSizePolicy.MinimumExpanding)
        # table.setColumnWidth(2, 50)                                                     # checkbox column
        # table.horizontalHeader().setSizePolicy(1,QtGui.QSizePolicy.MinimumExpanding)
        # table.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)            # name column

        # vertical
        table.resizeRowsToContents()
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(self.height)


    ### get table data ###
    def saveData(self):
        self.saveHousingTableData()
        self.saveInfraTableData()
        self.plot()



    # housing
    def saveHousingTableData(self):


        # get data from table
        nRows = self.housingTable.rowCount()
        id = []
        data = []
        for i in range(nRows):
            # housing percent value
            data.append(int(self.housingTable.item(i, 5).text()))
            # id column
            id.append(int(self.housingTable.item(i,0).text()))

        #print "housing percent: ", data
        #print "hidden housing table id: ", id

        # save data to excel sheet
        cellList = self.getCellString(data=id, column='K', skip=2)
        sheet = 'INPUT - Housing per plan '
        self.saveValue_xlwings(book=self.book, sheet=sheet, cells=cellList, vals=data)

        # refresh accInput
        #self.accInputPlot()


    # infra
    def saveInfraTableData(self):


        # get data from table
        nRows = self.infraTable.rowCount()
        id = []
        data = []
        for i in range(nRows):
            # checkbox value
            checked = self.infraTable.cellWidget(i, 1).findChild(QtGui.QCheckBox).isChecked()
            #print checked
            #data.append(checked)
            if checked:
                data.append(1)
            else:
                data.append(0)

            # id column
            id.append(int(self.infraTable.item(i,0).text()))

        #print "checkbox value: ", data
        #print "hidden infra table id: ", id

        # save data to excel sheet
        cellList = self.getCellString(data=id, column='R', skip=2)

        sheet = 'INPUT - Infra Projects'
        self.saveValue_xlwings(book=self.book, sheet=sheet, cells=cellList, vals=data)

        # refresh accInput
        #self.accInputPlot()




    ############################################################
    ############ LAYER OR TABLE SELECTION CHANGED ##############
    ############################################################
    ### table selection changed ###
    # housing
    def housingRowSelected(self):

        # get the name of the selected item from the table
        selectedItem = self.housingTable.selectedItems()[0].text().encode('utf-8')
        self.housingLayer.removeSelection()
        uf.selectFeaturesByExpression(self.housingLayer, "NameShort IS " + "'"+selectedItem+"'")
        self.zoomToSelectedFeature(scale=1.3, layer=self.housingLayer)
        #self.housingLabel.setText(selectedItem)

    # infra
    def infraRowSelected(self):

        # get the name of the selected item from the table
        selectedItem = self.infraTable.selectedItems()[0].text().encode('utf-8')
        self.infraLayer.removeSelection()
        uf.selectFeaturesByExpression(self.infraLayer, "ShortName IS " + "'"+selectedItem+"'")
        if selectedItem == "HOV Purmerend-Adam":
            extent = QgsRectangle(118370,490064,131057,505361)
            self.canvas.setExtent(extent)
            self.canvas.refresh()
        else:
            self.zoomToSelectedFeature(scale=1.3, layer=self.infraLayer)
        #self.infraLabel.setText(selectedItem)

    ### layer selection changed ###
    # housing
    def housingLayerSelectionChanged(self):
        ## this is called if user changes the project selection on the canvas


        self.housingTable.blockSignals(True)

        ## check if it wasn't just a double click, in which case clear the selected tableWidgetItem
        feat = self.housingLayer.selectedFeatures()
        if feat:
            feat = feat[0]
        else:
            self.housingTable.clearSelection()
            self.housingTable.blockSignals(False)
            return

        ## check if package changed
        packageMap = int(feat.attribute("Package")[1])
        #packageTable = self.packageComboBox.currentIndex()
        packageTable = self.packageTable.currentRow()
        if packageMap != packageTable and packageTable != 0:
                #self.packageComboBox.setCurrentIndex(packageMap)
                self.packageTable.selectRow(packageMap)
                self.packageSelected()

        # TODO: in the following function is where the Max. total amount label should also be updated
        ## select the corresponding row of the project and update the label above sliders
        rowCount = self.housingTable.rowCount()
        # iterate over all table rows and check where the name corresponds to the currently selected feature
        for i in range(rowCount):
            # get name from table
            tableFeatureName = self.housingTable.item(i, 1).text()
            layerFeatureName = feat.attribute("NameShort")
            if tableFeatureName == layerFeatureName:
                # select/highlight matching row
                self.housingTable.selectRow(i)
                # update the label above the sliders
                #self.housingLabel.setText(tableName)
                # update the slider position
                self.housingSlider.setValue(int(self.housingTable.item(i,5).text()))
                break

        self.housingTable.blockSignals(False)

    # infra
    def infraLayerSelectionChanged(self):
        ## this is called if user changes the project selection on the canvas

        self.infraTable.blockSignals(True)

        ## check if it wasn't just a double click, in which case clear the selected tableWidgetItem
        feat = self.infraLayer.selectedFeatures()
        if feat:
            feat = feat[0]
        else:
            self.infraTable.clearSelection()
            self.infraTable.blockSignals(False)
            return

        ## check if package changed
        packageMap = int(feat.attribute("Package")[1])
        #packageTable = self.packageComboBox.currentIndex()
        packageTable = self.packageTable.currentRow()
        if packageMap != packageTable and packageTable != 0:
                #self.packageComboBox.setCurrentIndex(packageMap)
                self.packageTable.selectRow(packageMap)
                self.packageSelected()

        ## select the corresponding row of the project and update the label above sliders
        rowCount = self.infraTable.rowCount()
        # iterate over all table rows and check where the name corresponds to the currently selected feature
        for i in range(rowCount):
            # get name from table, ATTENTION FOR THE COLUMN ID HERE; APPARENTLY IF YOU CALL WITH .item(row,column), the hidden column is still regarded
            tableFeatureName = self.infraTable.item(i, 2).text()
            layerFeatureName = feat.attribute("ShortName")
            if tableFeatureName == layerFeatureName:
                # select/highlight matching row
                self.infraTable.selectRow(i)
                # update the label above the sliders
                #self.infraLabel.setText(tableFeatureName)
                # update the infra project description
                self.descriptionText.setText(feat.attribute("Descriptio"))
                break

        #self.infraTable.selectRow(4)

        self.infraTable.blockSignals(False)

    ############################################################
    ################## CANVAS ##################################
    ############################################################
    def loadProjectFile(self):

        # open the QGIS project file
        scenario_open = False
        scenario_file = os.path.join(os.path.dirname(__file__),'data', 'project_file','RegionalGamesIII_5.qgs')


        # check if file exists
        if os.path.isfile(scenario_file):
            self.iface.addProject(scenario_file)
            scenario_open = True
        else:
            last_dir = uf.getLastDir("PlanningToolClass")
            new_file = QtGui.QFileDialog.getOpenFileName(self, "", last_dir, "(*.qgs)")
            if new_file:
                self.iface.addProject(unicode(new_file))
                scenario_open = True


    def zoomToSelectedFeature(self, scale, layer):

        box = layer.boundingBoxOfSelected()
        box.scale(scale)
        self.canvas.setExtent(box)
        #self.canvas.zoomScale(50000)
        self.canvas.refresh()

    ############################################################
    ################## EXCEL ###################################
    ############################################################
    def getCellString(self, data=None, column=None, skip=None):
        ### get feature cells
        # feautreID + 3 = excel row
        data = np.asarray(data) + skip
        cellList = []
        for row in data:
            cellList.append(column+str(row))

        return cellList



    def getValue_xlwings(self, book, sheet, cells):
        # # # run Excel with xlwings
        # # # this does not work on windows yet, but the only reason is probably that it cannot access the sheet because Excel opens
        # # # with a put in Product Key Window. So maybe it is actually better to use win32com.client solution as this seems to work better here
        #
        # app = xw.App(visible=False)
        # book = app.books.open(filename)
        # #book = xw.Book(filename)
        # #app = xw.apps.active
        # app.visible = False

        ##get new value based on UDF (user defined function)
        vals = []
        for cell in cells:
            val = book.sheets[sheet].range(cell).value
            # sometimes there are strange values coming from the excel formulas, e.g. very close to zero. So filter them:
            if ((val < 0.01) and (val > -0.01)):
                val = 0
            vals.append(val)

        # book.close()
        # app.kill()

        # return value
        return np.asarray(vals)
        #return [-1035, -1907, -3106, -7902, -3487]

    def saveValue_xlwings(self, book, sheet, cells, vals):

        # set new value
        for i, cell in enumerate(cells):
            book.sheets[sheet].range(cell).value = vals[i]
        book.save()
        # book.close()  # Ya puedo cerrar el libro.
        # # app.kill()

        # return value
        return 0


    ###########################################################
    ################## PLOT ###################################
    ###########################################################
    def plot(self):

        #if self.toolBox.currentIndex() == 1:
            # generate the plots
        self.accPlot()
        self.marketPlot()
        self.financialPlot()
        self.spatialPlot()
        #else:
            #pass



    def accPlot(self):
        ### INDICATORS

        ### PLOT
        ## first clear the Figure() from the accessibilityInputChart layout,
        ## so a new one will be printed when function is run several times
        for i in reversed(range(self.accessibilityChart.count())):
            self.accessibilityChart.itemAt(i).widget().setParent(None)

        # add matplotlib Figure to chartFrame / accessibilityInputChart layout
        figure = Figure(figsize=(1,1), tight_layout=True)
        #figure.suptitle("Accessibility", fontsize=12)
        figureCanvas = FigureCanvas(figure)
        self.accessibilityChart.addWidget(figureCanvas)
        figure.patch.set_alpha(0.0)
        ax = figure.add_subplot(111)


        # get values from excel sheets
        sheet = 'Indicator 1 Accessibility'
        # data for package 1 to 5
        # car
        data1 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['C10','C11','C12','C13','C14'])
        # public transport
        data2 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['D10','D11','D12','D13','D14'])
        # bike
        data3 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['E10','E11','E12','E13','E14'])
        #data3 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['E10','E11','E12','E13','E14'])
        # data for all packages; car, bike, public transport
        data4 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['C18','D18','E18'])
        # add all packages to the plot data
        data1=np.append(data1, data4[0])
        data2=np.append(data2, data4[1])
        data3=np.append(data3, data4[2])



        labels = ('1', '2', '3', '4', '5', 'All')



        y_pos = np.arange(len(data1))
        width = self.barHeight

        a=ax.barh(y_pos-width, data1, width, color='blue', ecolor='black')
        b=ax.barh(y_pos, data2, width, color='red', ecolor='black')
        c=ax.barh(y_pos+width, data3, width, color='green', ecolor='black')

        # label
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=7)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_ylabel('Package', fontsize=7)
        #ax.set_xticks([-100,-80,-60,-40,-20,0,20,40,60,80,100])
        ax.set_xticks([0,20,40,60,80,100])
        ax.xaxis.set_tick_params(labelsize=7)
        ax.set_xlabel('[%]', fontsize=7)
        ax.xaxis.set_label_coords(1, -0.025)

        # legend
        figure.legend((a[0], b[0], c[0]), ('Car', 'Public Transport', 'Bicycle'), bbox_to_anchor=(0.5, 1.01), loc='upper center', ncol=3, prop={'size': 7})
        #figure.tight_layout(rect=[0,0.03,1,0.95])
        #ax.legend((a[0], b[0], c[0]), ('Car', 'Public \n Transport', 'Bicycle'), loc='lower right', prop={'size': 7})

        # set the xlims
        # xlims = ax.get_xlim()
        # ax.set_xlim(xlims[0]*1.2, xlims[1]*1.2)
        xlims = ax.get_xlim()
        if (xlims[0]<0) and (xlims[1]>0):
            m = max(abs(np.array(xlims)))
            ax.set_xlim(-m*1.5, m*1.5)
        else:
            ax.set_xlim(xlims[0]*1.2, xlims[1]*1.2)
        # annotate bars
        self.labelBars(ax, data1, -width)
        self.labelBars(ax, data2, 0)
        self.labelBars(ax, data3, width)

        return


    def marketPlot(self):
        ### INDICATORS

        ### PLOT
        ## first clear the Figure() from the accessibilityInputChart layout,
        ## so a new one will be printed when function is run several times
        for i in reversed(range(self.marketChart.count())):
            self.marketChart.itemAt(i).widget().setParent(None)

        # add matplotlib Figure to chartFrame / accessibilityInputChart layout
        figure = Figure(figsize=(1,1), tight_layout=True)
        #figure.suptitle("Market balance \n\n ", fontsize=12)
        figureCanvas = FigureCanvas(figure)
        self.marketChart.addWidget(figureCanvas)
        figure.patch.set_alpha(0.0)
        ax = figure.add_subplot(111)


        # get values from excel sheets
        sheet = 'Indicator 2 Market balance'
        data = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['E3','E4','E5','E6','E8'])
        labels = ('Edam-Volendam', 'Hoorn', 'Purmerend', 'Zaanstad', 'Total')

        #print "market balance", data

        y_pos = np.arange(len(data))
        #performance = 100 * np.random.rand(len(data))
        #error = np.random.rand(len(people))

        ax.barh(y_pos, data, align='center', color='blue', ecolor='black')

        # label
        #y
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=7)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_ylabel('Municipality', fontsize=7)
        #x
        ax.xaxis.set_tick_params(labelsize=7)
        ax.set_xlabel('HU', fontsize=7)
        ax.xaxis.set_label_coords(1.05, -0.025)



        # set the xlims
        xlims = ax.get_xlim()
        if (xlims[0]<0) and (xlims[1]>0):
            m = max(abs(np.array(xlims)))
            ax.set_xlim(-m*1.5, m*1.5)
        else:
            ax.set_xlim(xlims[0]*1.2, xlims[1]*1.2)

        # annotate bars
        self.labelBars(ax,data)

        return


    def financialPlot(self):
        ### INDICATORS

        ### PLOT
        ## first clear the Figure() from the accessibilityInputChart layout,
        ## so a new one will be printed when function is run several times
        for i in reversed(range(self.financialChart.count())):
            self.financialChart.itemAt(i).widget().setParent(None)

        # add matplotlib Figure to chartFrame / accessibilityInputChart layout
        figure = Figure(figsize=(1,1), tight_layout=True)
        #figure.suptitle("Finances", fontsize=12)
        figureCanvas = FigureCanvas(figure)
        self.financialChart.addWidget(figureCanvas)
        figure.patch.set_alpha(0.0)
        ax = figure.add_subplot(111)


        # get values from excel sheets
        sheet = 'Indicator 3 Finances'
        data1 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['B25','B26','B27','B28','B29'])
        data2 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['C25','C26','C27','C28','C29'])
        data3 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['D25','D26','D27','D28','D29'])
        labels = ('1', '2', '3', '4', '5')


        y_pos = np.arange(len(data1))

        width = self.barHeight

        a=ax.barh(y_pos-width, data1, width, color='blue', ecolor='black')
        b=ax.barh(y_pos, data2, width, color='red', ecolor='black')
        c=ax.barh(y_pos+width, data3, width, color='green', ecolor='black')

        # labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=7)
        ax.ticklabel_format(style='plain', axis='x')
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_ylabel('Package', fontsize=7)


        #ax.xaxis.set_tick_params(labelsize=7)
        #ax.set_xticks([-1000000000, -500000000, 0, 500000000, 1000000000])
        #ax.set_xticklabels(labels=['-300M EUR', '-200M EUR', '', '0', '250M EUR', '500M EUR'], fontsize=7)

        xlabels=ax.get_xticklabels()
        xlabs=[]
        for xlab in xlabels:
            xlabs.append(xlab.get_text())

        ax.set_xticklabels(labels=xlabs,rotation=15)
        ax.xaxis.set_tick_params(labelsize=7)

        #ax.set_xlabel('[€]', fontsize=7)


        # legend
        #ax.legend((a[0], b[0], c[0]), ('Housing revenue', 'Transport investments', 'Financial result'), loc='lower right', prop={'size': 7})
        figure.legend((a[0], b[0], c[0]), ('Housing rev.', 'Transport investm.', 'Finances'), bbox_to_anchor=(0.5, 1.01), loc='upper center', ncol=3, prop={'size': 7})

        #ax.set_xticks([0,10,20,30,40,50,60,70,80,90,100])
        #ax.set_title('How fast do you want to go today?')

        ##set the xlims
        # xlims = ax.get_xlim()
        # ax.set_xlim(xlims[0]*1.2, xlims[1]*1.2)
        xlims = ax.get_xlim()
        if (xlims[0]<0) and (xlims[1]>0):
            m = max(abs(np.array(xlims)))
            ax.set_xlim(-m*1.5, m*1.5)
        else:
            ax.set_xlim(xlims[0]*1.2, xlims[1]*1.2)
        # annotate bars
        self.labelBars(ax, data1, -width)
        self.labelBars(ax, data2, 0)
        self.labelBars(ax, data3, width)

        # xlabels = ax.get_xticklabels()
        # for xlab in xlabels:
        #     print xlab.get_text()


        return

    def spatialPlot(self):
        ### INDICATORS

        ### PLOT
        ## first clear the Figure() from the accessibilityInputChart layout,
        ## so a new one will be printed when function is run several times
        for i in reversed(range(self.spatialChart.count())):
            self.spatialChart.itemAt(i).widget().setParent(None)

        # add matplotlib Figure to chartFrame / accessibilityInputChart layout
        figure = Figure(figsize=(1,1), tight_layout=True)
        #figure.suptitle("Spatial goals", fontsize=12)
        figureCanvas = FigureCanvas(figure)
        self.spatialChart.addWidget(figureCanvas)
        figure.patch.set_alpha(0.0)
        ax = figure.add_subplot(111)


        # get values from excel sheets
        sheet = 'Indicator 4 Spatial Goals'
        # tod
        data1 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['B11','B12','B13','B14','B15'])
        # infill
        data2 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['D11','D12','D13','D14','D15'])
        # rental
        #data3 = self.getValue_xlwings(book=self.book, sheet=sheet, cells=['F11','F12','F13','F14','F15'])
        #labels = ('Package 1', 'Package 2', 'Package 3', 'Package 4', 'Package 5')
        labels = ('1', '2', '3', '4', '5')

        # data1 = 100 * np.random.rand(len(labels))
        # data2 = 100 * np.random.rand(len(labels))
        # data3 = 100 * np.random.rand(len(labels))

        # print "spatial1: ", data1
        # print "spatial2: ", data2
        # print "spatial3: ", data3

        y_pos = np.arange(len(data1))
        #performance = 100 * np.random.rand(len(data))
        #error = np.random.rand(len(people))
        width = self.barHeight

        a=ax.barh(y_pos-width, data1, width, color='blue', ecolor='black')
        b=ax.barh(y_pos, data2, width, color='red', ecolor='black')
        #c=ax.barh(y_pos+width, data3, width, color='green', ecolor='black')

        # labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=7)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_ylabel('Package', fontsize=7)
        ax.set_xticks([0,10,20,30,40,50,60,70,80,90,100])
        ax.xaxis.set_tick_params(labelsize=7)
        ax.set_xlabel('[%]', fontsize=7)
        ax.xaxis.set_label_coords(1, -0.025)

        # legend
        figure.legend((a[0], b[0]), ('TOD', 'Infill'), bbox_to_anchor=(0.5, 1.01), loc='upper center', ncol=3, prop={'size': 7})
        #ax.legend((a[0], b[0]), ('TOD', 'Infill'), loc='lower right', prop={'size': 7})

        #figure.tight_layout(rect=[0.4, 0.4, 1, 1])
        #figure.tight_layout(pad=0.05)
        #figure.subplots_adjust(hspace=0.53)

        # set the xlims
        xlims = ax.get_xlim()
        if (xlims[0]<0) and (xlims[1]>0):
            m = max(abs(np.array(xlims)))
            ax.set_xlim(-m*1.5, m*1.5)
        else:
            ax.set_xlim(xlims[0]*1.2, xlims[1]*1.2)
        # xlims = ax.get_xlim()
        # ax.set_xlim(xlims[0]*1.2, xlims[1]*1.2)
        # annotate bars
        self.labelBars(ax, data1, -width)
        self.labelBars(ax, data2, 0)
        #self.labelBars(ax, data3, width)



        return

    def labelBars(self, axis=None, data=None, offset=0):

        # annotate bars
        m = max(abs(data))
        for i, v in enumerate(data):
            t = str(int(v))
            if v < 0:
                align = 'right'
                p = -m
            elif v == 0:
                continue
            else:
                align = 'left'
                p = m
            #axis.text(v+(p*0.05), i+offset, str(int(t)), horizontalalignment=align, verticalalignment='center', color='black', fontsize=6, style='italic')
            axis.text(v+(p*0.05), i+offset, "{:,}".format(int(t)), horizontalalignment=align, verticalalignment='center', color='black', fontsize=6, style='italic')




    ############################################################
    ################## CLOSE ###################################
    ############################################################
    def closeEvent(self, event):
        self.housingTable.clearSelection()
        self.infraTable.clearSelection()
        self.housingLayer.removeSelection()
        self.infraLayer.removeSelection()
        #self.packageComboBox.setCurrentIndex(0)
        self.packageTable.selectRow(0)
        self.closingPlugin.emit()
        event.accept()

























