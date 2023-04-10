# coding=utf-8
"""Plot factory test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import os.path
import unittest

from qgis.PyQt.QtCore import QFile, QIODevice
from qgis.PyQt.QtXml import QDomDocument
from DataPlotly.test.utilities import get_qgis_app
from DataPlotly.gui.dock import (DataPlotlyDock, DataPlotlyDockManager)


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


def read_project(project_path):
    """Retur a document from qgs file

    Args:
        project_path (str): path to qgs file

    Returns:
        QDocument: document
    """
    xml_file = QFile(project_path)
    if xml_file.open(QIODevice.ReadOnly):
        xml_doc = QDomDocument()
        xml_doc.setContent(xml_file)
        xml_file.close()
        return xml_doc
    return None


class DataPlotlyDockManagerTest(unittest.TestCase):
    """
    Test DataPlotlyDockManager
    """

    def setUp(self):
        self.dock_widgets = {}
        self.dock_manager = DataPlotlyDockManager(
            iface=IFACE, dock_widgets=self.dock_widgets)

    def test_001_constructor(self):
        """
        Test the constructor of DataPlotlyDockManager
        """
        self.assertIs(self.dock_widgets, self.dock_manager.dock_widgets)

    def test_002_add_new_dock(self):
        """
        Test addNewDock of DataPlotlyDockManager
        """
        # checks DataPlotly main dock
        self.assertNotIn('DataPlotly', self.dock_widgets)
        dock_widget = self.dock_manager.addNewDock()
        self.assertIsInstance(dock_widget, DataPlotlyDock)
        self.assertIn('DataPlotly', self.dock_widgets)
        self.assertIs(dock_widget, self.dock_widgets['DataPlotly'])

        # checks it's not possible to add a new dock with DataPlotly as dock_id
        dock_widget2 = self.dock_manager.addNewDock(dock_title='NewDataPlotly',
                                                    dock_id='DataPlotly')
        self.assertIs(dock_widget2, dock_widget)

        # checks we can not add new dock with same dock_id
        dock_params = {'dock_title': 'DataPlotly2', 'dock_id': 'DataPlotly2'}
        self.dock_manager.addNewDock(**dock_params)
        self.assertIn('DataPlotly2', self.dock_widgets)
        new_dock_widget = self.dock_manager.addNewDock(
            dock_title='DataPlotly2b', dock_id='DataPlotly2')
        self.assertFalse(new_dock_widget)

    def test_003_remove_dock(self):
        """
        Test removeDock
        """
        dock_id = 'dock_to_remove'
        self.dock_manager.addNewDock(dock_id=dock_id)
        self.assertIn(dock_id, self.dock_widgets)
        self.dock_manager.removeDock(dock_id)
        self.assertNotIn(dock_id, self.dock_widgets)

    def test_004_remove_docks(self):
        """
        Test removeDocks
        """
        docks = ['DataPlotly', 'DataPlotly2', 'DataPlotly3']
        for dock in docks:
            self.dock_manager.addNewDock(dock_id=dock)
        self.dock_manager.removeDocks()
        # do not remove DataPlotly main dock
        self.assertIn('DataPlotly', self.dock_widgets)
        self.assertEqual(len(self.dock_widgets), 1)

    def test_005_get_dock(self):
        """
        Test getDock
        """
        docks = ['DataPlotly', 'DataPlotly2', 'DataPlotly3']
        for dock in docks:
            self.dock_manager.addNewDock(dock_id=dock)
        dock = self.dock_manager.getDock('DataPloty4_wrong_id')
        self.assertIsNone(dock)
        dock = self.dock_manager.getDock('DataPlotly3')
        self.assertIsInstance(dock, DataPlotlyDock)
        self.assertIs(dock, self.dock_widgets['DataPlotly3'])

    def test_read_project(self):
        """
        Test read_project with or without StateDataPlotly
        """
        project_path = os.path.join(os.path.dirname(
            __file__), 'test_project_with_state.qgs')
        document = read_project(project_path)
        ok = self.dock_manager.read_from_project(document)
        self.assertTrue(ok)
        project_path = os.path.join(os.path.dirname(
            __file__), 'test_project_without_state.qgs')
        document = read_project(project_path)
        ko = self.dock_manager.read_from_project(document)
        self.assertFalse(ko)

    def test_add_docks_from_project(self):
        """
        Test docks are added, custom project without StateDataPlotly node
        """
        project_path = os.path.join(os.path.dirname(
            __file__), 'test_project_without_state.qgs')
        document = read_project(project_path)
        self.dock_manager.addDocksFromProject(document)
        # all docks except main DataPlotlyDock are created
        self.assertIn('my-test', self.dock_widgets)

    # TODO add others test (write_to_project, maybe some tests with the state and geometry)


if __name__ == "__main__":
    suite = unittest.makeSuite(DataPlotlyDockManagerTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
