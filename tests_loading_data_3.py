# this is for adding the "external" folder to the system path, because the QGIS python is only looking in the system path for python packages
# you can see that this works by doing import sys, sys.path inside the QGIS python console
import os, sys
#sys.path.append(os.path.join(os.path.dirname(__file__), "external"))

import xlwings as xw



while xw.apps.count > 0:
    xw.apps.active.kill()


print(xw.apps.active)


a=5