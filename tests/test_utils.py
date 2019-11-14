# -*- coding: utf-8 -*-

"""
***************************************************************************
    test_utils.py
    ---------------------
    Date                 : November 2019
    Copyright            : (C) 2019 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'November 2019'
__copyright__ = '(C) 2019, Alexander Bruy'

import os

from qgis.PyQt.QtCore import QCoreApplication, QSettings

from qgis.testing import start_app, unittest

from processing.core.ProcessingConfig import ProcessingConfig

from processing_pktools.pktoolsProvider import PktoolsProvider
from processing_pktools import pktoolsUtils

testDataPath = os.path.join(os.path.dirname(__file__), 'data')


class TestPktoolsUtils(unittest.TestCase):

    def __init__(self, methodName):
        super().__init__(methodName)

        QCoreApplication.setOrganizationName('alexbruy')
        QCoreApplication.setOrganizationDomain('qgis.org')
        QCoreApplication.setApplicationName('pktools')
        QSettings().clear()

        self.provider = PktoolsProvider()
        self.provider.load()

    @classmethod
    def setUpClass(cls):
        start_app()

    def testPktoolsDirectory(self):
        self.assertFalse(pktoolsUtils.pktoolsDirectory())
        ProcessingConfig.setSettingValue(pktoolsUtils.PKTOOLS_DIRECTORY, '/usr/local/bin')
        self.assertEqual(pktoolsUtils.pktoolsDirectory(), '/usr/local/bin')
        ProcessingConfig.setSettingValue(pktoolsUtils.PKTOOLS_DIRECTORY, None)
        self.assertFalse(pktoolsUtils.pktoolsDirectory())

    def testCompositeOptions(self):
        result = pktoolsUtils.parseCompositeOption('-c', '1,2,3')
        self.assertEqual(result, ['-c', '1', '-c', '2', '-c' , '3'])

        result = pktoolsUtils.parseCompositeOption('-c', '1, 2, 3')
        self.assertEqual(result, ['-c', '1', '-c', '2', '-c' , '3'])

        result = pktoolsUtils.parseCompositeOption('-c', '1,2,3', ';')
        self.assertEqual(result, ['-c', '1,2,3'])

        result = pktoolsUtils.parseCompositeOption('-c', '1; 2; 3', ';')
        self.assertEqual(result, ['-c', '1', '-c', '2', '-c' , '3'])

        result = pktoolsUtils.parseCompositeOption('-b', [1])
        self.assertEqual(result, ['-b', '1'])

        result = pktoolsUtils.parseCompositeOption('-b', [1, 2, 3])
        self.assertEqual(result, ['-b', '1', '-b', '2', '-b' , '3'])

        result = pktoolsUtils.parseCreationOptions('COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9')
        self.assertEqual(result, ['-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2', '-co' , 'ZLEVEL=9'])

    def testArgumentsQuoting(self):
        result = pktoolsUtils.prepareArguments(['cmd', '-i', 'input.tif', '-o', 'output.tif'])
        self.assertEqual(result, 'cmd -i input.tif -o output.tif')

        result = pktoolsUtils.prepareArguments(['cmd', '-i', '/home/user/input.tif', '-o', 'output.tif'])
        self.assertEqual(result, 'cmd -i /home/user/input.tif -o output.tif')

        result = pktoolsUtils.prepareArguments(['cmd', '-i', '/home/user/my data/input.tif', '-o', 'output.tif'])
        self.assertEqual(result, 'cmd -i \'/home/user/my data/input.tif\' -o output.tif')


if __name__ == '__main__':
    nose2.main()
