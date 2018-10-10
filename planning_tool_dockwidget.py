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

import os
import math

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QPoint, QSize

from qgis.core import *
from qgis.core import QgsGeometry, QgsMapLayerRegistry
# from PyQt4 import QtCore
# from PyQt4 import QtGui

from qgis.gui import *
from qgis.gui import QgsMapTool
from qgis.networkanalysis import *

from PyQt4.QtGui import QCursor, QPixmap, QAction
from PyQt4.QtCore import Qt, pyqtSignal, QPoint
#from PyQt4.QtCore import pyqtSignal
from . import utility_functions as uf

# this is for adding the "external" folder to the system path, because the QGIS python is only looking in the system path for python packages
# you can see that this works by doing import sys, sys.path inside the QGIS python console
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "external"))

import processing
import random
import numpy as np
import openpyxl
import xlwings as xw
# matplotlib for the charts
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


FORM_BASE, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PlanningTool_dockwidget_base.ui'))

FORM_INDICATORS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PlanningTool_chart.ui'))

FORM_HOUSING, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PlanningTool_housing.ui'))

FORM_INFRASTRUCTURE, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PlanningTool_infrastructure.ui'))




################################################################################################################
###################################################### SELECT-TOOL #############################################
################################################################################################################
class PointTool(QgsMapTool, QAction):
    def __init__(self, widget, canvas, action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.action = action
        self.widget = widget
        #self.book = self.widget.book

        self.cursor = QCursor(Qt.PointingHandCursor)

        # layers need to be turned on when PointTool is opened for the first time, otherwise error when trying to access these layers
        self.infra_layer = uf.getCanvasLayerByName(self.canvas, "Infrastructure_Investments")
        self.housing_layer = uf.getCanvasLayerByName(self.canvas, "Housing_Plans")



    # def canvasPressEvent(self, event):
    #     pass
    #
    # def canvasMoveEvent(self, event):
    #     x = event.pos().x()
    #     y = event.pos().y()
    #
    #     point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def canvasReleaseEvent(self, event):

        mapPoint = self.toMapCoordinates(event.pos())
        infra_layerPoint = self.toLayerCoordinates(self.infra_layer, mapPoint)
        housing_layerPoint = self.toLayerCoordinates(self.housing_layer, mapPoint)

        # layers need to be turned on when PointTool is opened for the first time, otherwise error when trying to access these layers
        infra_intersection = [None, 10000000]
        for poly in self.infra_layer.getFeatures():
            if poly.geometry().contains(QgsGeometry.fromPoint(infra_layerPoint)):
                self.infra_layer.removeSelection()
                self.infra_layer.select([poly.id()])
                break
        #         cent = poly.geometry().centroid().asPoint()
        #
        #         dist = cent.distance(infra_layerPoint)
        #
        #         if dist < infra_intersection[1]:
        #             infra_intersection[0] = poly
        #             infra_intersection[1] = dist
        #
        # if infra_intersection[0]:
        #     infra_layer.select([infra_intersection[0].id()])

        housing_intersections = [None, 10000000]
        for poly in self.housing_layer.getFeatures():
            if poly.geometry().contains(QgsGeometry.fromPoint(housing_layerPoint)):
                self.housing_layer.removeSelection()
                self.housing_layer.select([poly.id()])
                break


    def canvasDoubleClickEvent(self, event):
        self.infra_layer.removeSelection()
        self.housing_layer.removeSelection()

    def activate(self):
        self.action.setChecked(True)
        self.canvas.setCursor(self.cursor)
    #
    def deactivate(self):
        self.action.setChecked(False)




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

        # TODO: what should maybe be done is to implement my own data structure from the layer
        # and excel data, e.g. a pandas table, and use that for loading and saving data.
        # When the plugin is closed or changes are saved with saving button then this data structure is pushed to the
        # layers and excel sheet. This also means that the OK button only saves in my own data structure, and the
        # populate table function gets its values from that.

        # load project file
        self.loadProjectFile()

        self.infraLayer = uf.getCanvasLayerByName(self.canvas, "Infrastructure_Investments")
        self.housingLayer = uf.getCanvasLayerByName(self.canvas, "Housing_Plans")

        # populate box and table
        self.populateComboBox()
        self.packageSelected()


        # connect signal/slot
        # table
        self.housingTable.cellClicked.connect(self.housingRowSelected)
        self.infraTable.cellClicked.connect(self.infraRowSelected)
        # comboBox
        self.packageComboBox.currentIndexChanged.connect(self.packageSelected)
        # layers
        self.infraLayer.selectionChanged.connect(self.infraLayerSelectionChanged)
        self.housingLayer.selectionChanged.connect(self.housingLayerSelectionChanged)
        # sliders
        self.housingSlider.valueChanged.connect(self.housingSliderChanged)
        #self.housingLayer.valueChanged.connect(self.housingLayerSelectionChanged)


        # buttons
        # signal slots for buttons should simly save all the current percentages to the excel sheet and then update the plot
        # in this way the plot is only update from the OK button and not from moving the slider, which obviously would be terrible
        self.okHousing.clicked.connect(self.comboHeight)




        # generate the plot
        self.refreshPlot()
    ############################################################
    ################## SLIDERS #################################
    ############################################################
    def housingSliderChanged(self):
        #print self.housingSlider.value()
        if self.housingTable.selectedItems():
            # set current slider value in the housing table (works dynamic)
            row = self.housingTable.currentRow()
            percentItem = QtGui.QTableWidgetItem(str(self.housingSlider.value()))
            percentItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.housingTable.setItem(row, 1, percentItem)
            #self.housingTable.setItem(row, 1, QtGui.QTableWidgetItem(str(self.housingSlider.value())))

    ############################################################
    ################## COMBOBOX ################################
    ############################################################
    def populateComboBox(self):
        #
        # listView = QtGui.QListView()
        # listView.font().setPointSize(25)
        #
        # self.packageComboBox.setView(listView)
        #
        #
        # font = self.packageComboBox.font()
        # font.setPointSize(25)
        # self.packageComboBox.setFont(font)

        view = QtGui.QListView()  # creat a ListView
        #view.setFixedWidth(500)  # set the ListView with fixed Width
        #view.setFixedHeight(200)

        #self.packageComboBox.setMaximumWidth(500)  # will be overwritten by style-sheet
        #self.packageComboBox.addItems(["TEsst1111", "TEsst11111111111111", "TEsst1111111111111111111111111"])


        self.packageComboBox.addItem("All Packages")
        self.packageComboBox.addItem("Package 1 - Noordoever Noordzeekanaal")
        self.packageComboBox.addItem("Package 2 - Zaandam – Noord")
        self.packageComboBox.addItem("Package 3 - Purmerend: BBG of A7")
        self.packageComboBox.addItem("Package 4 - Hoorn")
        self.packageComboBox.addItem("Package 5 - Ring A10 oost – Waterland")
        #pass

        #
        self.packageComboBox.setStyleSheet('''
        QComboBox { min-height: 40px; max-height: 40px;}
        QComboBox QAbstractItemView::item { min-height: 40px; max-height: 40px;}"
        ''')

        self.packageComboBox.setView(view)


        # self.packageComboBox.setIconSize(QSize(48, 48))
        # self.packageComboBox.setSizePolicy(Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Expanding)
        # self.packageComboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        #QComboBox { min-height: 40px;}
        #QListView::item:selected { color: red; background-color: lightgray; min-width: 1000px;}"
        self.packageComboBox.setMinimumHeight(100)
        self.packageComboBox.adjustSize()
        #self.packageComboBox.update()


    def comboHeight(self):
        # print self.packageComboBox.model()
        # self.packageComboBox.model().setData(self.packageComboBox.model().index(0, 0), QSize(100, 100), Qt.SizeHintRole)
        # print self.packageComboBox.model()

        # self.packageComboBox.setStyleSheet("QComboBox QAbstractItemView
        #     {
        #     min-width: 150px;
        #     }

        # listView = QtGui.QListView()
        # self.packageComboBox.setView(listView)

        # self.packageComboBox.setStyleSheet(
        #     QComboBox QAbstractItemView::item { min-height: 35px; min-width: 50px; }QListView::item:selected { color: black; background-color: lightgray}")

        # self.packageComboBox.addItem("All Packages")
        # self.packageComboBox.addItem("Package 1 - Noordoever Noordzeekanaal")
        # self.packageComboBox.addItem("Package 2 - Zaandam – Noord")
        # self.packageComboBox.addItem("Package 3 - Purmerend: BBG of A7")
        # self.packageComboBox.addItem("Package 4 - Hoorn")
        # self.packageComboBox.addItem("Package 5 - Ring A10 oost – Waterland")
        pass




    def packageSelected(self):

        package = self.packageComboBox.currentIndex()


        ####if "all packages" selected
        if package == 0:
            #populate table with all packages
            expressionHousing = "Package IS 'p1' or Package IS 'p2' or Package IS 'p3' or Package IS 'p4' or Package IS 'p5'"
            expressionInfra = "Package IS 'P1' or Package IS 'P2' or Package IS 'P3' or Package IS 'P4' or Package IS 'P5'"
        else:
            expressionHousing = "Package IS " + "'p"+str(package)+"'"
            expressionInfra = "Package IS " + "'P"+str(package)+"'"

        
        request = QgsFeatureRequest().setFilterExpression(expressionHousing)
        housingFeatureIterator = self.housingLayer.getFeatures(request)
        feat = QgsFeature()
        housingFeatureIterator.nextFeature(feat)
        housingBox = feat.geometry().boundingBox()
        housingNames = [feat.attribute('NameShort')]
        while housingFeatureIterator.nextFeature(feat):
            housingBox.combineExtentWith(feat.geometry().boundingBox())
            housingNames.append(feat.attribute('NameShort'))

        request = QgsFeatureRequest().setFilterExpression(expressionInfra)
        infraFeatureIterator = self.infraLayer.getFeatures(request)
        feat = QgsFeature()
        infraFeatureIterator.nextFeature(feat)
        infraBox = feat.geometry().boundingBox()
        infraNames = [feat.attribute('ShortName')]
        while infraFeatureIterator.nextFeature(feat):
            infraBox.combineExtentWith(feat.geometry().boundingBox())
            infraNames.append(feat.attribute('ShortName'))

        # populate the tables
        self.populateTable(attributes=housingNames, table=self.housingTable, tableName='Housing Plans')
        self.populateTable(attributes=infraNames, table=self.infraTable, tableName='Infrastructure Investments')

        # zoom to package
        #if (not self.housingLayer.selectedFeatures()) and (not self.infraLayer.selectedFeatures()):
        housingBox.combineExtentWith(infraBox)
        self.canvas.setExtent(housingBox)
        self.canvas.refresh()


    ############################################################
    ################## TABLE ###################################
    ############################################################


    # housing
    def populateTable(self, attributes=None, table=None, tableName=None):


        table.clear()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels([tableName, "%"])
        table.setRowCount(len(attributes))
        for i, att in enumerate(attributes):
            # i is the table row, items mus tbe added as QTableWidgetItems
            table.setItem(i,0,QtGui.QTableWidgetItem(att))
            # TODO: here is need to get the previous value of this row, instead of just setting it to a constant value
            percentItem = QtGui.QTableWidgetItem('10')
            percentItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            table.setItem(i, 1, percentItem)


        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # horizontal
        table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        table.setColumnWidth(1, 50)

        # vertical
        table.resizeRowsToContents()
        table.verticalHeader().setVisible(True)
        table.verticalHeader().setDefaultSectionSize(40)




    # infra
    def populateTable(self, attributes=None, table=None, tableName=None):


        table.clear()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels([tableName, "%"])
        table.setRowCount(len(attributes))
        for i, att in enumerate(attributes):
            # i is the table row, items mus tbe added as QTableWidgetItems
            table.setItem(i,0,QtGui.QTableWidgetItem(att))
            # TODO: here is need to get the previous value of this row, instead of just setting it to a constant value
            percentItem = QtGui.QTableWidgetItem('10')
            percentItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            table.setItem(i, 1, percentItem)


        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # horizontal
        table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        table.setColumnWidth(1, 50)

        # vertical
        table.resizeRowsToContents()
        table.verticalHeader().setVisible(True)
        table.verticalHeader().setDefaultSectionSize(40)




    # def populateTable(self, attributes=None, table=None, tableName=None):
    #
    #
    #     table.clear()
    #     table.setColumnCount(2)
    #     table.setHorizontalHeaderLabels([tableName, "%"])
    #     table.setRowCount(len(attributes))
    #     for i, att in enumerate(attributes):
    #         # i is the table row, items mus tbe added as QTableWidgetItems
    #         table.setItem(i,0,QtGui.QTableWidgetItem(att))
    #         # TODO: here is need to get the previous value of this row, instead of just setting it to a constant value
    #         percentItem = QtGui.QTableWidgetItem('10')
    #         percentItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    #         table.setItem(i, 1, percentItem)
    #         #table.setItem(i, 1, QtGui.QTableWidgetItem('10'))
    #
    #     table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    #
    #     # horizontal
    #     table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
    #     #table.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
    #     #table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
    #     #table.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
    #     table.setColumnWidth(1, 50)
    #
    #     # vertical
    #     table.resizeRowsToContents()
    #     table.verticalHeader().setVisible(True)
    #     #table.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
    #     table.verticalHeader().setDefaultSectionSize(40)


    # housing



    def housingRowSelected(self):

        selectedItem = self.housingTable.selectedItems()[0].text().encode('utf-8')

        self.housingLayer.removeSelection()
        uf.selectFeaturesByExpression(self.housingLayer, "NameShort IS " + "'"+selectedItem+"'")
        self.zoomToSelectedFeature(scale=1.3, layer=self.housingLayer)
        self.housingLabel.setText(selectedItem)

    # infra
    def infraRowSelected(self):

        selectedItem = self.infraTable.selectedItems()[0].text().encode('utf-8')
        self.infraLayer.removeSelection()
        uf.selectFeaturesByExpression(self.infraLayer, "ShortName IS " + "'"+selectedItem+"'")
        self.zoomToSelectedFeature(scale=1.3, layer=self.infraLayer)
        self.infraLabel.setText(selectedItem)


    ############################################################
    ################## LAYER SELECTION CHANGED #################
    ############################################################
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
        packageTable = self.packageComboBox.currentIndex()
        if packageMap != packageTable and packageTable != 0:
                self.packageComboBox.setCurrentIndex(packageMap)
                self.packageSelected()

        ## select the corresponding row of the project and update the label above sliders
        rowCount = self.housingTable.rowCount()
        # iterate over all table rows and check where the name corresponds to the currently selected feature
        for i in range(rowCount):
            tableName = self.housingTable.item(i, 0).text()
            layerName = feat.attribute("NameShort")
            if tableName == layerName:
                # select/highlight matching row
                self.housingTable.selectRow(i)
                # update the label above the sliders
                self.housingLabel.setText(tableName)
                # update the slider position
                self.housingSlider.setValue(int(self.housingTable.item(i,1).text()))
                break

        self.housingTable.blockSignals(False)

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
        packageTable = self.packageComboBox.currentIndex()
        if packageMap != packageTable and packageTable != 0:
                self.packageComboBox.setCurrentIndex(packageMap)
                self.packageSelected()

        ## select the corresponding row of the project and update the label above sliders
        rowCount = self.infraTable.rowCount()
        # iterate over all table rows and check where the name corresponds to the currently selected feature
        for i in range(rowCount):
            tableName = self.infraTable.item(i, 0).text()
            layerName = feat.attribute("ShortName")
            if tableName == layerName:
                # select/highlight matching row
                self.infraTable.selectRow(i)
                # update the label above the sliders
                self.infraLabel.setText(tableName)
                break

        #self.infraTable.selectRow(4)

        self.infraTable.blockSignals(False)

    ############################################################
    ################## CANVAS ##################################
    ############################################################
    def loadProjectFile(self):

        # open the QGIS project file
        scenario_open = False
        scenario_file = os.path.join(os.path.dirname(__file__),'data','project_file24.qgs')


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

    # # save value
    # def saveValue(self):
    #
    #     iC = self.inputYes.isChecked()
    #     iC2 = self.inputNo.isChecked()
    #     iA = self.inputAmsterdam.text()
    #     iE = self.inputEdam.text()
    #     iH = self.inputHoorn.text()
    #     iP = self.inputPurmerend.text()
    #     iZ = self.inputZaanstad.text()
    #     iPr = self.inputProvince.text()
    #     iM = self.inputMinistry.text()
    #
    #     # take from input field and save to excel file, depending on polygonID = row in excel file
    #     # column depending on which input field
    #
    #
    #     srcfile = openpyxl.load_workbook(self.excel_file, read_only=False,
    #                                      keep_vba=True)  # to open the excel sheet and if it has macros
    #     sheet = srcfile.get_sheet_by_name(self.sheet_name)  # get sheetname from the file
    #
    #     # project id is at row+2 in excel, thats why I need to introduce this skip variable
    #     k = 2
    #     if iC == True and iC2 == False:
    #         sheet['P' + str(self.id + k)] = 1
    #     elif iC == False and iC2 == True:
    #         sheet['P' + str(self.id + k)] = 0
    #     else:
    #         # chase case where both yes and no are checked
    #         uf.showMessage(self.iface, 'Please select either "yes" or "no"', type='Info', lev=1, dur=5)
    #         return
    #     sheet['Q' + str(self.id + k)] = float(iA)
    #     sheet['R' + str(self.id + k)] = float(iE)
    #     sheet['S' + str(self.id + k)] = float(iH)
    #     sheet['T' + str(self.id + k)] = float(iP)
    #     sheet['U' + str(self.id + k)] = float(iZ)
    #     sheet['V' + str(self.id + k)] = float(iPr)
    #     sheet['W' + str(self.id + k)] = float(iM)
    #
    #     srcfile.save(self.excel_file)
    #
    #     self.refreshPlot()
    ############################################################
    ################## EXCEL ###################################
    ############################################################
    def getValue_xlwings(self, book, sheet, cells):
        # # # run Excel with xlwings
        # # # this does not work on windows yet, but the only reason is probably that it cannot access the sheet because Excel opens
        # # # with a put in Product Key Window. So maybe it is actually better to use win32com.client solution as this seems to work better here
        #
        # TODO: open app and book in planning_tool.py and pass to the dockwidget, same way as done for the plot dockwidget that is passed to infrastructure input class
        # app = xw.App(visible=False)
        # book = app.books.open(filename)
        # #book = xw.Book(filename)
        # #app = xw.apps.active
        # app.visible = False

        ##get new value based on UDF (user defined function)
        vals = []
        for cell in cells:
            vals.append(book.sheets[sheet].range(cell).value)

        # book.close()
        # app.kill()

        # return value
        return np.asarray(vals)
        #return [-1035, -1907, -3106, -7902, -3487]


    ###########################################################
    ################## PLOT ###################################
    ###########################################################
    def refreshPlot(self):
        ### INDICATORS

        #self.excel_file = os.path.join(os.path.dirname(__file__), 'data', 'excel_data.xlsm')

        print "refreshing plot"

        ### ACCESIBILITY
        # sheet_name = 'INPUT - Infra Projects'
        # ## Transit accesibility
        # c = []
        # af = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='AF', row_start=3, row_end=40)
        # aj = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='AJ', row_start=3, row_end=40)
        # ak = aj * 0.01
        # p = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='P', row_start=3, row_end=40)
        # ar = p * af * ak
        # c.append(sum(ar))
        # # c4
        # ag = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='AG', row_start=3, row_end=40)
        # as1 = p * ag * ak
        # c.append(sum(as1))
        # # c5
        # ah = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='AH', row_start=3, row_end=40)
        # at = p * ah * ak
        # c.append(sum(at))
        # # c6
        # ai = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='AI', row_start=3, row_end=40)
        # au = p * ai * ak
        # c.append(sum(au))
        # ## Car accesibility
        # d = []
        # # d3
        # aa = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='AA', row_start=3, row_end=40)
        # aj = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='AJ', row_start=3, row_end=40)
        # ak = aj * 0.01
        # p = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='P', row_start=3, row_end=40)
        # aw = p * aa * ak
        # d.append(sum(aw))
        # # d4
        # ab = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='AB', row_start=3, row_end=40)
        # ax = p * ab * ak
        # d.append(sum(ax))
        # # d5
        # ac = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='AC', row_start=3, row_end=40)
        # ay = p * ac * ak
        # d.append(sum(ay))
        # # d6
        # ad = self.getValue(filepath=self.excel_file, sheetname=sheet_name, col='AD', row_start=3, row_end=40)
        # az = p * ad * ak
        # d.append(sum(az))
        #
        # cd = np.add(c, d)
        # accesibility = np.append(cd, np.mean(cd))

        ### Accesibility
        #accesibility = self.getValue_xlwings(self.book, 'Indicator 1 Accessibility', ['E3', 'E4', 'E5', 'E6', 'E7'])
        #accesibility = np.append(accesibility, np.mean(accesibility))

        ### Market Balance
        market_balance = np.asarray([-1035, -1907, -3106, -7902, -3487])
        #market_balance = self.getValue_xlwings(self.excel_file, 'Indicator 2 Market balance', ['E3', 'E4', 'E5', 'E6', 'E7'])

        ### Market Balance
        finances = np.asarray([-5.01, 0, -35.2, 0, 0, 0])
        #finances = self.getValue_xlwings(self.excel_file, 'Indicator 3 Finances', ['E3', 'E4', 'E5', 'E6', 'E7', 'E8'])



        ### PLOT
        # first clear the Figure() from the chartView layout,
        # so a new one will be printed when function is run several times
        for i in reversed(range(self.chartView.count())):
            self.chartView.itemAt(i).widget().setParent(None)

        # add matplotlib Figure to chartFrame / chartView layout
        self.chart_figure = Figure(figsize=(1,1), tight_layout=True)
        #self.chart_figure.suptitle("Indicators \n\n ", fontsize=18, fontweight='bold')
        self.chart_canvas = FigureCanvas(self.chart_figure)
        self.chartView.addWidget(self.chart_canvas)

        self.plotChartHorizontal(self.chart_figure.add_subplot(111))

        # plot the subplots
        #self.plotChart(self.chart_figure.add_subplot(111), accesibility, "Accessibility", 'b')
        #self.plotChart(self.chart_figure.add_subplot(111), market_balance, "Market Balance", 'g')
        #self.plotChart(self.chart_figure.add_subplot(313), finances, "Finances", 'r')
        #self.chart_figure.tight_layout()
        # you can actually probably adjust it perfectly with this
        #self.chart_figure.tight_layout(rect=[0.1, -0.05, 0.94, 1])
        #self.chart_figure.subplots_adjust(hspace=0.53)
        # make background of plot transparent
        self.chart_figure.patch.set_alpha(0.0)
        #self.chart_figure.patch.set_facecolor('red')

        return

    # def getValue(self, filepath=None, sheetname=None, col=None, row_start=0, row_end=1):
    #     source_file = openpyxl.load_workbook(filepath, read_only=False, keep_vba=True)  # to open the excel sheet and if it has macros
    #     sheet = source_file.get_sheet_by_name(sheetname)
    #     data = []
    #     for i in range(row_start, row_end + 1):
    #         val = float(sheet[col + str(i)].value)
    #         data.append(val)
    #     source_file.save(self.excel_file)
    #     return np.array(data)


    def plotChart(self, ax, indicator, indicator_name, color):

        ax.cla()

        N = len(indicator)
        ind = np.arange(N)  # the x locations for the groups
        width = 0.35  # the width of the bars

        #rects1 = ax.bar(ind - width, first, width, color='b')
        rects = ax.bar(ind, indicator, width, color=color, align='center')
        #rects3 = ax.bar(ind + width, first, width, color='r')


        # add some text for labels, title and axes ticks
        ax.set_ylabel('Indicator score')
        #ax.set_xlabel('Region')
        ax.set_xticks(ind)
        if N == 5:
            ax.set_xticklabels(('Edam-Vol.', 'Hoorn', 'Purmerend', 'Zaanstad', 'Province'), rotation=30)
        else:
            ax.set_xticklabels(('Edam-Vol.', 'Hoorn', 'Purmerend', 'Zaanstad', 'Province', 'Ministry'), rotation=30)
        ax.legend((rects[0],), (indicator_name,), fontsize=12)

        #low = min(rects1)

        #ax.set_aspect(aspect='equal')

        if np.mean(indicator) < 0:
            ax.invert_yaxis()
            ax.set_ylim((0, min(indicator)*1.8))
        else:
            ax.set_ylim((0, max(indicator)*1.8))

        def autolabel(rectangle):
            """
            Attach a text label above each bar displaying its height
            """
            for rect in rectangle:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                        '%.3f' % float(height),
                        ha='center', va='bottom')

        autolabel(rects)


    def plotChartHorizontal(self, ax):
        #fig, ax = plt.subplots()

        # Example data
        people = ('Hoorn', 'Amsterdam', 'Municipality')
        y_pos = np.arange(len(people))
        performance = 100 * np.random.rand(len(people))
        #error = np.random.rand(len(people))

        ax.barh(y_pos, performance, align='center',
                color='blue', ecolor='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(people)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Percent')
        ax.set_xticks([0,10,20,30,40,50,60,70,80,90,100])
        #ax.set_title('How fast do you want to go today?')


    ############################################################
    ################## CLOSE ###################################
    ############################################################
    def closeEvent(self, event):
        self.housingTable.clearSelection()
        self.infraTable.clearSelection()
        self.housingLayer.removeSelection()
        self.infraLayer.removeSelection()
        self.packageComboBox.setCurrentIndex(0)
        self.closingPlugin.emit()
        event.accept()

























