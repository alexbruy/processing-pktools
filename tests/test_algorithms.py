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
from processing_pktools.algs.RasterSvm import RasterSvm
from processing_pktools.algs.RasterToTextExtent import RasterToTextExtent
from processing_pktools.algs.RasterToTextMask import RasterToTextMask
from processing_pktools.algs.RasterToVector import RasterToVector
from processing_pktools.algs.RegularSampling import RegularSampling
from processing_pktools.algs.Sieve import Sieve
from processing_pktools.algs.SpatialFilter import SpatialFilter
from processing_pktools.algs.SpectralFilter import SpectralFilter
from processing_pktools.algs.SunShadow import SunShadow
from processing_pktools.algs.VectorFromText import VectorFromText
from processing_pktools.algs.VectorSampling import VectorSampling
from processing_pktools.algs.VectorToText import VectorToText

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
                 '-fir', 'all', '-ulx', '0.0', '-uly', '0.0',
                 '-lrx', '0.0', '-lry', '0.0', '-dx', '1.0', '-dy', '1.0',
                 '-a_srs', 'EPSG:2994', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ATTRIBUTE': 0,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'intensity', '-comp', 'last',
                 '-fir', 'all', '-ulx', '0.0', '-uly', '0.0',
                 '-lrx', '0.0', '-lry', '0.0', '-dx', '1.0', '-dy', '1.0',
                 '-a_srs', 'EPSG:2994', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'COMPOSITE': 0,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'min',
                 '-fir', 'all', '-ulx', '0.0', '-uly', '0.0',
                 '-lrx', '0.0', '-lry', '0.0', '-dx', '1.0', '-dy', '1.0',
                 '-a_srs', 'EPSG:2994', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'FILTER': 0,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'first', '-ulx', '0.0', '-uly', '0.0',
                 '-lrx', '0.0', '-lry', '0.0', '-dx', '1.0', '-dy', '1.0',
                 '-a_srs', 'EPSG:2994', '-of', 'GTiff', '-o', output])

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
                 '-fir', 'all', '-ulx', '0.0', '-uly', '0.0',
                 '-lrx', '0.0', '-lry', '0.0', '-dx', '1.0', '-dy', '1.0',
                 '-a_srs', 'EPSG:2994', '-class', '2', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'CLASSES': '3,4,5',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'all', '-ulx', '0.0', '-uly', '0.0',
                 '-lrx', '0.0', '-lry', '0.0', '-dx', '1.0', '-dy', '1.0',
                 '-a_srs', 'EPSG:2994', '-class', '3', '-class', '4',
                 '-class', '5', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'ARGUMENTS': '-nbin 15',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'all', '-ulx', '0.0', '-uly', '0.0',
                 '-lrx', '0.0', '-lry', '0.0', '-dx', '1.0', '-dy', '1.0',
                 '-a_srs', 'EPSG:2994', '-nbin', '15', '-of', 'GTiff',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SIZE_X': 1,
                                     'SIZE_Y': 1,
                                     'CRS': 'EPSG:2994',
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pklas2img', '-i', source, '-n', 'z', '-comp', 'last',
                 '-fir', 'all', '-ulx', '0.0', '-uly', '0.0',
                 '-lrx', '0.0', '-lry', '0.0', '-dx', '1.0', '-dy', '1.0',
                 '-a_srs', 'EPSG:2994', '-co', 'COMPRESS=DEFLATE',
                 '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9', '-of', 'GTiff',
                 '-o', output])

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

    def testRasterSvm(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RasterSvm()
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
                ['pksvm', '-i', source, '-t', points, '-label', 'id',
                 '-svmt', 'C_SVC', '-kt', 'radial', '-of', 'GTiff',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'SVM': 2,
                                     'OUTPUT': output}, context, feedback),
                ['pksvm', '-i', source, '-t', points, '-label', 'id',
                 '-svmt', 'one_class', '-kt', 'radial', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'KERNEL': 1,
                                     'OUTPUT': output}, context, feedback),
                ['pksvm', '-i', source, '-t', points, '-label', 'id',
                 '-svmt', 'C_SVC', '-kt', 'polynomial', '-of', 'GTiff',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'DEGREE': 5,
                                     'OUTPUT': output}, context, feedback),
                ['pksvm', '-i', source, '-t', points, '-label', 'id',
                 '-svmt', 'C_SVC', '-kt', 'radial', '-kd', '5', '-of', 'GTiff',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'GAMMA': 1.5,
                                     'OUTPUT': output}, context, feedback),
                ['pksvm', '-i', source, '-t', points, '-label', 'id',
                 '-svmt', 'C_SVC', '-kt', 'radial', '-g', '1.5', '-of', 'GTiff',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'COEF_0': 0.1,
                                     'OUTPUT': output}, context, feedback),
                ['pksvm', '-i', source, '-t', points, '-label', 'id',
                 '-svmt', 'C_SVC', '-kt', 'radial', '-c0', '0.1', '-of', 'GTiff',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'ARGUMENTS': '-cv 2',
                                     'OUTPUT': output}, context, feedback),
                ['pksvm', '-i', source, '-t', points, '-label', 'id',
                 '-svmt', 'C_SVC', '-kt', 'radial', '-cv', '2', '-of', 'GTiff',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'TRAINING': points,
                                     'FIELD': 'id',
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pksvm', '-i', source, '-t', points, '-label', 'id',
                 '-svmt', 'C_SVC', '-kt', 'radial', '-co', 'COMPRESS=DEFLATE',
                 '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9', '-of', 'GTiff',
                 '-o', output])

    def testRasterToTextExtent(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RasterToTextExtent()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.txt'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'matrix',
                 '-ulx', '0.0', '-uly', '0.0', '-lrx', '0.0', '-lry', '0.0',
                 '-dx', '0.0', '-dy', '0.0', '-r', 'near', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'BAND': 2,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '2', '-of', 'matrix',
                 '-ulx', '0.0', '-uly', '0.0', '-lrx', '0.0', '-lry', '0.0',
                 '-dx', '0.0', '-dy', '0.0', '-r', 'near', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'EXTENT': '635616.3,638864.6,848977.79,853362.37',
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'matrix',
                 '-ulx', '635616.3', '-uly', '853362.37',
                 '-lrx', '638864.6', '-lry', '848977.79',
                 '-dx', '0.0', '-dy', '0.0', '-r', 'near', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'FORMAT': 1,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'list',
                 '-ulx', '0.0', '-uly', '0.0', '-lrx', '0.0', '-lry', '0.0',
                 '-dx', '0.0', '-dy', '0.0', '-r', 'near', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RESAMPLING': 1,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'matrix',
                 '-ulx', '0.0', '-uly', '0.0', '-lrx', '0.0', '-lry', '0.0',
                 '-dx', '0.0', '-dy', '0.0', '-r', 'bilinear', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SIZE_X': 0.1,
                                     'SIZE_Y': 0.1,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'matrix',
                 '-ulx', '0.0', '-uly', '0.0', '-lrx', '0.0', '-lry', '0.0',
                 '-dx', '0.1', '-dy', '0.1', '-r', 'near', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ARGUMENTS': '-dstnodata -9999',
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'matrix',
                 '-ulx', '0.0', '-uly', '0.0', '-lrx', '0.0', '-lry', '0.0',
                 '-dx', '0.0', '-dy', '0.0', '-r', 'near',
                 '-dstnodata', '-9999', '-o', output])

    def testRasterToTextMask(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RasterToTextMask()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')
        mask = os.path.join(testDataPath, 'mask.shp')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.txt'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MASK': mask,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'matrix',
                 '-e', mask, '-dx', '0.0', '-dy', '0.0', '-r', 'near',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'BAND': 2,
                                     'MASK': mask,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '2', '-of', 'matrix',
                 '-e', mask, '-dx', '0.0', '-dy', '0.0', '-r', 'near',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MASK': mask,
                                     'FORMAT': 1,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'list',
                 '-e', mask, '-dx', '0.0', '-dy', '0.0', '-r', 'near',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MASK': mask,
                                     'RESAMPLING': 1,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'matrix',
                 '-e', mask, '-dx', '0.0', '-dy', '0.0', '-r', 'bilinear',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MASK': mask,
                                     'SIZE_X': 0.1,
                                     'SIZE_Y': 0.1,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'matrix',
                 '-e', mask, '-dx', '0.1', '-dy', '0.1', '-r', 'near',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MASK': mask,
                                     'ARGUMENTS': '-dstnodata -9999',
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpimg', '-i', source, '-b', '1', '-of', 'matrix',
                 '-e', mask, '-dx', '0.0', '-dy', '0.0', '-r', 'near',
                 '-dstnodata', '-9999', '-o', output])

    def testRasterToVector(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RasterToVector()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')
        mask = os.path.join(testDataPath, 'mask.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.shp'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkpolygonize', '-i', source, '-b', '1', '-n', 'DN',
                 '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'BAND': 2,
                                     'OUTPUT': output}, context, feedback),
                ['pkpolygonize', '-i', source, '-b', '2', '-n', 'DN',
                 '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MASK': mask,
                                     'OUTPUT': output}, context, feedback),
                ['pkpolygonize', '-i', source, '-b', '1', '-m', mask,
                 '-n', 'DN', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'FIELD_NAME': 'ELEV',
                                     'OUTPUT': output}, context, feedback),
                ['pkpolygonize', '-i', source, '-b', '1', '-n', 'ELEV',
                 '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'NODATA': -9999,
                                     'OUTPUT': output}, context, feedback),
                ['pkpolygonize', '-i', source, '-b', '1', '-n', 'DN',
                 '-nodata', '-9999.0', '-f', 'ESRI Shapefile', '-o', output])

    def testRegularSampling(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = RegularSampling()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.shp'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-grid', '100', '-buf', '3',
                 '-r', 'centroid', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RULE': 0,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-grid', '100', '-buf', '3',
                 '-r', 'point', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'CELL_SIZE': 500,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-grid', '500', '-buf', '3',
                 '-r', 'centroid', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'BUFFER': 5,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-grid', '100', '-buf', '5',
                 '-r', 'centroid', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'THRESHOLD': 50,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-grid', '100', '-buf', '3',
                 '-r', 'centroid', '-t', '50.0', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RULE': 9,
                                     'CLASSES': '5,10',
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-grid', '100', '-buf', '3',
                 '-r', 'mode', '-c', '5', '-c', '10', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'RULE': 12,
                                     'PERCENTILE': 75,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-grid', '100', '-buf', '3',
                 '-r', 'percentile', '-perc', '75.0', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ARGUMENTS': '-b 1',
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-grid', '100', '-buf', '3',
                 '-r', 'centroid', '-b', '1', '-f', 'ESRI Shapefile',
                 '-o', output])

    def testSieve(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = Sieve()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')
        mask = os.path.join(testDataPath, 'mask.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OUTPUT': output}, context, feedback),
                ['pksieve', '-i', source, '-b', '1', '-s', '0', '-c', '8',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'BAND': 2,
                                     'OUTPUT': output}, context, feedback),
                ['pksieve', '-i', source, '-b', '2', '-s', '0', '-c', '8',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SIZE': 100,
                                     'OUTPUT': output}, context, feedback),
                ['pksieve', '-i', source, '-b', '1', '-s', '100', '-c', '8',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'CONNECTEDNESS': 1,
                                     'OUTPUT': output}, context, feedback),
                ['pksieve', '-i', source, '-b', '1', '-s', '0', '-c', '4',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'MASK': mask,
                                     'OUTPUT': output}, context, feedback),
                ['pksieve', '-i', source, '-b', '1', '-s', '0', '-c', '8',
                 '-m', mask, '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pksieve', '-i', source, '-b', '1', '-s', '0', '-c', '8',
                 '-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9',
                 '-of', 'GTiff', '-o', output])

    def testSpatialFilter(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = SpatialFilter()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'dilate', '-dx', '3', '-dy', '3',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'FILTER': 6,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'median', '-dx', '3', '-dy', '3',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'KERNEL_X': 5,
                                     'KERNEL_Y': 5,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'dilate', '-dx', '5', '-dy', '5',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'CIRCULAR': True,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'dilate', '-dx', '3', '-dy', '3',
                 '-circ', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ARGUMENTS': '-pad symmetric',
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'dilate', '-dx', '3', '-dy', '3',
                 '-pad', 'symmetric', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'dilate', '-dx', '3', '-dy', '3',
                 '-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9',
                 '-of', 'GTiff', '-o', output])

    def testSpectralFilter(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = SpectralFilter()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'dilate', '-dz', '1',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'FILTER': 6,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'median', '-dz', '1',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'KERNEL_Z': 3,
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'dilate', '-dz', '3',
                 '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ARGUMENTS': '-pad symmetric',
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'dilate', '-dz', '1',
                 '-pad', 'symmetric', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pkfilter', '-i', source, '-f', 'dilate', '-dz', '1',
                 '-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9',
                 '-of', 'GTiff', '-o', output])

    def testSunShadow(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = SunShadow()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.tif'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ZENITH_ANGLE': 10,
                                     'AZIMUTH_ANGLE': 170,
                                     'SHADOW': 50,
                                     'OUTPUT': output}, context, feedback),
                ['pkdsm2shadow', '-i', source, '-sza', '10.0', '-saa', '170.0',
                 '-f', '50', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ZENITH_ANGLE': 10,
                                     'AZIMUTH_ANGLE': 170,
                                     'SHADOW': 50,
                                     'ARGUMENTS': '-ot Float32',
                                     'OUTPUT': output}, context, feedback),
                ['pkdsm2shadow', '-i', source, '-sza', '10.0', '-saa', '170.0',
                 '-f', '50', '-ot', 'Float32', '-of', 'GTiff', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'ZENITH_ANGLE': 10,
                                     'AZIMUTH_ANGLE': 170,
                                     'SHADOW': 50,
                                     'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                     'OUTPUT': output}, context, feedback),
                ['pkdsm2shadow', '-i', source, '-sza', '10.0', '-saa', '170.0',
                 '-f', '50', '-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2',
                 '-co', 'ZLEVEL=9', '-of', 'GTiff', '-o', output])

    def testVectorFromText(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = VectorFromText()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'data.txt')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.shp'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkascii2ogr', '-i', source, '-x', '0', '-y', '1',
                 '-a_srs', 'EPSG:4326', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'COLUMN_X': 3,
                                     'COLUMN_Y': 4,
                                     'OUTPUT': output}, context, feedback),
                ['pkascii2ogr', '-i', source, '-x', '3', '-y', '4',
                 '-a_srs', 'EPSG:4326', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'CRS': 'EPSG:3857',
                                     'OUTPUT': output}, context, feedback),
                ['pkascii2ogr', '-i', source, '-x', '0', '-y', '1',
                 '-a_srs', 'EPSG:3857', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'FIELDS': '-n id -ot Integer -n label -ot Integer',
                                     'OUTPUT': output}, context, feedback),
                ['pkascii2ogr', '-i', source, '-x', '0', '-y', '1',
                 '-a_srs', 'EPSG:4326', '-n', 'id', '-ot', 'Integer',
                 '-n', 'label', '-ot', 'Integer', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SEPARATOR': ';',
                                     'OUTPUT': output}, context, feedback),
                ['pkascii2ogr', '-i', source, '-x', '0', '-y', '1',
                 '-a_srs', 'EPSG:4326', '-fs', ';', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'CREATE_POLYGON': True,
                                     'OUTPUT': output}, context, feedback),
                ['pkascii2ogr', '-i', source, '-x', '0', '-y', '1',
                 '-a_srs', 'EPSG:4326', '-l', '-f', 'ESRI Shapefile',
                 '-o', output])

    def testVectorSampling(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = VectorSampling()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'dem.tif')
        mask = os.path.join(testDataPath, 'mask.shp')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.shp'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-s', mask, '-buf', '3',
                 '-r', 'centroid', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'RULE': 0,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-s', mask, '-buf', '3',
                 '-r', 'point', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'BUFFER': 5,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-s', mask, '-buf', '5',
                 '-r', 'centroid', '-f', 'ESRI Shapefile', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'THRESHOLD': 50,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-s', mask, '-buf', '3',
                 '-r', 'centroid', '-t', '50.0', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'RULE': 9,
                                     'CLASSES': '5,10',
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-s', mask, '-buf', '3',
                 '-r', 'mode', '-c', '5', '-c', '10', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'RULE': 12,
                                     'PERCENTILE': 75,
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-s', mask, '-buf', '3',
                 '-r', 'percentile', '-perc', '75.0', '-f', 'ESRI Shapefile',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SAMPLES': mask,
                                     'ARGUMENTS': '-b 1',
                                     'OUTPUT': output}, context, feedback),
                ['pkextractogr', '-i', source, '-s', mask, '-buf', '3',
                 '-r', 'centroid', '-b', '1', '-f', 'ESRI Shapefile',
                 '-o', output])

    def testVectorToText(self):
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        alg = VectorToText()
        alg.initAlgorithm()

        source = os.path.join(testDataPath, 'points.shp')

        with tempfile.TemporaryDirectory() as outdir:
            output = outdir + '/check.txt'

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpogr', '-i', source, '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'SEPARATOR': ';',
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpogr', '-i', source, '-fs', ';', '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'FIELDS': 'id,label',
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpogr', '-i', source, '-n', 'id', '-n', 'label',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'FIELDS': 'id,label',
                                     'TRANSPOSE': True,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpogr', '-i', source, '-n', 'id', '-n', 'label', '-t',
                 '-o', output])

            self.assertEqual(
                alg.generateCommand({'INPUT': source,
                                     'POSITION': True,
                                     'OUTPUT': output}, context, feedback),
                ['pkdumpogr', '-i', source, '-pos', '-o', output])


if __name__ == '__main__':
    nose2.main()
