# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanningToolClass
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QPoint, QSize
from PyQt4.QtGui import QAction, QIcon, QToolBar, QComboBox, QColor
from qgis.gui import QgsMapTool


#from . import utility_functions as uf
import utility_functions as uf


# Initialize Qt resources from file resources.py
import resources

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "external"))

import xlwings as xw

# Import the code for the DockWidget
from planning_tool_dockwidget import IndicatorsChartDocked, PointTool
#from planning_tool_dockwidget import HousingInput, InfrastructureInput
#from planning_tool_dockwidget import IndicatorsChart
from nearest_feature_map_tool import NearestFeatureMapTool

import os.path


class PlanningToolClass:
    """QGIS Plugin Implementation."""

    # initializes plugin when qgis is started, or loaded with plugin reloader
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        # iface literally means interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.canvas.setSelectionColor(QColor("green"))


        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PlanningToolClass_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.transl(u'&Regional Game Mobiele Stad')
        # TODO: We are going to let the user set this up in a future iteration
        self.planning_toolbar = self.iface.addToolBar(u'RGMSToolbar')
        self.planning_toolbar.setObjectName(u'mRGMSToolbar')


        print "** INITIALIZING PlanningToolClass"

        self.pluginIsActive = False
        self.ic = None
        self.app = None
        self.book = None

    # noinspection PyMethodMayBeStatic
    def transl(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PlanningToolClass', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.planning_toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # DO NOT FORGET TO ALSO CHANGE ICON PATH IN resources.qrc AND metadata.txt FILES
        # text is the text that appears when you hover over the plugin icon in the toolbar
        icon_path = ':/plugins/PlanningToolClass/icons/rgms.png'
        self.rgmsAction = self.add_action(
            icon_path,
            text=self.transl(u'Planning Tool'),
            callback=self.run,
            parent=self.iface.mainWindow())




    #--------------------------------------------------------------------------
    # unload plugin

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # TODO: this is only printed when the plugin is reopened, is that correct?
        print "** CLOSING PlanningToolClass"

        # disconnects
        self.ic.closingPlugin.disconnect(self.onClosePlugin)

        # skip first action, because it is the plugin icon itself
        iterAction = iter(self.actions)
        next(iterAction)
        for action in iterAction:
            self.iface.removePluginMenu(
                self.transl(u'&Regional Game Mobiele Stad'),
                action)
            self.planning_toolbar.removeAction(action)

        for separator in self.separators:
            self.planning_toolbar.removeAction(separator)


        # toolbars that were present before opening plugin are restored here
        for i, toolbar in enumerate(self.toolbars0):
            toolbar.setVisible(self.toolbars0_visible[i])

        ### layer tree icon size
        self.iface.layerTreeView().setIconSize(self.tree_size)

        # and put the planning_toolbar back in place, i.e. dock it
        #### this is the source of the problem that I get a new toolbar when reloading the plugin, as this actually opens a new toolbar instead of just adding the existing planning_toolbar
        #### basically it is not even needed
        #self.iface.addToolBar(self.planning_toolbar)
        #TODO: what needs to be done here instead is simply docking self.planning_toolbar, but I cannot seems to get that done.

        # close excel sheet
        if self.book:
            self.book.close()
            self.app.kill()

        self.rgmsAction.setVisible(True)

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        print "** UNLOAD PlanningToolClass"
        #self.iface.mainWindow().removeToolBar(self.planning_toolbar)


        if self.pluginIsActive:
            print "active"
            self.onClosePlugin()

        for action in self.actions:
            self.iface.removePluginMenu(
                self.transl(u'&Regional Game Mobiele Stad'),
                action)
            self.iface.removeToolBarIcon(action)

        # remove the toolbar
        del self.planning_toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""


        if not self.pluginIsActive:
            self.pluginIsActive = True

            # load project file
            self.loadProjectFile()

            #### toolbar stuff:
            # gathering all toolbars of the QGIS GUI and their visibility state
            # and save them as global variables
            # then set all of them invisible for the PlanningTool start
            self.toolbars0 = self.iface.mainWindow().findChildren(QToolBar)
            self.toolbars0_visible = []

            #### layertree icon size
            self.tree_size = self.iface.layerTreeView().iconSize()
            self.iface.layerTreeView().setIconSize(QSize(50, 50))

            # set toolbars invisible
            for toolbar in self.toolbars0:
                self.toolbars0_visible.append(toolbar.isVisible())
                toolbar.setVisible(False)

            # show planning toolbar
            self.planning_toolbar.show()
            # update/ add additional stuff to planning toolbar
            self.updateToolbar()


            # TODO: not working anymore with the new QGIS project file,
            # thus also the "home" button in the toolbar not working anymore
            #self.zoomToInfrastructureInvestments()


            # prepare excel file
            self.excel_file = os.path.join(os.path.dirname(__file__), 'data', 'excel_data.xlsm')
            #self.app = xw.App(visible=False)
            #self.book = self.app.books.open(self.excel_file)

            ## initialise IndicatorsChart widget here
            # dockwidget does not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.ic == None:
                # Create the dockwidget (after translation) and keep reference
                self.ic = IndicatorsChartDocked(self.iface, book=self.book)
                # maptool = MapToolEmitPoint(self.canvas)
                # self.canvas.setMapTool(maptool)
                # maptool.canvasDoubleClicked.connect(self.handleDoubleClick)


            # connect to provide cleanup on closing of dockwidget
            self.ic.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.ic)

            self.ic.setWindowTitle(self.transl(u'&Regional Game Mobiele Stad'))
            self.ic.show()

            #self.ic = IndicatorsChartDocked(self.iface, book=self.book)






    # ### helper functions
    # def handleDoubleClick(self, point, buttons):
    #     # do stuff with point and buttons
    #     print "double-clicked"

    def loadProjectFile(self):


        # open the QGIS project file
        scenario_open = False
        scenario_file = os.path.join(os.path.dirname(__file__),'data','project_file22.qgs')


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


    def updateToolbar(self):

        self.rgmsAction.setVisible(False)

        # save
        icon_path = ':/plugins/PlanningToolClass/icons/save.png'
        self.add_action(
            icon_path,
            text=self.transl(u'Save'),
            callback=self.openHousingInput,
            parent=self.iface.mainWindow())

        ##toolbar icons /  add the map navigation actions
        # separator
        self.separators = []
        self.separators.append(self.planning_toolbar.addSeparator())


        # zoom to infrastructure investments / home
        icon_path = ':/plugins/PlanningToolClass/icons/home.png'
        self.add_action(
            icon_path,
            text=self.transl(u'Zoom to Infrastructure Investments'),
            callback=self.zoomToInfrastructureInvestments,
            parent=self.iface.mainWindow())

        # # pan - only needed for OSX version
        self.planning_toolbar.addAction(self.iface.actionPan())
        self.actions.append(self.iface.actionPan())

        # touch
        self.planning_toolbar.addAction(self.iface.actionTouch())
        self.actions.append(self.iface.actionTouch())

        # # zoom window
        # self.planning_toolbar.addAction(self.iface.actionZoomIn())
        # self.actions.append(self.iface.actionZoomIn())

        # zoom to previous extent
        self.planning_toolbar.addAction(self.iface.actionZoomLast())
        self.actions.append(self.iface.actionZoomLast())

        # identify features
        self.planning_toolbar.addAction(self.iface.actionIdentify())
        self.actions.append(self.iface.actionIdentify())



        # # select municipality, bookmarks button and combo box, the combo box is filled with the unique GEMEENTE fields in zoomToMunicipality
        # self.municipalityCombo = QComboBox(self.iface.mainWindow())
        # self.municipalityComboAction = self.planning_toolbar.addWidget(self.municipalityCombo)
        # self.municipalityCombo.setToolTip("Municipalities")
        # self.actions.append(self.municipalityComboAction)
        #
        # layer_housing = uf.getLegendLayerByName(self.iface, "Housing_Plans")
        #
        # idx = layer_housing.fieldNameIndex('GEMEENTE')
        # municipalities = layer_housing.uniqueValues(idx)
        # for municipality in municipalities:
        #     #print str(municipality)
        #     self.municipalityCombo.addItem("'"+str(municipality)+"'")
        #
        # icon_path = ':/plugins/PlanningToolClass/icons/magnifier.png'
        # self.add_action(
        #     icon_path,
        #     text=self.transl(u'Zoom to Municipality'),
        #     callback=self.zoomToMunicipality,
        #     parent=self.iface.mainWindow())

        #### zoom to package
        # self.packageCombo = QComboBox(self.iface.mainWindow())
        # self.packageComboAction = self.planning_toolbar.addWidget(self.packageCombo)
        # self.packageCombo.setToolTip("Packages")
        # self.actions.append(self.packageComboAction)
        #
        # layer_infra = uf.getLegendLayerByName(self.iface, "Infrastructure_Investments")
        #
        # idx = layer_infra.fieldNameIndex('Package')
        # packages = layer_infra.uniqueValues(idx)
        # for package in packages:
        #     #print str(package)
        #     self.packageCombo.addItem("'"+str(package)+"'")
        #
        # icon_path = ':/plugins/PlanningToolClass/icons/magnifier.png'
        # self.add_action(
        #     icon_path,
        #     text=self.transl(u'Zoom to Package'),
        #     callback=self.zoomToPackage,
        #     parent=self.iface.mainWindow())

        # separator
        self.separators.append(self.planning_toolbar.addSeparator())

        # self.planning_toolbar.addAction(self.iface.actionSelect())
        # self.actions.append(self.iface.actionSelect())


        # add infrastructure input
        icon_path = ':/plugins/PlanningToolClass/icons/select_2.png'
        self.iiAction = self.add_action(
            icon_path,
            text=self.transl(u'Select'),
            callback=self.activateSelectionTool,
            parent=self.iface.mainWindow())
        self.iiAction.setObjectName('mSelectAction')
        self.iiAction.setCheckable(True)


        # # add calculate indicators button
        # icon_path = ':/plugins/PlanningToolClass/icons/calculator.png'
        # self.add_action(
        #     icon_path,
        #     text=self.transl(u'Calculate Indicators'),
        #     callback=self.openIndicatorsChart,
        #     parent=self.iface.mainWindow())

        # separator
        self.separators.append(self.planning_toolbar.addSeparator())

        # close plugin
        icon_path = ':/plugins/PlanningToolClass/icons/close.png'
        self.add_action(
            icon_path,
            text=self.transl(u'Close Plugin'),
            callback=self.onClosePlugin,
            parent=self.iface.mainWindow())


        # extra necessary actions
        # self.planning_toolbar.addAction(self.iface.actionZoomActualSize())
        # self.planning_toolbar.addAction(self.iface.actionZoomFullExtent())
        # self.planning_toolbar.addAction(self.iface.actionZoomToLayer())
        # self.planning_toolbar.addAction(self.iface.actionZoomToSelected())
        # self.planning_toolbar.addAction(self.iface.actionDraw())
        # self.planning_toolbar.addAction(self.iface.actionSelect())



    def zoomToInfrastructureInvestments(self):


        # zoom on infrastructure investments layer extent / home
        uf.zoomToLayer(self.iface, "Infrastructure_Investments")


    def zoomToMunicipality(self):

        # get the Housing_Projects layer
        layer = uf.getLegendLayerByName(self.iface, "Housing_Plans")
        # remove current selections on this layer
        layer.removeSelection()
        # get the currently selected item in the municipality combo box
        gemeente = str(self.municipalityCombo.currentText())
        # select the features for this municipality
        uf.selectFeaturesByExpression(layer, '"GEMEENTE" IS ' + gemeente)
        # make box around the features
        box = layer.boundingBoxOfSelected()
        # unselect features again
        layer.removeSelection()
        # zoom to the box
        self.canvas.setExtent(box)
        self.canvas.refresh()


    def zoomToPackage(self):

        # get the Housing_Projects layer
        layer1 = uf.getLegendLayerByName(self.iface, "Housing_Plans")
        layer2 = uf.getLegendLayerByName(self.iface, "Infrastructure_Investments")
        # remove current selections on this layer
        layer1.removeSelection()
        layer2.removeSelection()
        # get the currently selected item in the municipality combo box
        package = str(self.packageCombo.currentText())
        # select the features for this municipality
        uf.selectFeaturesByExpression(layer1, '"Package" IS ' + package)
        uf.selectFeaturesByExpression(layer2, '"Package" IS ' + package)
        # make box around the features
        box1 = layer1.boundingBoxOfSelected()
        box2 = layer2.boundingBoxOfSelected()
        box1.combineExtentWith(box2)
        # unselect features again
        layer1.removeSelection()
        layer2.removeSelection()
        # zoom to the box
        self.canvas.setExtent(box1)
        self.canvas.refresh()


