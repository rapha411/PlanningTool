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
from PyQt4.QtGui import QAction, QIcon, QToolBar
#from PyQt4 import QtGui, QtCore, uic
from . import utility_functions as uf


# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from planning_tool_dockwidget import PlanningToolClassDockWidget
from planning_tool_dockwidget import IndicatorsDialog
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
        self.menu = self.transl(u'&Planning Tool')
        # TODO: We are going to let the user set this up in a future iteration
        self.planning_toolbar = self.iface.addToolBar(u'PTToolbar')
        self.planning_toolbar.setObjectName(u'mPTToolbar')
        # TODO: add the necessary navigation tools to the


        # print "** INITIALIZING PlanningToolClass"

        self.pluginIsActive = False
        self.dockwidget = None


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
        icon_path = ':/plugins/PlanningToolClass/icons/pt_icon.png'
        self.add_action(
            icon_path,
            text=self.transl(u'Planning Tool'),
            callback=self.run,
            parent=self.iface.mainWindow())


        icon_path = ':/plugins/PlanningToolClass/icons/calculator.png'
        self.add_action(
            icon_path,
            text=self.transl(u'Calculate Indicators'),
            callback=self.openIndicatorDialog,
            parent=self.iface.mainWindow())


        # add the map navigation actions
        self.planning_toolbar.addSeparator()
        self.planning_toolbar.addAction(self.iface.actionPan())
        self.planning_toolbar.addAction(self.iface.actionPanToSelected())
        self.planning_toolbar.addAction(self.iface.actionZoomIn())
        self.planning_toolbar.addAction(self.iface.actionZoomOut())
        self.planning_toolbar.addAction(self.iface.actionZoomActualSize())
        self.planning_toolbar.addAction(self.iface.actionZoomFullExtent())




    #--------------------------------------------------------------------------
    # unload plugin

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING PlanningToolClass"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        # toolbars that were present before opening plugin are restored here
        for i, toolbar in enumerate(self.toolbars0):
            toolbar.setVisible(self.toolbars0_visible[i])
            toolbar.setIconSize(self.toolbars0_size[i])

        # and put the planning_toolbar back in place, i.e. dock it
        self.iface.addToolBar(self.planning_toolbar)



        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD PlanningToolClass"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.transl(u'&Storm Help'),
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
            self.toolbars0_size = []
            # TODO also need to get the QSize of the existing toolbars so they will appear in the correct size again

            for toolbar in self.toolbars0:
                self.toolbars0_visible.append(toolbar.isVisible())
                toolbar.setVisible(False)
                #print(toolbar.objectName())
                self.toolbars0_size.append(toolbar.iconSize())
                print(toolbar.iconSize())

            # # add toolbars that are necessary for the plugin to interface (self.iface.mainWindow()) here
            # self.iface.mainWindow().findChild(QToolBar, "mMapNavToolBar").setVisible(True)
            # self.iface.mainWindow().findChild(QToolBar, "mMapNavToolBar").setIconSize(QSize(64,64))
            # #TODO: could also change orientation and location of mMapNavToolBar to appear vertically on the right of the screen
            # # http://pyqt.sourceforge.net/Docs/PyQt4/qtoolbar.html#allowedAreas

            # following is taken from here: https://forum.qt.io/topic/4082/how-to-float-qtoolbar-on-creation

            # self.navToolbar = self.iface.mainWindow().findChild(QToolBar, "mMapNavToolBar")
            # t.setAllowedAreas(Qt.NoToolBarArea)
            self.planning_toolbar.setAllowedAreas(Qt.AllToolBarAreas)
            # self.navToolbar.setOrientation(Qt.Horizontal)
            self.planning_toolbar.setIconSize(QSize(64,64))
            p = self.planning_toolbar.mapToGlobal(QPoint(0, 0))
            self.planning_toolbar.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
            self.planning_toolbar.move(p.x() + 30, p.y() + 50)
            self.planning_toolbar.adjustSize()
            self.planning_toolbar.show()



            ### start plugin
            #print "** STARTING PlanningToolClass"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = PlanningToolClassDockWidget(self.iface)
                #self.dockwidget2 = IndicatorsDialog(self.dockwidget)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)

            #self.dockwidget.setFloating(True)
            #self.dockwidget.move(QPoint(0, 0))

            # start plugin in fullscreen, but first do self.dockwidget.move(QPoint(0, 0))
            #self.dockwidget.showFullScreen()


            self.dockwidget.setWindowTitle("Planning Tool")
            self.dockwidget.show()

    def openIndicatorDialog(self):
        self.nd = IndicatorsDialog(self.iface)
        self.nd.show()
        self.nd.move(QPoint(150, 150))
