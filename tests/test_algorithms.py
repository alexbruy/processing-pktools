# -*- coding: utf-8 -*-

"""
***************************************************************************
    test_algorithms.py
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

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import tempfile

from qgis.core import (QgsProcessingContext,
                       QgsProcessingFeedback,
                      )
from qgis.testing import (start_app,
                          unittest
                         )

from processing_pktools.algs.ApplyColorTable import ApplyColorTable
from processing_pktools.algs.CreateColorTable import CreateColorTable
from processing_pktools.algs.FillNoData import FillNoData

testDataPath = os.path.join(os.path.dirname(__file__), 'data')


class TestAlgorithms(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        start_app()

    def testApplyColorTable(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = ApplyColorTable()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')
        colorTable = os.path.join(testDataPath, 'ctable.txt')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'COLOR_TABLE': colorTable,
                                     'OUTPUT': output}, context, feedback),
                ['pkcreatect', '-i', source, '-ct', colorTable,
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'COLOR_TABLE': colorTable,
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pkcreatect', '-i', source, '-ct', colorTable,
                 '-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'COLOR_TABLE': colorTable,
                                     'ARGUMENTS': '-legend legend.png',
                                     'OUTPUT': output}, context, feedback),
                ['pkcreatect', '-i', source, '-ct', colorTable,
                 '-legend', 'legend.png', '-of', 'GTiff', '-o', output])

    def testCreateColorTable(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = CreateColorTable()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RANGE': [0, 100],
                                     'OUTPUT': output}, context, feedback),
                ['pkcreatect', '-i', source, '-min', '0.0', '-max', '100.0',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RANGE': [0, 100],
                                     'GRAYSCALE': True,
                                     'OUTPUT': output}, context, feedback),
                ['pkcreatect', '-i', source, '-min', '0.0', '-max', '100.0',
                 '-g', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RANGE': [0, 100],
                                     'ARGUMENTS': '-legend legend.png',
                                     'OUTPUT': output}, context, feedback),
                ['pkcreatect', '-i', source, '-min', '0.0', '-max', '100.0',
                 '-legend', 'legend.png', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RANGE': [0, 100],
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pkcreatect', '-i', source, '-min', '0.0', '-max', '100.0',
                  '-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9',
                  '-of', 'GTiff', '-o', output])

    def testFillNoData(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = FillNoData()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MASK': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkfillnodata', '-i', source, '-m', source, '-b', '1',
                 '-d', '0', '-it', '0', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'BANDS': [2],
                                     'MASK': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkfillnodata', '-i', source, '-m', source, '-b', '2',
                 '-d', '0', '-it', '0', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'BANDS': [1, 2, 3],
                                     'MASK': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkfillnodata', '-i', source, '-m', source, '-b', '1',
                 '-b', '2', '-b', '3', '-d', '0', '-it', '0',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MASK': source,
                                     'DISTANCE': 3,
                                     'OUTPUT': output}, context, feedback),
                ['pkfillnodata', '-i', source, '-m', source, '-b', '1',
                 '-d', '3', '-it', '0', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MASK': source,
                                     'ITERATIONS': 2,
                                     'OUTPUT': output}, context, feedback),
                ['pkfillnodata', '-i', source, '-m', source, '-b', '1',
                 '-d', '0', '-it', '2', '-of', 'GTiff', '-o', output])


if __name__ == '__main__':
    nose2.main()