### activate map Tool
    def activateSelectionTool(self):

        mapTool = PointTool(widget=self.ic, canvas=self.canvas, action=self.iiAction)
        self.canvas.setMapTool(mapTool)
        # self.iiAction.setChecked(True)
        uf.showMessage(self.iface, 'tap on polygon to select, double-tap on canvas to remove selection', type='Info', lev=1, dur=5)


    #### open dialogs:

    def openHousingInput(self):

        layer = self.iface.activeLayer()
        projectName, ids = uf.getFieldValues(layer, 'NAAMPLAN', null=False, selection=True)
        package, ids = uf.getFieldValues(layer, 'Package', null=False, selection=True)
        if layer:
            if str(layer.name()) != 'Housing_Plans':
                uf.showMessage(self.iface, "please select a housing project first", type='Info', lev=1, dur=5)
                return
        else:
            uf.showMessage(self.iface, "please select a housing project first", type='Info', lev=1, dur=5)
            return

        if len(projectName) == 1:
            self.hi = HousingInput(self.iface, chart=self.ic)
            self.hi.show()
            self.hi.move(QPoint(450, 150))
            self.hi.naamplanLabel.setText(str(projectName[0]))
            self.hi.packageLabel.setText('PACKAGE ' + str(package[0][-1:]))
        else:
            uf.showMessage(self.iface, "please select exactly one housing project", type='Info', lev=1, dur=5)



    def openInfrastructureInput(self):

        # # Create a new NearestFeatureMapTool and keep reference
        # self.nearestFeatureMapTool = \
        #     NearestFeatureMapTool(self.iface.mapCanvas())
        # self.iface.mapCanvas().setMapTool(self.nearestFeatureMapTool)



        layer = self.iface.activeLayer()
        investmentName, ids = uf.getFieldValues(layer, 'InfrProj', null=False, selection=True)
        package, ids = uf.getFieldValues(layer, 'Package', null=False, selection=True)
        if layer:
            if str(layer.name()) != 'Infrastructure_Investments':
                uf.showMessage(self.iface, "please select an infrastructure project first", type='Info', lev=1, dur=5)
                return
        else:
            uf.showMessage(self.iface, "please select an infrastructure project first", type='Info', lev=1, dur=5)
            return

        if len(investmentName) == 1:
            self.ii = InfrastructureInput(self.iface, chart=self.ic)
            self.ii.show()
            self.ii.move(QPoint(450, 150))
            self.ii.investmentLabel.setText(str(investmentName[0]))
            self.ii.packageLabel2.setText('PACKAGE ' + str(package[0][-1:]))
            # TODO: continue here: this doesn't work. Its about the WindowStaysOnTopHint, which Gustavo wants
            #self.ii.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
            #self.ii.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        else:
            uf.showMessage(self.iface, "please select exactly one infrastructure project", type='Info', lev=1, dur=5)



    def openIndicatorsChart(self):
        #self.ic = IndicatorsChart(self.iface)  #old
        #self.ic = IndicatorsChartDocked(self.iface)    #new
        #self.ic is now already initialized at the initialization of the plugin, as it needs to be passed to the input forms, even if it has not yet been opened
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.ic)
        self.ic.show()
        #self.ic.move(QPoint(100, 150))
        #self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)