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
                       QgsRectangle,
                      )
from qgis.testing import (start_app,
                          unittest
                         )

from processing_pktools.algs.ApplyColorTable import ApplyColorTable
from processing_pktools.algs.CreateColorTable import CreateColorTable
from processing_pktools.algs.FillNoData import FillNoData
from processing_pktools.algs.FilterDem import FilterDem
from processing_pktools.algs.LasToRaster import LasToRaster
from processing_pktools.algs.RandomSampling import RandomSampling
from processing_pktools.algs.RasterAnn import RasterAnn
from processing_pktools.algs.RasterComposite import RasterComposite
from processing_pktools.algs.RasterFromText import RasterFromText
from processing_pktools.algs.RasterSampling import RasterSampling

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

    def testFilterDem(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = FilterDem()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilterdem', '-i', source, '-f', 'vito', '-dim', '17',
                 '-st', '0.0', '-minchange', '0', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'FILTER': 2,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilterdem', '-i', source, '-f', 'promorph', '-dim', '17',
                 '-st', '0.0', '-minchange', '0', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'KERNEL_SIZE': 20,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilterdem', '-i', source, '-f', 'vito', '-dim', '20',
                 '-st', '0.0', '-minchange', '0', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'CIRCULAR': True,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilterdem', '-i', source, '-f', 'vito', '-dim', '17',
                 '-circ', '-st', '0.0', '-minchange', '0', '-of', 'GTiff',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SLOPE_THRESHOLD': 1.5,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilterdem', '-i', source, '-f', 'vito', '-dim', '17',
                 '-st', '1.5', '-minchange', '0', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MIN_CHANGE': 200,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilterdem', '-i', source, '-f', 'vito', '-dim', '17',
                 '-st', '0.0', '-minchange', '200', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ARGUMENTS': '-nodata -9999',
                                     'OUTPUT': output}, context, feedback),
                ['pkfilterdem', '-i', source, '-f', 'vito', '-dim', '17',
                 '-st', '0.0', '-minchange', '0', '-nodata', '-9999',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pkfilterdem', '-i', source, '-f', 'vito', '-dim', '17',
                 '-st', '0.0', '-minchange', '0', '-co', 'COMPRESS=DEFLATE',
                 '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9', '-of', 'GTiff',
                 '-o', output])

    def testLasToRaster(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = LasToRaster()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'all', '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:2994',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ATTRIBUTE': 0,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'intensity', '-comp', 'last',
                 '-fir', 'all', '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:2994',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'COMPOSITE': 0,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'min',
                 '-fir', 'all', '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:2994',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'FILTER': 0,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'first', '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:2994',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'EXTENT': '635616.3,638864.6,848977.79,853362.37',
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'all', '-ulx', '635616.3', '-uly', '853362.37',
                 '-lrx', '638864.6', '-lry', '848977.79', '-dx', '1.0',
                 '-dy', '1.0', '-a_srs', 'EPSG:2994', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'CLASSES': '2',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'all', '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:2994',
                 '-class', '2', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'CLASSES': '3,4,5',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'all', '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:2994',
                 '-class', '3', '-class', '4', '-class', '5', '-of', 'GTiff',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'ARGUMENTS': '-nbin 15',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'all', '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:2994',
                 '-nbin', '15', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'all', '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:2994',
                 '-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9',
                 '-of', 'GTiff', '-o', output])

    def testRandomSampling(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RandomSampling()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.shp'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-rand', '100', '-buf', '3',
                 '-r', 'centroid', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RULE': 0,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-rand', '100', '-buf', '3',
                 '-r', 'point', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'COUNT': 500,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-rand', '500', '-buf', '3',
                 '-r', 'centroid', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'BUFFER': 5,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-rand', '100', '-buf', '5',
                 '-r', 'centroid', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'THRESHOLD': 50,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-rand', '100', '-buf', '3',
                 '-r', 'centroid', '-t', '50.0', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RULE': 9,
                                     'CLASSES': '5,10',
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-rand', '100', '-buf', '3',
                 '-r', 'mode', '-c', '5', '-c', '10', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RULE': 12,
                                     'PERCENTILE': 75,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-rand', '100', '-buf', '3',
                 '-r', 'percentile', '-perc', '75.0', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ARGUMENTS': '-b 1',
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-rand', '100', '-buf', '3',
                 '-r', 'centroid', '-b', '1', '-f', 'ESRI Shapefile',
                 '-o', output])

    def testRasterAnn(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RasterAnn()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')
        points = os.path.join(testDataPath, 'points.shp')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'OUTPUT': output}, context, feedback),
                ['pkann', '-i', source, '-t', points, '-label', 'id',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'NEURONS': '5',
                                     'OUTPUT': output}, context, feedback),
                ['pkann', '-i', source, '-t', points, '-label', 'id',
                 '-nn', '5', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'NEURONS': '15,5',
                                     'OUTPUT': output}, context, feedback),
                ['pkann', '-i', source, '-t', points, '-label', 'id',
                 '-nn', '15', '-nn', '5', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'N_FOLD': '2',
                                     'OUTPUT': output}, context, feedback),
                ['pkann', '-i', source, '-t', points, '-label', 'id',
                 '-cv', '2', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'ARGUMENTS': '-b 2',
                                     'OUTPUT': output}, context, feedback),
                ['pkann', '-i', source, '-t', points, '-label', 'id',
                 '-b', '2', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pkann', '-i', source, '-t', points, '-label', 'id',
                 '-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9',
                 '-of', 'GTiff', '-o', output])

    def testRasterComposite(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RasterComposite()
        alg.initAlgorithm()

        source_1 = os.path.join(testDataPath, 'dem.tif')
        source_2 = os.path.join(testDataPath, 'mask.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': [source_1],
                                     'BANDS': '1,2',
                                     'OUTPUT': output}, context, feedback),
                ['pkcomposite', '-i', source_1, '-cr', 'overwrite',
                 '-cb', '1', '-cb', '2', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': [source_1, source_2],
                                     'BANDS': '1,2',
                                     'OUTPUT': output}, context, feedback),
                ['pkcomposite', '-i', source_1, '-i', source_2, '-cr', 'overwrite',
                 '-cb', '1', '-cb', '2', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': [source_1],
                                     'BANDS': '1,2',
                                     'RULE': 4,
                                     'OUTPUT': output}, context, feedback),
                ['pkcomposite', '-i', source_1, '-cr', 'mean',
                 '-cb', '1', '-cb', '2', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': [source_1],
                                     'BANDS': '1,2',
                                     'ARGUMENTS': '-r near',
                                     'OUTPUT': output}, context, feedback),
                ['pkcomposite', '-i', source_1, '-cr', 'overwrite',
                 '-cb', '1', '-cb', '2', '-r', 'near', '-of', 'GTiff',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': [source_1],
                                     'BANDS': '1,2',
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pkcomposite', '-i', source_1, '-cr', 'overwrite',
                 '-cb', '1', '-cb', '2', '-co', 'COMPRESS=DEFLATE',
                 '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9', '-of', 'GTiff',
                 '-o', output])

    def testRasterFromText(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RasterFromText()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'data.txt')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'UL_POINT': '18.67,45.77',
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:4326',
                                     'OUTPUT': output}, context, feedback),
                ['pkascii2img', '-i', source, '-ulx', '18.67', '-uly', '45.77',
                 '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:4326',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'UL_POINT': '18.67,45.77',
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:4326',
                                     'ARGUMENTS': '-ot Float32',
                                     'OUTPUT': output}, context, feedback),
                ['pkascii2img', '-i', source, '-ulx', '18.67', '-uly', '45.77',
                 '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:4326',
                 '-ot', 'Float32', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'UL_POINT': '18.67,45.77',
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:4326',
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pkascii2img', '-i', source, '-ulx', '18.67', '-uly', '45.77',
                 '-dx', '1.0', '-dy', '1.0', '-a_srs', 'EPSG:4326',
                 '-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9',
                 '-of', 'GTiff', '-o', output])

    def testRasterSampling(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RasterSampling()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')
        mask = os.path.join(testDataPath, 'mask.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.shp'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractimg', '-i', source, '-s', mask,
                 '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'CLASSES': '5,10',
                                     'OUTPUT': output}, context, feedback),
                ['pkextractimg', '-i', source, '-s', mask, '-c', '5', '-c', '10',
                 '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'THRESHOLD': 75,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractimg', '-i', source, '-s', mask, '-t', '75.0',
                 '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'ARGUMENTS': '-b 1',
                                     'OUTPUT': output}, context, feedback),
                ['pkextractimg', '-i', source, '-s', mask, '-b', '1',
                 '-f', 'ESRI Shapefile', '-o', output])


if __name__ == '__main__':
    nose2.main()
