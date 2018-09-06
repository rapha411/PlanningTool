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

from PyQt4 import QtGui, QtCore, uic
from qgis.core import *
from qgis.core import QgsGeometry, QgsMapLayerRegistry
# from PyQt4 import QtCore
# from PyQt4 import QtGui

from qgis.gui import *
from qgis.gui import QgsMapTool
from qgis.networkanalysis import *

from PyQt4.QtGui import QCursor, QPixmap
from PyQt4.QtCore import Qt, pyqtSignal, QPoint
#from PyQt4.QtCore import pyqtSignal
from . import utility_functions as uf

import processing
import random
import numpy as np
# matplotlib for the charts
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PlanningTool_dockwidget_base.ui'))

FORM_CLASS2, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PlanningTool_second.ui'))


class MapToolEmitPoint(QgsMapToolEmitPoint):
    canvasDoubleClicked = QtCore.pyqtSignal(object, object)

    def canvasDoubleClickEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        self.canvasDoubleClicked.emit(point, event.button())
        super(MapToolEmitPoint, self).canvasDoubleClickEvent(event)


class IndicatorsDialog(QtGui.QDialog, FORM_CLASS2):
    def __init__(self, iface, parent=None):

        super(IndicatorsDialog, self).__init__(parent)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


        # add matplotlib Figure to chartFrame
        self.chart_figure = Figure()
        # self.chart_subplot_hist = self.chart_figure.add_subplot(221)
        # self.chart_subplot_line = self.chart_figure.add_subplot(222)
        # self.chart_subplot_pie = self.chart_figure.add_subplot(224)
        self.chart_subplot_bar = self.chart_figure.add_subplot(111)

        self.chart_canvas = FigureCanvas(self.chart_figure)
        self.chartLayout.addWidget(self.chart_canvas)
        self.plotChart()
        self.chart_figure.tight_layout()



        #signal slot for closing indicator window
        self.closeIndicators.clicked.connect(self.closeIndicatorDialog)



    def plotChart(self):

        ax = self.chart_subplot_bar

        N = 5
        ind = np.arange(N)  # the x locations for the groups
        width = 0.25  # the width of the bars

        men_means = (20, 35, 30, 35, 27)
        men_std = (2, 3, 4, 1, 2)
        rects1 = ax.bar(ind - width, men_means, width, color='b', yerr=men_std)

        women_means = (25, 32, 34, 20, 25)
        women_std = (3, 5, 2, 3, 3)
        rects2 = ax.bar(ind, women_means, width, color='g', yerr=women_std)

        municipality_means = (11, 31, 44, 10, 19)
        municipality_std = (6, 2, 5, 7, 3)
        rects3 = ax.bar(ind + width, municipality_means, width, color='r', yerr=municipality_std)


        # add some text for labels, title and axes ticks
        ax.set_ylabel('Scores')
        ax.set_xlabel('Indicators')
        ax.set_title('Scores by organization')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(('I1', 'I2', 'I3', 'I4', 'I5'))

        ax.legend((rects1[0], rects2[0], rects3[0]), ('Ministry', 'Province', 'Municipality'))

        def autolabel(rects):
            """
            Attach a text label above each bar displaying its height
            """
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                        '%d' % int(height),
                        ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)
        autolabel(rects3)



    def closeIndicatorDialog(self):
        self.hide()



