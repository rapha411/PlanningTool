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
from planning_tool_dockwidget import IndicatorsChartDocked
from SelectionMappingTool import SelectionTool

import os.path
import subprocess


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
        self.planning_toolbar = self.iface.addToolBar(u'RGMSToolbar')
        self.planning_toolbar.setObjectName(u'mRGMSToolbar')


        print "** INITIALIZING PlanningToolClass"

        self.pluginIsActive = False
        self.ic = None
        self.mapTool = None
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

        # close excel sheet
        if self.book:
            #self.book.save()
            self.book.close()
            #self.app.quit()
            self.app.kill()
            self.book = None
            self.app = None
            del self.app
            del self.book

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

        # set icon size back, iface.mainWindow().findChildren(QToolBar)[i].iconSize() reveals that it is 24x24
        self.planning_toolbar.setIconSize(QSize(24, 24))



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

        if self.mapTool:
            self.canvas.unsetMapTool(self.mapTool)
            self.mapTool = None

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

            #### toolbar stuff:
            # gathering all toolbars of the QGIS GUI and their visibility state
            # and save them as global variables
            # then set all of them invisible for the PlanningTool start
            self.toolbars0 = self.iface.mainWindow().findChildren(QToolBar)
            self.toolbars0_visible = []

            #### layertree icon size
            self.tree_size = self.iface.layerTreeView().iconSize()
            self.iface.layerTreeView().setIconSize(QSize(40, 40))

            # set toolbars invisible
            for toolbar in self.toolbars0:
                self.toolbars0_visible.append(toolbar.isVisible())
                toolbar.setVisible(False)

            # show planning toolbar
            self.planning_toolbar.show()
            # update/ add additional stuff to planning toolbar
            self.updateToolbar()

            # zoom to infra investments at the start of the plugin
            #self.zoomToInfrastructureInvestments()

            # open excel
            self.excel_file = os.path.join(os.path.dirname(__file__), 'data', 'excel', '20180926 Regional game IMS 2.6.xlsx')
            self.app = xw.App(visible=False)
            #self.book = self.app.books.open(self.excel_file)

            print "open new app"


            ## initialise IndicatorsChart widget here
            # dockwidget does not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.ic == None:
                # Create the dockwidget (after translation) and keep reference
                print "pass new book"
                self.book = self.app.books.open(self.excel_file)
                self.ic = IndicatorsChartDocked(self.iface, book=self.book)
                # maptool = MapToolEmitPoint(self.canvas)
                # self.canvas.setMapTool(maptool)
                # maptool.canvasDoubleClicked.connect(self.handleDoubleClick)
            else:
                print "pass old book"
                self.book = self.app.books.open(self.excel_file)
                self.ic.book = self.book


            # connect to provide cleanup on closing of dockwidget
            self.ic.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.ic)

            self.ic.setWindowTitle('Regional Game Mobiele Stad')
            self.ic.show()

            #self.ic = IndicatorsChartDocked(self.iface, book=self.book)


    # ### helper functions
    def updateToolbar(self):

        self.rgmsAction.setVisible(False)

        # # save
        # icon_path = ':/plugins/PlanningToolClass/icons/save.png'
        # self.add_action(
        #     icon_path,
        #     text=self.transl(u'Save'),
        #     callback=self.save,
        #     parent=self.iface.mainWindow())
        #
        # ##toolbar icons /  add the map navigation actions
        # separator
        self.separators = []
        # self.separators.append(self.planning_toolbar.addSeparator())


        # zoom to infrastructure investments / home
        icon_path = ':/plugins/PlanningToolClass/icons/home.png'
        self.add_action(
            icon_path,
            text=self.transl(u'Zoom to Infrastructure Investments'),
            callback=self.zoomToInfrastructureInvestments,
            parent=self.iface.mainWindow())

        # # # pan - only needed for OSX version
        # self.planning_toolbar.addAction(self.iface.actionPan())
        # self.actions.append(self.iface.actionPan())

        # zoom window
        self.planning_toolbar.addAction(self.iface.actionZoomIn())
        self.actions.append(self.iface.actionZoomIn())

        # zoom to previous extent
        self.planning_toolbar.addAction(self.iface.actionZoomLast())
        self.actions.append(self.iface.actionZoomLast())

        # separator
        self.separators.append(self.planning_toolbar.addSeparator())

        # identify features
        self.planning_toolbar.addAction(self.iface.actionIdentify())
        self.actions.append(self.iface.actionIdentify())

        # separator
        self.separators.append(self.planning_toolbar.addSeparator())

        # self.planning_toolbar.addAction(self.iface.actionSelect())
        # self.actions.append(self.iface.actionSelect())

        # touch
        self.planning_toolbar.addAction(self.iface.actionTouch())
        self.actions.append(self.iface.actionTouch())

        # add infrastructure input
        icon_path = ':/plugins/PlanningToolClass/icons/select.png'
        self.iiAction = self.add_action(
            icon_path,
            text=self.transl(u'Select'),
            callback=self.activateSelectionTool,
            parent=self.iface.mainWindow())
        self.iiAction.setObjectName('mSelectAction')
        self.iiAction.setCheckable(True)

        # remove selection tool
        icon_path = ':/plugins/PlanningToolClass/icons/deselectAll.png'
        self.iiAction = self.add_action(
            icon_path,
            text=self.transl(u'Clear selection'),
            callback=self.clearSelectedFeatures,
            parent=self.iface.mainWindow())

        self.separators.append(self.planning_toolbar.addSeparator())

        # add infrastructure input
        icon_path = ':/plugins/PlanningToolClass/icons/help.png'
        self.add_action(
            icon_path,
            text=self.transl(u'Help'),
            callback=self.openHelp,
            parent=self.iface.mainWindow())

        # self.planning_toolbar.addAction(self.iface.actionSelect())
        # self.actions.append(self.iface.actionSelect())

        # add deselect function here
        # self.planning_toolbar.addAction(self.iface.actionDeleteSelected())
        # self.actions.append(self.iface.actionDeleteSelected())


        # # add calculate indicators button
        # icon_path = ':/plugins/PlanningToolClass/icons/calculator.png'
        # self.add_action(
        #     icon_path,
        #     text=self.transl(u'Calculate Indicators'),
        #     callback=self.openIndicatorsChart,
        #     parent=self.iface.mainWindow())

        # # separator
        # self.separators.append(self.planning_toolbar.addSeparator())

        # # close plugin
        # icon_path = ':/plugins/PlanningToolClass/icons/close.png'
        # self.add_action(
        #     icon_path,
        #     text=self.transl(u'Close Plugin'),
        #     callback=self.onClosePlugin,
        #     parent=self.iface.mainWindow())

        # extra necessary actions
        # self.planning_toolbar.addAction(self.iface.actionZoomActualSize())
        # self.planning_toolbar.addAction(self.iface.actionZoomFullExtent())
        # self.planning_toolbar.addAction(self.iface.actionZoomToLayer())
        # self.planning_toolbar.addAction(self.iface.actionZoomToSelected())
        # self.planning_toolbar.addAction(self.iface.actionDraw())
        # self.planning_toolbar.addAction(self.iface.actionSelect())

        self.planning_toolbar.setIconSize(QSize(40, 40))

    def zoomToInfrastructureInvestments(self):
        # zoom on infrastructure investments layer extent / home
        uf.zoomToLayer(self.iface, "Infrastructure Projects")


    def clearSelectedFeatures(self):

        uf.getCanvasLayerByName(self.canvas, "Infrastructure Projects").removeSelection()
        uf.getCanvasLayerByName(self.canvas, "Housing Plans").removeSelection()




### activate map Tool
    def activateSelectionTool(self):

        if self.mapTool == None:
            self.mapTool = SelectionTool(widget=self.ic, canvas=self.canvas, action=self.iiAction)
        self.canvas.setMapTool(self.mapTool)
        #uf.showMessage(self.iface, 'Tap on a polygon to select the corresponding project. Double-tap on the map canvas to remove all selections.', type='Info', lev=1, dur=10)


#### open dialogs:
    def openIndicatorsChart(self):
        #self.ic = IndicatorsChart(self.iface)  #old
        #self.ic = IndicatorsChartDocked(self.iface)    #new
        #self.ic is now already initialized at the initialization of the plugin, as it needs to be passed to the input forms, even if it has not yet been opened
        self.ic.setFloating(False)
        #self.ic.setAllowedAreas(Qt.RightDockWidgetArea)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.ic)
        self.ic.show()
        #self.ic.move(QPoint(100, 150))
        #self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)


    def save(self):
        pass


    def openHelp(self):
        print "open help"
        filepath = os.path.join(os.path.dirname(__file__), 'Help.pdf')
        subprocess.Popen([filepath], shell=True)
        #print "open PDF"


