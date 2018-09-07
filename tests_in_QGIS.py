from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QPoint, QSize
from PyQt4.QtGui import QAction, QIcon, QToolBar, QDockWidget


dockwidget = iface.mainWindow().findChildren(QDockWidget)
for dock in dockwidget:
    #self.toolbars0_visible.append(toolbar.isVisible())
    #toolbar.setVisible(False)
    print(dock.objectName())


t = iface.mainWindow().findChild(QToolBar, "mMapNavToolBar")

#t.setAllowedAreas(Qt.NoToolBarArea)
t.setAllowedAreas(Qt.AllToolBarAreas)
#t.setOrientation(Qt.Vertical)
t.setOrientation(Qt.Horizontal)
p = t.mapToGlobal(QPoint(0, 0))
t.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
t.move(p.x() + 30, p.y() + 50)
t.adjustSize()

t.show()

def activated(dock):
    dock = iface.mainWindow().findChild(QDockWidget, dock)
    visible = dock.isVisible()
    dock.setVisible(not visible)