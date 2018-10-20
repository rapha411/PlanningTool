## Regional Game Mobiele Stad plugin – User Guide

# Introduction

The QGIS plugin Regional Game Mobiele Stad allows players to negotiate and make decisions on spatial plan projects for:  1) housing plans, and 2) infrastructure projects. Players can select or zoom in on a desired location, select one polygon representing either a plan or an project, and view attributes interactively. The plugin features a form docked on the right hand side of the screen, which allows display and modification of attribute values for either a housing plan or an infrastructure project.  With this form, players interactively change a selection of attributes for a selected polygon. Once the changes are saved, the plugin will recalculate indicators based on the new values of the attribute table involved. Upon closing, the plugin will bring QGIS to its default configuration.


# Installation

The QGIS plugin Regional Game Mobiele Stad is an extension for QGIS, an open source GIS package available from: http://qgis.org/en/site/. The recommended version of QGIS for installation is 2.18 LTR (Long Term Release). The plugin is not available from the official QGIS plugins repository and must be downloaded from this site: https://github.com/raphaelsulzer/PlanningTool/releases

After downloading it, you must install the plugin in the QGIS plugins folder, located under your user profile in: .qgis2/python/plugins. Simply unzip the PlanningTool.zip file and move the folder into this folder. Then start QGIS and load the plugin ‘Regional Game Mobiele Stad’ from the ‘Plugins Manager’ window.

The plugin does not require any additional configuration. An activated Microsoft Excel installation on the computer is necessary for the plugin to work. Formulas for calculating indicators are in spreadsheet ‘20180904 Regional game IMS 2.8.xlsx’, located inside the PlanningTool/data/excel folder.

For an optimal user experience set your screen to a resolution 1920x1080.


# User interaction

![alt text](images/start.png?raw=true "Title")

The plugin shows four main components: toolbar (top left), layers panel (left), map interface (center), input and output window (right).

![alt text](images/gui.png?raw=true "QGIS user interface with Regional Game Mobiele Stad")


# Toolbar

![alt text](images/toolbar.png?raw=true "Title")


# Map interface and layers panel

Interaction with the map interface is only possible if one of the mapping tools is activated. Interaction with the layers panel is only necessary for the use of the ‘Identify Features’ map tool.


# Input and output window

![alt text](images/input_output.png?raw=true "Title")



Raphael Sulzer (raphaelsulzer@gmx.de)
Gustavo Arciniegas (geocolconsultant@gmail.com)

