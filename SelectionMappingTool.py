from qgis.core import *
from qgis.core import QgsGeometry, QgsMapLayerRegistry

from qgis.gui import *
from qgis.gui import QgsMapTool
from qgis.networkanalysis import *

from PyQt4.QtGui import QCursor, QPixmap, QAction
from PyQt4.QtCore import Qt, pyqtSignal, QPoint
from . import utility_functions as uf

# this is for adding the "external" folder to the system path, because the QGIS python is only looking in the system path for python packages
# you can see that this works by doing import sys, sys.path inside the QGIS python console
import os, sys
#sys.path.append(os.path.join(os.path.dirname(__file__), "external"))


################################################################################################################
###################################################### SELECT-TOOL #############################################
################################################################################################################
class SelectionTool(QgsMapTool, QAction):
    def __init__(self, widget, canvas, action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.action = action
        self.widget = widget
        #self.book = self.widget.book

        self.cursor = QCursor(Qt.PointingHandCursor)

        # layers need to be turned on when PointTool is opened for the first time, otherwise error when trying to access these layers
        self.infra_layer = uf.getCanvasLayerByName(self.canvas, "Infrastructure Projects")
        self.housing_layer = uf.getCanvasLayerByName(self.canvas, "Housing Plans")

        #self.canvas.setMapTool().connect(self.deactivate)
        #self.canvas.mapToolSet.connect(self.deactivate)




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


