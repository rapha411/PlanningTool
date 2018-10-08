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
        self.book = self.widget.book

        self.cursor = QCursor(Qt.PointingHandCursor)

        self.infra_layer = uf.getCanvasLayerByName(self.canvas, "Infrastructure_Investments")
        self.housing_layer = uf.getCanvasLayerByName(self.canvas, "Housing_Plans")

        self.infra_layer.selectionChanged.connect(self.infraSelectionChanged)
        self.housing_layer.selectionChanged.connect(self.housingSelectionChanged)

        ### TODO: now just put this in the SelectionChanged function
        # self.widget.inputAmsterdam.setText("works")


    def infraSelectionChanged(self):
        if self.infra_layer.selectedFeatures():
            print "infra selection Changed"
            self.widget.selectInfraRow()


    def housingSelectionChanged(self):
        if self.housing_layer.selectedFeatures():
            print "housing selection Changed"
            self.widget.selectHousingRow()

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
        print "map tool deactivated"


class IndicatorsChartDocked(QtGui.QDockWidget, FORM_BASE, QgsMapTool):

    closingPlugin = pyqtSignal()
    # canvasDoubleClicked = pyqtSignal(object, object)

    def __init__(self, iface, parent=None, book=None):

        super(IndicatorsChartDocked, self).__init__(parent)

        self.setupUi(self)

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        self.book = book
        self.excel_file = os.path.join(os.path.dirname(__file__), 'data', 'excel_data.xlsm')


        # generate the plot
        self.refreshPlot()

        self.infraLayer = uf.getCanvasLayerByName(self.canvas, "Infrastructure_Investments")
        self.housingLayer = uf.getCanvasLayerByName(self.canvas, "Housing_Plans")


        self.populateComboBox()
        self.populateTable()

        # connect signal/slot
        self.housingTable.cellClicked.connect(self.selectHousingFeat)
        self.infraTable.cellClicked.connect(self.selectInfraFeat)

        self.packageComboBox.currentIndexChanged.connect(self.zoomToPackage)



        ## infrastructure input
        # signal slot for closing indicator window
        # TODO: closeInfrastructure is actually cancel infrastructure, which should maybe actually restore the values that were
        # their, before the input windows was opened
        #self.okInfrastructure.clicked.connect(self.saveValue)


        # # get project ID and corresponding data from excel sheet
        # self.layer = self.iface.activeLayer()
        # # self.id is the row number (zero starting) of the attributes table in QGIS, so not the actual id column value
        # # thas where the +4 in the getValue call below is coming from
        # temp1, temp2 = uf.getFieldValues(self.housing_layer, 'id', null=False, selection=True)
        # # guard for when not exactly one project is selected
        # if len(temp1) != 1:
        #     #return
        #     pass
        # # self.id = temp1[0]
        # temp1 = None
        # temp2 = None
        # # print "die project ID aus QGIS: ", self.id
        #
        # # get excel row by id of project id from QGIS
        # #excel_id = self.getValue(filepath=self.excel_file, sheetname=self.sheet_name, col='A', row_start=self.id)[0]
        # # print "excel id: ", excel_id
        #
        # # # get values with openpyxl
        # # iC = self.getValue(filepath=self.excel_file, sheetname=self.sheet_name, col='P', row_start=self.id)[0]
        # # iA = self.getValue(filepath=self.excel_file, sheetname=self.sheet_name, col='Q', row_start=self.id)[0]
        # # iE = self.getValue(filepath=self.excel_file, sheetname=self.sheet_name, col='R', row_start=self.id)[0]
        # # iP = self.getValue(filepath=self.excel_file, sheetname=self.sheet_name, col='S', row_start=self.id)[0]
        # # iZ = self.getValue(filepath=self.excel_file, sheetname=self.sheet_name, col='T', row_start=self.id)[0]
        # # iH = self.getValue(filepath=self.excel_file, sheetname=self.sheet_name, col='U', row_start=self.id)[0]
        # # iM = self.getValue(filepath=self.excel_file, sheetname=self.sheet_name, col='V', row_start=self.id)[0]
        # # # TODO replace these getValue calls with getValue_xlwings calls, because they always fuck up the excel file!!
        # # #   should also be faster, if that for some reason doesn't work, I could also try to fix the getValue function, e.g. by using a in_memory_file
        #
        #
        # ## get values with xlwings
        # #vals = self.getValue_xlwings(self.app, self.excel_file, 'INPUT - Infra Projects', ['P21','P21','P21','P21','P21','P21','P21'])
        # # iC = vals[0]
        # # iA = vals[1]
        # # iE = vals[2]
        # # iP = vals[3]
        # # iZ = vals[4]
        # # iH = vals[5]
        # # iM = vals[6]

    ############################################################
    ################## COMBOBOX ################################
    ############################################################
    def populateComboBox(self):
        self.packageComboBox.addItem("All Packages")
        self.packageComboBox.addItem("Package 1 - Noordoever Noordzeekanaal")
        self.packageComboBox.addItem("Package 2 - Zaandam – Noord")
        self.packageComboBox.addItem("Package 3 - Purmerend: BBG of A7")
        self.packageComboBox.addItem("Package 4 - Hoorn")
        self.packageComboBox.addItem("Package 5 - Ring A10 oost – Waterland")



    def zoomToPackage(self):


        #TODO: try to implement this without selecting the features, as this triggers feature selection signal
        #solution: https://gis.stackexchange.com/questions/176170/find-bounding-box-for-multiple-features-using-pyqgis

        # remove current selections on this layer
        self.housingLayer.removeSelection()
        self.infraLayer.removeSelection()
        # get the currently selected item in the municipality combo box
        package = self.packageComboBox.currentIndex()
        if package == 0:
            uf.zoomToLayer(self.iface, "Infrastructure_Investments")
            return

        print '"Package" IS p' + "'"+str(package)+"'"
        ### select the features for this municipality
        uf.selectFeaturesByExpression(self.housingLayer, '"Package" IS ' + "'p"+str(package)+"'")
        uf.selectFeaturesByExpression(self.infraLayer, '"Package" IS ' + "'P"+str(package)+"'")
        # make box around the features
        box1 = self.housingLayer.boundingBoxOfSelected()
        box2 = self.infraLayer.boundingBoxOfSelected()
        box1.combineExtentWith(box2)
        # unselect features again
        self.housingLayer.removeSelection()
        self.infraLayer.removeSelection()
        # zoom to the box
        self.canvas.setExtent(box1)
        self.canvas.refresh()




    ############################################################
    ################## TABLE ###################################
    ############################################################
    def populateTable(self):

        # housing
        housingFeats, temp2 = uf.getFieldValues(self.housingLayer, 'NameShort', null=False, selection=False)
        # guard for when not exactly one project is selected
        if len(housingFeats) != 1:
            #return
            pass

        self.housingTable.clear()
        self.housingTable.setColumnCount(2)
        self.housingTable.setHorizontalHeaderLabels(["Housing Plan", "%"])
        self.housingTable.setRowCount(len(housingFeats))
        for i, feat in enumerate(housingFeats):
            # i is the table row, items mus tbe added as QTableWidgetItems
            self.housingTable.setItem(i,0,QtGui.QTableWidgetItem(str(feat)))
            self.housingTable.setItem(i, 1, QtGui.QTableWidgetItem("percent"))

        # horizontal sizing
        self.housingTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        #self.housingTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.housingTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        #self.housingTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.housingTable.resizeRowsToContents()
        self.housingTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.housingTable.verticalHeader().setVisible(False)
        #self.housingTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        # vertical sizing
        self.housingTable.verticalHeader().setDefaultSectionSize(30)

        # infra
        infraFeats, temp2 = uf.getFieldValues(self.infraLayer, 'ShortName', null=False, selection=False)
        # guard for when not exactly one project is selected
        if len(infraFeats) != 1:
            #return
            pass

        self.infraTable.clear()
        self.infraTable.setColumnCount(2)
        self.infraTable.setHorizontalHeaderLabels(["Infrastructure Investment", "%"])
        self.infraTable.setRowCount(len(infraFeats))
        for i, feat in enumerate(infraFeats):
            # i is the table row, items mus tbe added as QTableWidgetItems
            self.infraTable.setItem(i,0,QtGui.QTableWidgetItem(str(feat)))
            self.infraTable.setItem(i, 1, QtGui.QTableWidgetItem("percent"))

        # horizontal sizing
        self.infraTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        #self.infraTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.infraTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        #self.infraTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.infraTable.resizeRowsToContents()
        self.infraTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.infraTable.verticalHeader().setVisible(False)
        #self.infraTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        # vertical sizing
        self.infraTable.verticalHeader().setDefaultSectionSize(30)


    # housing
    def selectHousingFeat(self):

        # selectedItem = self.housingTable.selectedItems()[0]
        # row=selectedItem.row()
        row = self.housingTable.currentRow()
        self.housingLayer.removeSelection()
        self.housingLayer.select(row)
        self.zoomToSelectedFeature(1.2, self.housingLayer)
        self.housingLabel.setText(self.housingTable.currentItem().text())


    def selectHousingRow(self):

        feat, id = uf.getFieldValues(self.housingLayer, 'NameShort', null=False, selection=True)
        self.housingTable.selectRow(id[0])
        #self.housingLabel.setText(str(feat)[3:-2])

    # infra
    def selectInfraFeat(self):

        # selectedItem = self.infraTable.selectedItems()[0]
        # row=selectedItem.row()
        row = self.infraTable.currentRow()
        self.infraLayer.removeSelection()
        self.infraLayer.select(row)
        self.zoomToSelectedFeature(1.2, self.infraLayer)
        self.infraLabel.setText(self.infraTable.currentItem().text())


    def selectInfraRow(self):

        feat, id = uf.getFieldValues(self.infraLayer, 'ShortName', null=False, selection=True)
        self.infraTable.selectRow(id[0])
        #self.infraLabel.setText(str(feat)[3:-2])



    ############################################################
    ################## CANVAS ##################################
    ############################################################
    def zoomToSelectedFeature(self, scale, layer):

        box = layer.boundingBoxOfSelected()
        box.scale(scale)
        #self.canvas = self.determineCanvas()
        self.canvas.setExtent(box)
        #self.canvas.zoomScale(50000)
        self.canvas.refresh()



    def getPoint(self, mapPoint, mouseButton):
        # change tool so you don't get more than one POI
        #self.canvas.unsetMapTool(self.emitPoint)
        #self.canvas.setMapTool(self.userTool)

        # Get the click
        if mapPoint:
            pass

        return



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
    #     print 'new values saved'
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
        self.closingPlugin.emit()
        event.accept()

























