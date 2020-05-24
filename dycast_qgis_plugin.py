# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DycastQgisPlugin
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
import os.path

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import QgsApplication, Qgis, QgsTask

from .util.configure_path import configure_path
configure_path()

from dycast_qgis.models.configuration import Configuration

from dycast_qgis.services.configuration_service import ConfigurationService
from dycast_qgis.services.database_service import DatabaseService
from dycast_qgis.services.layer_service import LayerService
from dycast_qgis.services.logging_service import log_message

from dycast_qgis.util.remote_debugging import enable_remote_debugging
from dycast_qgis.tasks import load_cases_task
from dycast_qgis.resources import *
from dycast_qgis.dycast_qgis_plugin_dialog import DycastQgisPluginDialog
from dycast_qgis.settings_dialog import SettingsDialog


class DycastQgisPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        enable_remote_debugging()

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DycastQgisPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Dycast')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.config_service = ConfigurationService()
        self.config = self.config_service.load_config()
        self.database_service = DatabaseService(self.config)
        self.layer_service = LayerService(self.config)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DycastQgisPlugin', message)

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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/dycast_qgis_plugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Open DYCAST'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Dycast'),
                action)
            self.iface.removeToolBarIcon(action)

    def select_input_file(self):
        file_path, filter_string = QFileDialog.getOpenFileName(
            parent=self.dlg,
            caption="Select input file...",
            filter='TSV (*.tsv)')

        self.dlg.importCaseFileLineEdit.setText(file_path)
        return file_path

    def import_input_file(self):
        file_path = self.dlg.importCaseFileLineEdit.text()
        log_message("Loading {file_path}".format(file_path=file_path), Qgis.Info)

        if file_path:
            task = QgsTask.fromFunction(
                "Load Dycast Cases Task", load_cases_task.run, on_finished=load_cases_task.finished, file_path=file_path)

            task.taskCompleted.connect(
                lambda: self.dlg.importCaseFileResultLabel.setText(task.returned_values))
            task_id = QgsApplication.taskManager().addTask(task)

            self.dlg.importCaseFileResultLabel.setText(
                "Running import task. Task ID: {task_id}".format(task_id=task_id))
        else:
            self.dlg.importCaseFileResultLabel.setText(
                "Select an input file from your devise")

    def run(self):
        """Run method that performs all the real work"""

        self.iface.openMessageLog()

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = DycastQgisPluginDialog()
            self.settings_dialog = SettingsDialog(self.config, self.config_service, self.database_service, self.layer_service)

            self.dlg.importCaseFileBrowseButton.clicked.connect(
                self.select_input_file)
            self.dlg.importCaseFileStartButton.clicked.connect(
                self.import_input_file)

            self.dlg.settingsPushButton.clicked.connect(
                self.settings_dialog.show)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
