# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DycastQgisPluginDialog
                                 A QGIS plugin
 This plugin integrates the Dynamic Continuous-Area Space-Time (DYCAST) system into QGIS. Dycast is a biologically based spatiotemporal model that uses georeferenced case data to identify areas at high risk for the transmission of mosquito-borne diseases such as zika, dengue, and West Nile virus (WNV).
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-07-30
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Dycast Project
        email                : meijer.vincent@gmail.com
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

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dycast_qgis_plugin_dialog_base.ui'))


class DycastQgisPluginDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DycastQgisPluginDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)