class PlanningToolClassDockWidget(QtGui.QDockWidget, FORM_CLASS, QgsMapTool, QgsMapLayerRegistry):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(PlanningToolClassDockWidget, self).__init__(parent)
        #super(QgsMapTool, self).__init__(canvas)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # define globals
        self.iface = iface
        self.canvas = self.iface.mapCanvas()


        self.comboBoxType.addItems(["A","B","C","D","E"])
        #self.comboBoxValue.addItems(["I","II","III","IV"])
        #self.comboBoxValue.resize(200,30)

        model = self.comboBoxValue.model()
        for index in range(10):
            item = QtGui.QStandardItem(str(index))
            item.setForeground(QtGui.QColor('red'))
            font = item.font()
            font.setPointSize(30)
            item.setFont(font)
            model.appendRow(item)





        # page 0 - choose to give or take help
        #self.Pages.setCurrentIndex(0)
        self.activateCanvas()









    def handleDoubleClick(self, point, buttons):
        print('doubleclick')


    def goBack(self):

        if self.Pages.currentIndex() == 16:
            self.Pages.setCurrentIndex(0)

        elif self.Pages.currentIndex() == 17:
            self.Pages.setCurrentIndex(11)

        elif self.Pages.currentIndex() == 20:
            self.Pages.setCurrentIndex(11)

        elif self.Pages.currentIndex() == 19:
            self.Pages.setCurrentIndex(11)
        
        elif self.Pages.currentIndex() == 19:
            self.Pages.setCurrentIndex(11)
        
        elif self.Pages.currentIndex() == 5:
            self.Pages.setCurrentIndex(4)
            # remove the selected roads the user choose for a blocking but didn't save
            roads_layer = uf.getLegendLayerByName(self.iface, "Roads")
            roads_layer.removeSelection()

        elif self.Pages.currentIndex() == 4:
            self.Pages.setCurrentIndex(10)

        elif self.Pages.currentIndex() == 6:
            self.Pages.setCurrentIndex(3)

        elif self.Pages.currentIndex() == 7:
            self.Pages.setCurrentIndex(0)

        elif self.Pages.currentIndex() == 8:
            self.Pages.setCurrentIndex(9)

        elif self.Pages.currentIndex() == 10:
            self.Pages.setCurrentIndex(0)
        
        elif self.Pages.currentIndex() == 2:
            self.Pages.setCurrentIndex(0)
        
        elif self.Pages.currentIndex() == 11:
            self.Pages.setCurrentIndex(4)

        elif self.Pages.currentIndex() == 13:
            self.Pages.setCurrentIndex(12)
            # remove destination_layer after user doen't want to go to a self choosen destination anymore
            destination_layer = uf.getLegendLayerByName(self.iface, "Destination")
            QgsMapLayerRegistry.instance().removeMapLayers([destination_layer])

        elif self.Pages.currentIndex() == 14:
            self.Pages.setCurrentIndex(12)
            # remove destination_layer after user doen't want to go to a self choosen destination anymore
            destination_layer = uf.getLegendLayerByName(self.iface, "Destination")
            QgsMapLayerRegistry.instance().removeMapLayers([destination_layer])

        elif self.Pages.currentIndex() == 3:
            self.Pages.setCurrentIndex(12)
            # remove destination_layer after user doen't want to go to a self choosen destination anymore
            destination_layer = uf.getLegendLayerByName(self.iface, "Destination")
            QgsMapLayerRegistry.instance().removeMapLayers([destination_layer])

        elif self.Pages.currentIndex() == 15:
            self.Pages.setCurrentIndex(11)

        elif self.Pages.currentIndex() == 21:
            self.Pages.setCurrentIndex(14)

        elif self.Pages.currentIndex() == 18:
            self.Pages.setCurrentIndex(13)

        elif self.Pages.currentIndex() == 12:
            self.Pages.setCurrentIndex(1)

        elif self.Pages.currentIndex() == 22:
            self.Pages.setCurrentIndex(13)

        elif self.Pages.currentIndex() == 23:
            self.Pages.setCurrentIndex(14)

        elif self.Pages.currentIndex() == 25:
            self.Pages.setCurrentIndex(22)

        elif self.Pages.currentIndex() == 24:
            self.Pages.setCurrentIndex(23)

        elif self.Pages.currentIndex() == 19:
            self.Pages.setCurrentIndex(17)

        elif self.Pages.currentIndex() == 26:
            self.Pages.setCurrentIndex(6)


        remove_layer = ["Routes", "Buffer", "Obstacle_Temp"]
        # remove selection on all layers
        layers = QgsMapLayerRegistry.instance().mapLayers().values()
        for layer in layers:

            if layer.name() in remove_layer:
                try:
                    QgsMapLayerRegistry.instance().removeMapLayers([layer])
                except:
                    pass

        self.canvas = self.determineCanvas()
        #self.toolPan = QgsMapToolPan(self.canvas)
        #self.canvas.setMapTool(self.toolPan)




    def determineCanvas(self):

        # always ask for index of the current page
        if self.Pages.currentIndex() == 2:
            self.canvas = self.QgsMapCanvas2

        elif self.Pages.currentIndex() == 0:
            self.canvas = self.QgsMapCanvas0

        elif self.Pages.currentIndex() == 1:
            self.canvas = self.QgsMapCanvas1

        elif self.Pages.currentIndex() == 3:
            self.canvas = self.QgsMapCanvas3

        elif self.Pages.currentIndex() == 4:
            self.canvas = self.QgsMapCanvas4

        elif self.Pages.currentIndex() == 5:
            self.canvas = self.QgsMapCanvas5

        elif self.Pages.currentIndex() == 6:
            self.canvas = self.QgsMapCanvas6

        elif self.Pages.currentIndex() == 9:
            self.canvas = self.QgsMapCanvas9

        elif self.Pages.currentIndex() == 10:
            self.canvas = self.QgsMapCanvas10

        elif self.Pages.currentIndex() == 11:
            self.canvas = self.QgsMapCanvas11

        elif self.Pages.currentIndex() == 12:
            self.canvas = self.QgsMapCanvas12

        elif self.Pages.currentIndex() == 13:
            self.canvas = self.QgsMapCanvas13

        elif self.Pages.currentIndex() == 14:
            self.canvas = self.QgsMapCanvas14

        elif self.Pages.currentIndex() == 16:
            self.canvas = self.QgsMapCanvas16

        elif self.Pages.currentIndex() == 17:
            self.canvas = self.QgsMapCanvas17

        elif self.Pages.currentIndex() == 18:
            self.canvas = self.QgsMapCanvas18

        elif self.Pages.currentIndex() == 20:
            self.canvas = self.QgsMapCanvas20

        elif self.Pages.currentIndex() == 21:
            self.canvas = self.QgsMapCanvas21

        elif self.Pages.currentIndex() == 22:
            self.canvas = self.QgsMapCanvas22

        elif self.Pages.currentIndex() == 23:
            self.canvas = self.QgsMapCanvas23


        return self.canvas



    def activateCanvas(self):

        pass

        # #self.smallCanvas = self.determineCanvas()
        #
        # # add all the layers to the small canvas
        # layers = self.iface.legendInterface().layers()
        # canvas_layers = []
        # for layer in layers:
        #     canvas_layers.append(QgsMapCanvasLayer(layer))
        # #self.smallCanvas.setLayerSet(canvas_layers[6:])
        # #self.smallCanvas.setLayerSet(canvas_layers)
        # self.canvas.setLayerSet(canvas_layers)
        #
        # # roads_layer = uf.getLegendLayerByName(self.iface, "Roads")
        # #self.smallCanvas.setLayerSet([canvas_layers[1],])
        #
        # #print self.smallCanvas.layers()
        #
        # # legend = self.iface.legendInterface()
        # # # print legend.isLayerVisible(roads_layer)
        # # legend.setLayerVisible(roads_layer, False)
        #
        #
        # #
        # #self.smallCanvas.layerStateChange()
        # #self.smallCanvas.refreshAllLayers()
        # #
        # #self.smallCanvas.setLayerSet(canvas_layers)
        #
        #
        # # make the pan tool the current map tool
        # #self.toolPan = QgsMapToolPan(self.canvas)
        # #self.canvas.setMapTool(self.toolPan)
        #
        # # refresh small canvas
        # self.canvas.refresh()








    def showEvent(self, event):

        #self.Pages.setCurrentIndex(0)


        # open the QGIS project file
        scenario_open = False
        scenario_file = os.path.join(os.path.dirname(__file__),'data','project_file9.qgs')


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

        #uf.showMessage(self.iface, 'Strong winds! Keep out of red marked areas!', type='Info', lev=1, dur=10)



    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()



    # visualization
    def zoomToSelectedFeature(self, scale, layer):

        box = layer.boundingBoxOfSelected()
        box.scale(scale)
        self.canvas = self.determineCanvas()
        self.canvas.setExtent(box)
        #self.canvas.zoomScale(50000)
        self.canvas.refresh()


    def zoomToLocation(self, scale):

        canvas = self.determineCanvas()

        layer = uf.getLegendLayerByName(self.iface, "Location")

        layer.dataProvider().updateExtents()

        self.canvas.setExtent(layer.extent())
        self.canvas.zoomToSelected()
        #self.canvas.zoomByFactor(0.3)
        self.canvas.zoomScale(scale)





    def showOnMap(self):

        if self.Pages.currentIndex() == 11:
            self.Pages.setCurrentIndex(20)
            layer = uf.getLegendLayerByName(self.iface, "Emergencies")


        elif self.Pages.currentIndex() == 13:
            self.Pages.setCurrentIndex(18)
            layer = uf.getLegendLayerByName(self.iface, "Shelters")
            print('shelter')


        elif self.Pages.currentIndex() == 14:
            self.Pages.setCurrentIndex(21)
            layer = uf.getLegendLayerByName(self.iface, "Hospitals")

        canvas = self.determineCanvas()

        self.canvas.zoomToSelected(layer)
        #self.canvas.zoomByFactor(0.25)
        self.canvas.zoomScale(3000)

    ################################################################################################################
    ############################ user interaction (clicking buttons)################################################
    ################################################################################################################


    # all pages

    # def startNew(self):
    #
    #     self.Pages.setCurrentIndex(0)
    #
    #     #self.canvas.setMapTool(self.toolZoom)
    #
    #     # list of layers that should be removed
    #     remove_layer = ["Routes", "Buffer", "Emergency_Temp", "Destination", "Obstacle_Temp", "Temp_Network"]
    #     #remove_selection_layers = []
    #
    #     # remove selection on all layers
    #     layers = QgsMapLayerRegistry.instance().mapLayers().values()
    #     for layer in layers:
    #         try:
    #             layer.removeSelection()
    #
    #         except:
    #             pass
    #
    #         if layer.name() in remove_layer:
    #
    #             QgsMapLayerRegistry.instance().removeMapLayers([layer])
    #
    #     roads_layer = uf.getLegendLayerByName(self.iface, "Roads")
    #
    #     self.canvas.setExtent(roads_layer.extent())
    #     self.canvas.zoomByFactor(0.98)
    #     self.inputStreet.setText('Streetname')




    def showRouteInfo(self):


        if self.Pages.currentIndex() == 11 or self.Pages.currentIndex() == 20:
            self.Pages.setCurrentIndex(17)
            layer = uf.getLegendLayerByName(self.iface, "Emergencies")
            label = self.label_RouteInfo17
            destinationChosenByClicking = False

        elif self.Pages.currentIndex() == 13 or self.Pages.currentIndex() == 18:
            self.Pages.setCurrentIndex(22)
            layer = uf.getLegendLayerByName(self.iface, "Shelters")
            label = self.label_RouteInfo22
            destinationChosenByClicking = False

        elif self.Pages.currentIndex() == 14 or self.Pages.currentIndex() == 21:
            self.Pages.setCurrentIndex(23)
            layer = uf.getLegendLayerByName(self.iface, "Hospitals")
            label = self.label_RouteInfo23
            destinationChosenByClicking = False

        elif self.Pages.currentIndex() == 3:
            self.Pages.setCurrentIndex(6)
            label = self.label_RouteInfo6
            # no need to create a destination layer, so:
            destinationChosenByClicking = True

        if not destinationChosenByClicking:
            # save selected shelter/hospital/emergency in destination layer
            destination_layer = uf.getLegendLayerByName(self.iface, "Destination")
            if not destination_layer:

                emergency_layer = uf.getLegendLayerByName(self.iface, "Emergencies")
                destination_layer = uf.createTempLayer('Destination', 'POINT', emergency_layer.crs().postgisSrid(), [], [])

                symbol = QgsMarkerSymbolV2.createSimple({'name': 'circle', 'color': 'red'})
                symbol.setSize(0.1)
                destination_layer.rendererV2().setSymbol(symbol)

                uf.loadTempLayer(destination_layer)

            features = layer.selectedFeatures()
            closeFeatID = self.nearestFeature(features[0].geometry().asPoint())
            roads_layer = uf.getLegendLayerByName(self.iface, "Roads")
            closeFeat = uf.getFeatureById(roads_layer, closeFeatID)
            closePoint = closeFeat.geometry().centroid().asPoint()
            # choose location function will actually add it (and remove an older one)
            self.chooseLocation(destination_layer, closePoint)

        routeLength = self.calculateRoute()

        # calculate route info
        routeLength = routeLength/1000
        routeTime = str(int(1.8 * routeLength)+1)
        routeLength = "{:.1f}".format(routeLength)
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText("<font size = 10 color = blue ><b>" + routeTime + " min  </b></font> " +
                      "<font size = 4 color = black >" + str(routeLength)  + " km </font> ")








    # page 0
    def showMap(self):
        self.Pages.setCurrentIndex(16)
        self.canvas = self.determineCanvas()
        location_layer = uf.getLegendLayerByName(self.iface, "Location")
        if not location_layer:
            self.randLocation2()
        self.zoomToLocation(500)
        self.canvas.setMapTool(self.toolPan)



    def showWeather(self):
        self.Pages.setCurrentIndex(7)




    def needHelp(self):

        self.Pages.setCurrentIndex(2)
        self.canvas = self.determineCanvas()
        location_layer = uf.getLegendLayerByName(self.iface, "Location")
        if not location_layer:
            self.randLocation2()
        self.zoomToLocation(500)
        self.canvas.setMapTool(self.toolPan)


    def wantToHelp(self):

        self.Pages.setCurrentIndex(10)
        self.canvas = self.determineCanvas()
        location_layer = uf.getLegendLayerByName(self.iface, "Location")
        if not location_layer:
            self.randLocation2()
        self.zoomToLocation(500)
        self.canvas.setMapTool(self.toolPan)


    # page 1
    def leaveLocation(self):

        self.Pages.setCurrentIndex(12)
        #self.messageRoute()
        self.activateCanvas()


    def stayLocation(self):

        self.Pages.setCurrentIndex(9)
        self.activateCanvas()

        location_layer = uf.getLegendLayerByName(self.iface, "Location")
        roads_layer = uf.getLegendLayerByName(self.iface, "Roads")
        feat = location_layer.getFeatures().next()
        point = feat.geometry().asPoint()
        closeFeatID = self.nearestFeature(point)
        closeFeat = uf.getFeatureById(roads_layer, closeFeatID)

        street = str(closeFeat.attributes()[2])
        district = str(closeFeat.attributes()[3])
        housenumber = random.randrange(1, 150, 1)

        self.input_address.setText(str(street) + ' ' + str(housenumber) + ', ' + district)
        self.frame_details.setAutoFillBackground(True)
        # p = self.frame_details.palette()
        # p.setColor(self.frame_details.backgroundRole(), Qt.red)
        # self.frame_details.setPalette(p)
        # print('changecolor')


    # page 2
    def correctLocationRoute(self):

        self.Pages.setCurrentIndex(1)

        # select second point for routing/ end street for routing
        roads_layer = uf.getLegendLayerByName(self.iface, "Roads")

        self.iface.setActiveLayer(roads_layer)

        # activate and set up the small canvas
        self.canvas = self.determineCanvas()
        self.activateCanvas()

        location_layer = uf.getLegendLayerByName(self.iface, "Location")

        feat = location_layer.getFeatures().next()
        location_layer.select(feat.id())

        # self.zoomToSelectedFeature(1, location_layer)
        # self.canvas.zoomByFactor(0.2)
        self.zoomToLocation(500)

        self.canvas.setMapTool(self.toolPan)





    # page 5 - choose location for blocking (activateLocalization) and save
    def saveBlocking(self):


        roads_layer = uf.getLegendLayerByName(self.iface, "Roads")
        obstacles_layer = uf.getLegendLayerByName(self.iface, "Obstacles")
        obstacles_temp = uf.getLegendLayerByName(self.iface, "Obstacle_Temp")


        selected_sources = roads_layer.selectedFeatures()

        source_points = [feature.geometry().centroid().asPoint() for feature in selected_sources]

        feat = []
        for i, road in enumerate(selected_sources):

            feat.append(QgsFeature(obstacles_layer.pendingFields()))

            feat[i].setAttribute('streetID', road.id())

            feat[i].setGeometry(QgsGeometry.fromPoint(source_points[i]))

        obstacles_layer.dataProvider().addFeatures(feat)
        roads_layer.removeSelection()

        canvas = self.determineCanvas()
        self.canvas.refresh()

        if obstacles_temp:

            if obstacles_temp.featureCount() > 0:

                QgsMapLayerRegistry.instance().removeMapLayers([obstacles_temp])

                uf.showMessage(self.iface, 'The blocking has been saved succesfully!', type='Info', lev=3, dur=4)

            else:

                uf.showMessage(self.iface, 'No road selected! Try again!', type='Info', lev=2, dur=4)

        else:

            uf.showMessage(self.iface, 'No road selected! Try again!', type='Info', lev=2, dur=4)



    # page 7
    def call112(self):

        self.Pages.setCurrentIndex(8)


    # page 10
    def correctLocationHelp(self):
        self.Pages.setCurrentIndex(4)
        self.activateCanvas()
        self.zoomToLocation(500)


    # populate table
    def showEmergency(self):


        emergency_layer = uf.getLegendLayerByName(self.iface, "Emergencies")

        # get start point from location layer
        location_layer = uf.getLegendLayerByName(self.iface, "Location")
        startFeat = uf.getLastFeature(location_layer)
        startPoint = startFeat.geometry().centroid().asPoint()

        # populate table
        values = []
        # only use the first attribute in the list
        for feature in emergency_layer.getFeatures():

            dist = feature.geometry().distance(QgsGeometry.fromPoint(startPoint))
            dist = dist/1000
            name = str(feature.attributes()[1])
            type = str(feature.attributes()[0])
            nOfPeople = str(feature.attributes()[2])
            address = str(feature.attributes()[3])
            phone = str(feature.attributes()[4])



            values.append((name, type, nOfPeople, address, phone, dist, feature.id()))

        values.sort(key=lambda element: element[5], reverse=False)



        self.table_emergencies.clear()
        self.table_emergencies.setColumnCount(7)
        self.table_emergencies.setHorizontalHeaderLabels(["Type","Distance [km]", "Address", "Name","Phone", "No. of People", "ID"])
        self.table_emergencies.setRowCount(len(values))
        for i, item in enumerate(values):
            # i is the table row, items mus tbe added as QTableWidgetItems
            self.table_emergencies.setItem(i,0,QtGui.QTableWidgetItem(str(item[1])))
            self.table_emergencies.setItem(i, 1, QtGui.QTableWidgetItem("{:.1f}".format(item[5])))
            self.table_emergencies.setItem(i, 2, QtGui.QTableWidgetItem(str(item[3])))
            self.table_emergencies.setItem(i,3,QtGui.QTableWidgetItem(item[0]))
            self.table_emergencies.setItem(i, 4, QtGui.QTableWidgetItem(str(item[4])))
            self.table_emergencies.setItem(i, 5, QtGui.QTableWidgetItem(str(item[2])))
            self.table_emergencies.setItem(i, 6, QtGui.QTableWidgetItem(str(item[6])))
        self.table_emergencies.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table_emergencies.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        self.table_emergencies.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        self.table_emergencies.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.ResizeToContents)
        self.table_emergencies.horizontalHeader().setResizeMode(4, QtGui.QHeaderView.ResizeToContents)
        self.table_emergencies.horizontalHeader().setResizeMode(5, QtGui.QHeaderView.ResizeToContents)
        self.table_emergencies.horizontalHeader().setResizeMode(6, QtGui.QHeaderView.ResizeToContents)
        #self.table_hospital.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        #self.table_emergencies.resizeRowsToContents()
        self.table_emergencies.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table_emergencies.verticalHeader().setVisible(False)
        self.table_emergencies.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.table_emergencies.verticalHeader().setDefaultSectionSize(30)


        # select first/closest item

        cols = self.table_emergencies.columnCount()
        for i in range(cols):

            item1 = self.table_emergencies.item(0, i)
            item1.setSelected(True)
            print('setselected')

        self.selectSelectedItem()

    # page 11 - emergencies
    def emergencyChoosen(self):
        self.calculateRoute()
        self.Pages.setCurrentIndex(17)
        self.activateCanvas()



    def deleteEmergencyCheck(self):
        self.Pages.setCurrentIndex(15)


    # page 12
    def showOther(self):

        self.Pages.setCurrentIndex(3)
        self.removeSelectionAll()

        # initialize destination layer
        destination_layer = uf.getLegendLayerByName(self.iface, "Destination")
        if not destination_layer:

            emergency_layer = uf.getLegendLayerByName(self.iface, "Emergencies")
            destination_layer = uf.createTempLayer('Destination', 'POINT', emergency_layer.crs().postgisSrid(), [], [])

            symbol = QgsMarkerSymbolV2.createSimple({'name': 'circle', 'color': 'red'})
            symbol.setSize(3)
            destination_layer.rendererV2().setSymbol(symbol)

            uf.loadTempLayer(destination_layer)

        self.activateCanvas()

        self.zoomToLocation(1000)
        roads_layer = uf.getLegendLayerByName(self.iface, "Roads")
        self.iface.setActiveLayer(roads_layer)
        self.canvas.setMapTool(self.toolPan)


    # populate table
    def showShelter(self):

        self.Pages.setCurrentIndex(13)
        self.activateCanvas()

        shelter_layer = uf.getLegendLayerByName(self.iface, "Shelters")

        # get start point from location layer
        location_layer = uf.getLegendLayerByName(self.iface, "Location")
        startFeat = uf.getLastFeature(location_layer)
        startPoint = startFeat.geometry().centroid().asPoint()

        # populate table
        values = []
        # get all the attributes
        for feature in shelter_layer.getFeatures():

            dist = feature.geometry().distance(QgsGeometry.fromPoint(startPoint))
            dist = dist/1000

            type = str(feature.attributes()[2])
            name = str(feature.attributes()[3])

            if str(name) == 'NULL':
                name = type
            namename = name + ' (' + type + ')'
            values.append((feature.id(), namename, dist))

        values.sort(key=lambda element: element[2], reverse=False)

        self.table_shelter.clear()
        self.table_shelter.setColumnCount(3)
        self.table_shelter.setHorizontalHeaderLabels(["Name","Distance [km]", "ID"])
        self.table_shelter.setRowCount(len(values))
        for i, item in enumerate(values):
            # i is the table row, items mus tbe added as QTableWidgetItems
            self.table_shelter.setItem(i,0,QtGui.QTableWidgetItem(item[1]))
            self.table_shelter.setItem(i,1,QtGui.QTableWidgetItem("{:.1f}".format(item[2])))
            self.table_shelter.setItem(i, 2, QtGui.QTableWidgetItem(str(item[0])))
        self.table_shelter.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        #self.table_shelter.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.table_shelter.resizeRowsToContents()
        self.table_shelter.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table_shelter.verticalHeader().setVisible(False)
        self.table_shelter.verticalHeader().setDefaultSectionSize(30)


        # select first/closest item, or better whole row
        cols = self.table_shelter.columnCount()
        for i in range(cols):

            item1 = self.table_shelter.item(0, i)
            item1.setSelected(True)

        self.selectSelectedItem()


    # populate table
    def showHospital(self):

        self.Pages.setCurrentIndex(14)
        self.activateCanvas()


        hospital_layer = uf.getLegendLayerByName(self.iface, "Hospitals")

        # get start point from location layer
        location_layer = uf.getLegendLayerByName(self.iface, "Location")
        startFeat = uf.getLastFeature(location_layer)
        startPoint = startFeat.geometry().centroid().asPoint()

        # populate table
        values = []
        # get all the attributes
        for feature in hospital_layer.getFeatures():

            dist = feature.geometry().distance(QgsGeometry.fromPoint(startPoint))
            dist = dist/1000

            name = str(feature.attributes()[3])

            values.append((feature.id(), name, dist))

        values.sort(key=lambda element: element[2], reverse=False)

        self.table_hospital.clear()
        self.table_hospital.setColumnCount(3)
        self.table_hospital.setHorizontalHeaderLabels(["Name","Distance [km]", "ID"])
        self.table_hospital.setRowCount(len(values))
        for i, item in enumerate(values):
            # i is the table row, items mus tbe added as QTableWidgetItems
            self.table_hospital.setItem(i,0,QtGui.QTableWidgetItem(item[1]))
            self.table_hospital.setItem(i,1,QtGui.QTableWidgetItem("{:.1f}".format(item[2])))
            self.table_hospital.setItem(i, 2, QtGui.QTableWidgetItem(str(item[0])))
        self.table_hospital.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        #self.table_hospital.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.table_hospital.resizeRowsToContents()
        self.table_hospital.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table_hospital.verticalHeader().setVisible(False)
        self.table_hospital.verticalHeader().setDefaultSectionSize(30)


        # select first/closest item, or better whole row
        cols = self.table_hospital.columnCount()
        for i in range(cols):

            item1 = self.table_hospital.item(0, i)
            item1.setSelected(True)

        self.selectSelectedItem()



    # page 15 - delete emergency
    def deleteEmergency(self):

        emergency_layer = uf.getLegendLayerByName(self.iface, "Emergencies")
        emergency_layer.startEditing()
        emergency_layer.deleteSelectedFeatures()
        emergency_layer.commitChanges()
        self.canvas.refresh()
        self.Pages.setCurrentIndex(11)
        self.activateCanvas()
        self.showEmergency()
        uf.showMessage(self.iface, 'The emergency has been removed from the list!', type='Info', lev=3, dur=4)


    # page 17
    def startNavigation(self):

        if self.Pages.currentIndex() == 17:
            self.Pages.setCurrentIndex(19)

        elif self.Pages.currentIndex() == 23:
            self.Pages.setCurrentIndex(24)

        elif self.Pages.currentIndex() == 22:
            self.Pages.setCurrentIndex(25)

        elif self.Pages.currentIndex() == 6:
            self.Pages.setCurrentIndex(26)


    # page 18
    def changeRoute(self):

        self.calculateRoute()
        canvas = self.determineCanvas()
        self.canvas.refresh()

    # localization
    def randLocation2(self):

        emergency_layer = uf.getLegendLayerByName(self.iface, "Emergencies")

        rand_location = uf.createTempLayer('Location', 'POINT', emergency_layer.crs().postgisSrid(), [], [])

        feat = QgsFeature(rand_location.pendingFields())

        rand_x = random.randrange(84500, 100700, 1)
        rand_y = random.randrange(428500, 443900, 1)

        #rand_x = 94790
        #rand_y = 436014

        rand_point = QgsPoint(rand_x, rand_y)

        feat.setGeometry(QgsGeometry.fromPoint(rand_point))

        rand_location.dataProvider().addFeatures([feat])

        symbol = QgsMarkerSymbolV2.createSimple({'name': 'circle', 'color': 'yellow'})
        symbol.setSize(3)
        rand_location.rendererV2().setSymbol(symbol)

        uf.loadTempLayer(rand_location)
        self.activateCanvas()
        self.canvas = self.determineCanvas()

        self.iface.setActiveLayer(rand_location)

        feat = uf.getLastFeature(rand_location)

        rand_location.removeSelection()
        rand_location.select(feat.id())

        self.canvas.refresh()



    # get the point when the user clicks on the canvas
    def activateLocalization(self):

        self.canvas = self.determineCanvas()

        # generate canvas clicked signal here so it uses the right canvas
        self.emitPoint = QgsMapToolEmitPoint(self.canvas)
        self.emitPoint.canvasClicked.connect(self.getPoint)

        # activate coordinate capture tool
        self.canvas.setMapTool(self.emitPoint)

    def getPoint(self, mapPoint, mouseButton):
        # change tool so you don't get more than one POI
        #self.canvas.unsetMapTool(self.emitPoint)
        #self.canvas.setMapTool(self.userTool)

        # Get the click
        if mapPoint:

            # choose first location to help          # choose first location to help out
            if self.Pages.currentIndex() == 2 or self.Pages.currentIndex() == 10:

                randloc_layer = uf.getLegendLayerByName(self.iface, "Location")

                self.chooseLocation(randloc_layer, mapPoint)


            # choose destination by clicking
            elif self.Pages.currentIndex() == 3:

                roads_layer = uf.getLegendLayerByName(self.iface, "Roads")
                roads_layer.removeSelection()
                destination_layer = uf.getLegendLayerByName(self.iface, "Destination")

                #this is only still needed if user doesn't come from choose other, e.g. comes back from route
                if not destination_layer:

                    emergency_layer = uf.getLegendLayerByName(self.iface, "Emergencies")

                    destination_layer = uf.createTempLayer('Destination', 'POINT', emergency_layer.crs().postgisSrid(), [], [])

                    symbol = QgsMarkerSymbolV2.createSimple({'name': 'circle', 'color': 'red'})
                    symbol.setSize(3)
                    destination_layer.rendererV2().setSymbol(symbol)

                    uf.loadTempLayer(destination_layer)
                    self.activateCanvas()

                self.chooseLocation(destination_layer, mapPoint)



            # choose blocking location
            elif self.Pages.currentIndex() == 5:

                obstacle_temp = uf.getLegendLayerByName(self.iface, "Obstacle_Temp")
                roads_layer = uf.getLegendLayerByName(self.iface, "Roads")

                #this is only still needed if user doesn't come from helpAtEmergency, e.g. clicks save blocking before clicks choose blocked roads
                if not obstacle_temp:

                    obstacle_layer = uf.getLegendLayerByName(self.iface, "Obstacles")

                    obstacle_temp = uf.createTempLayer('Obstacle_Temp', 'POINT', obstacle_layer.crs().postgisSrid(), [], [])
                    symbol = QgsMarkerSymbolV2.createSimple({'name': 'circle', 'color': 'blue'})
                    symbol.setSize(3)
                    obstacle_temp.rendererV2().setSymbol(symbol)

                    uf.loadTempLayer(obstacle_temp)
                    #self.activateCanvas()

                # get featID of closest road
                featID = self.nearestFeature(mapPoint)
                feat = uf.getFeatureById(roads_layer, featID)
                blockedPoint = feat.geometry().centroid().asPoint()
                self.chooseLocation(obstacle_temp, blockedPoint)




    def chooseLocation(self, layer, mapPoint):

        # this function lets the user set his own location and deletes the old one
        # and deletes the previous one if the user clicks multiple times
        # additionally it is used to save the obstacles and destinations for shelter/hospital/emergency

        layer.startEditing()

        if layer.featureCount() > 0 and layer.name() != "Obstacle_Temp":
            feat_old = uf.getLastFeature(layer)
            layer.deleteFeature(feat_old.id())

        feat_new = QgsFeature(layer.pendingFields())
        feat_new.setGeometry(QgsGeometry.fromPoint(mapPoint))
        layer.dataProvider().addFeatures([feat_new])
        uf.loadTempLayer(layer)
        layer.commitChanges()
        layer.dataProvider().updateExtents()


        self.canvas = self.determineCanvas()
        #self.canvas.refresh()



    def chooseEnd(self):

        self.activateLocalization()


    def searchStreet(self):

        roads_layer = uf.getLegendLayerByName(self.iface, "Roads")
        roads_layer.removeSelection()

        street = self.inputStreet.text()

        roads_layer.removeSelection()

        feat = uf.getFeaturesByListValues(roads_layer, 'stt_naam', [street])

        if not feat:
            uf.showMessage(self.iface, 'Street not found. Try again!', type='Info', lev=2, dur=4)
            return
        else:
            sfeat = feat.iterkeys().next()

        # select the searched road
        roads_layer.select(sfeat)

        # add the centroid of the searched road to the destionation layer
        destination_layer = uf.getLegendLayerByName(self.iface, "Destination")

        streetFeat = uf.getFeatureById(roads_layer, sfeat)

        mapPoint = streetFeat.geometry().centroid().asPoint()
        self.chooseLocation(destination_layer, mapPoint)

        canvas = self.determineCanvas()

        self.canvas.zoomToSelected(roads_layer)
        self.canvas.zoomByFactor(10)

        # return the featureID
        return sfeat


    def nearestFeature(self, mapPoint):

        layerData = []

        layer = uf.getLegendLayerByName(self.iface, "Roads")

        if self.Pages.currentIndex() == 2 or self.Pages.currentIndex() == 6:

            layer.removeSelection()

        shortestDistance = float("inf")
        closestFeatureId = -1

        # Loop through all features in the layer
        for f in layer.getFeatures():
            dist = f.geometry().distance(QgsGeometry.fromPoint(mapPoint))
            #print(f.id())
            #print(dist)

            if dist < shortestDistance:
                shortestDistance = dist
                closestFeatureId = f.id()

        info = (layer, closestFeatureId, shortestDistance)
        layerData.append(info)



        if not len(layerData) > 0:
            # Looks like no vector layers were found - do nothing
            return

        # Sort the layer information by shortest distance
        layerData.sort(key=lambda element: element[2], reverse=False)

        # Select the closest feature
        layerWithClosestFeature, closestFeatureId, shortestDistance = layerData[0]
        #print(closestFeatureId)

        if self.Pages.currentIndex() == 3 or self.Pages.currentIndex() == 5 or self.Pages.currentIndex() == 13 or self.Pages.currentIndex() == 14 or self.Pages.currentIndex() == 11:
            layerWithClosestFeature.select(closestFeatureId)

        return closestFeatureId



    # analysis

    def getNetwork(self):
        roads_layer = uf.getLegendLayerByName(self.iface, "Roads")
        if roads_layer:
            # see if there is an obstacles layer to subtract roads from the network
            obstacles_layer = uf.getLegendLayerByName(self.iface, "Obstacles")
            if obstacles_layer:
                print('yes there is an obstacle')

                # remove features by id here, from obstacle layer, where I give the obstacle features the same id that the corresponding road has


                # first dublicate the roads_layer
                feats = [feat for feat in roads_layer.getFeatures()]

                road_network = uf.createTempLayer('Temp_Network','LINESTRING',roads_layer.crs().postgisSrid(),[],[])

                mem_layer_data = road_network.dataProvider()
                attr = roads_layer.dataProvider().fields().toList()
                mem_layer_data.addAttributes(attr)
                road_network.updateFields()
                mem_layer_data.addFeatures(feats)
                #QgsMapLayerRegistry.instance().addMapLayer(road_network)

                road_network.startEditing()

                for obstacles in obstacles_layer.getFeatures():

                    feat = uf.getFeatureById(road_network, obstacles['streetID']+1)

                    road_network.select(feat.id())

                a=road_network.deleteSelectedFeatures()
                print(a)

                road_network.commitChanges()

            else:
                road_network = roads_layer
            return road_network
        else:
            return


    def buildNetwork(self):
        self.network_layer = self.getNetwork()

        road_layer = uf.getLegendLayerByName(self.iface, "Roads")


        location_layer = uf.getLegendLayerByName(self.iface, "Location")
        location_layer.removeSelection()
        startFeat = uf.getLastFeature(location_layer)
        startPoint = startFeat.geometry().centroid().asPoint()
        startID = self.nearestFeature(startPoint)

        destination_layer = uf.getLegendLayerByName(self.iface, "Destination")
        if destination_layer:
            endFeat = uf.getLastFeature(destination_layer)
            endPoint = endFeat.geometry().centroid().asPoint()
            endID = self.nearestFeature(endPoint)
            print('yes dest')

            road_layer.select([startID, endID])

        else:
            # end is already selected by setSelectedItem function for the selected shelter or hospital or emergency
            road_layer.select([startID])
            for feat in road_layer.selectedFeatures():
                print(feat.id())

            print('attention: no destination!! if not selected by setSelectedItem function!!')


        if self.network_layer:
            # get the points to be used as origin and destination
            # in this case gets the centroid of the selected features
            selected_sources = road_layer.selectedFeatures()
            source_points = [feature.geometry().centroid().asPoint() for feature in selected_sources]
            # build the graph including these points
            if len(source_points) > 1:
                self.graph, self.tied_points = uf.makeUndirectedGraph(self.network_layer, source_points)
                # the tied points are the new source_points on the graph
                if self.graph and self.tied_points:
                    text = "network is built for %s points" % len(self.tied_points)
                    print(text)
        return


    def calculateRoute(self):
        self.buildNetwork()
        canvas = self.determineCanvas()
        self.canvas.setMapTool(self.toolPan)
        # origin and destination must be in the set of tied_points
        options = len(self.tied_points)
        if options > 1:
            # origin and destination are given as an index in the tied_points list
            origin = 0
            destination = random.randint(1,options-1)
            # calculate the shortest path for the given origin and destination
            path = uf.calculateRouteDijkstra(self.graph, self.tied_points, origin, destination)
            # store the route results in temporary layer called "Routes"
            routes_layer = uf.getLegendLayerByName(self.iface, "Routes")
            # create one if it doesn't exist
            if not routes_layer:
                attribs = ['id']
                types = [QtCore.QVariant.String]
                routes_layer = uf.createTempLayer('Routes','LINESTRING',self.network_layer.crs().postgisSrid(), attribs, types)
                uf.loadTempLayer(routes_layer)
            # insert route line
            for route in routes_layer.getFeatures():
                print route.id()
            uf.insertTempFeatures(routes_layer, [path], [['testing',100.00]])
            buffer = processing.runandload('qgis:fixeddistancebuffer',routes_layer,10.0,5,False,None)
            buffer_layer = uf.getLegendLayerByName(self.iface, "Buffer")

            # style of route layer
            symbols = buffer_layer.rendererV2().symbols()
            symbol = symbols[0]
            symbol.setColor(QtGui.QColor.fromRgb(50, 50, 250))
            self.activateCanvas()

            #self.legendInterface().refreshLayerSymbology(self.vlayer)




        # zoom on route
        layer = uf.getLegendLayerByName(self.iface, "Roads")
        self.zoomToSelectedFeature(1.5, layer)
        layer.removeSelection()

        # length of route
        route = routes_layer.getFeatures().next()
        return route.geometry().length()





    def dispEmergency(self, mapPoint):

        # create temp layer with point

        location_layer = uf.getLegendLayerByName(self.iface, "Location")
        QgsMapLayerRegistry.instance().removeMapLayers([location_layer])



        emergency_layer = uf.getLegendLayerByName(self.iface, "Emergencies")
        emergency_temp = uf.getLegendLayerByName(self.iface, "Emergency_Temp")


        if emergency_temp:

            QgsMapLayerRegistry.instance().removeMapLayers([emergency_temp])


        emergency_temp = uf.createTempLayer('Emergency_Temp', 'POINT', emergency_layer.crs().postgisSrid(), [], [])

        symbol = QgsMarkerSymbolV2.createSimple({'name': 'circle', 'color': 'yellow'})
        symbol.setSize(3)
        emergency_temp.rendererV2().setSymbol(symbol)


        #use this in the future:
        #insertTempFeatures(layer, coordinates, attributes)

        feat = QgsFeature(emergency_temp.pendingFields())

        feat.setGeometry(QgsGeometry.fromPoint(mapPoint))

        emergency_temp.dataProvider().addFeatures([feat])

        uf.loadTempLayer(emergency_temp)




    def saveEmergency(self):


        # first get the point, either from location or emergency_temp layer
        emergency_temp = uf.getLegendLayerByName(self.iface, "Emergency_Temp")
        location_layer = uf.getLegendLayerByName(self.iface, "Location")

        if location_layer:
            point = location_layer.getFeatures().next()
            QgsMapLayerRegistry.instance().removeMapLayers([location_layer])
        elif emergency_temp:
            point = emergency_temp.getFeatures().next()
            QgsMapLayerRegistry.instance().removeMapLayers([emergency_temp])
        else:
            return


        # now safe in (permanent) emergency layer
        emergency_layer = uf.getLegendLayerByName(self.iface, "Emergencies")
        emergency_layer.dataProvider().addFeatures([point])
        emergency_layer.dataProvider().updateExtents()
        self.iface.setActiveLayer(emergency_layer)
        self.canvas.refresh()
        uf.showMessage(self.iface, 'Your emergency has been added to the list!', type='Info', lev=3, dur=6)


    def saveInformation(self):

        self.saveEmergency()

        emergency_layer = uf.getLegendLayerByName(self.iface, "Emergencies")

        # req = QgsFeatureRequest()
        #
        # req.setFilterFid(emergency_layer.allFeatureIds()[-1])
        #
        # feat = emergency_layer.getFeatures(req).next()

        feat = uf.getLastFeature(emergency_layer)

        emergency_layer.startEditing()


        emergency_layer.changeAttributeValue(feat.id(), 0, self.input_description.document().toPlainText())
        emergency_layer.changeAttributeValue(feat.id(), 1, self.input_name.text())
        emergency_layer.changeAttributeValue(feat.id(), 2, self.input_nOfPeople.value())
        emergency_layer.changeAttributeValue(feat.id(), 3, self.input_address.text())
        emergency_layer.changeAttributeValue(feat.id(), 4, self.input_phone.text())

        emergency_layer.commitChanges()

        self.canvas.refresh()

        #uf.showMessage(self.iface, 'Your information has been saved succesfully!', type='Info', lev=3, dur=4)


    def selectSelectedItem(self):

        remove_layer = ["Routes", "Buffer"]

        # remove selection on all layers
        layers = QgsMapLayerRegistry.instance().mapLayers().values()
        for layer in layers:

            try:
                layer.removeSelection()

            except:
                pass

            if layer.name() in remove_layer:
                QgsMapLayerRegistry.instance().removeMapLayers([layer])


        # determine active table
        if self.Pages.currentIndex() == 13:
            layer = uf.getLegendLayerByName(self.iface, "Shelters")
            self.table = self.table_shelter
            # coloumn of featureID
            col = 2

        elif self.Pages.currentIndex() == 14:
            self.table = self.table_hospital
            col = 2
            layer = uf.getLegendLayerByName(self.iface, "Hospitals")


        elif self.Pages.currentIndex() == 11:
            self.table = self.table_emergencies
            col = 6
            layer = uf.getLegendLayerByName(self.iface, "Emergencies")


        self.iface.setActiveLayer(layer)

        selectedItem = self.table.selectedItems()[0]
        row=selectedItem.row()

        featID = self.table.item(row, col).text()
        layer.select(int(featID))



    def messageRoute(self):

        msgBox = QtGui.QMessageBox()
        msgBox.setTextFormat(QtCore.Qt.RichText)


        text = (

        "<p>The municipality provides temporary accommodation and initial medical aid in a number of emergency shelters in the city." +
        "To choose from a list of shelters select the" +
        "< font color = green > GREEN HOUSE < / font > </p>" +

        "<font color = black> If you need further medical attention select the </font>" +
        "< font color = red > RED CROSS </ font>")

        msgBox.setText(text)
        msgBox.exec_()



    def removeSelectionAll(self):

        layers = self.iface.legendInterface().layers()
        for layer in layers:
            try:
                layer.removeSelection()
            except:
                pass




































