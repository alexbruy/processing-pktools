# -*- coding: utf-8 -*-

"""
***************************************************************************
    SunShadow.py
    ---------------------
    Date                 : October 2019
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
__date__ = 'October 2019'
__copyright__ = '(C) 2019, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import (QgsRasterFileWriter,
                       QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class SunShadow(PktoolsAlgorithm):

    INPUT = 'INPUT'
    ZENITH_ANGLE = 'ZENITH_ANGLE'
    AZIMUTH_ANGLE = 'AZIMUTH_ANGLE'
    SHADOW = 'SHADOW'
    DATA_TYPE = 'DATA_TYPE'
    COLOR_TABLE = 'COLOR_TABLE'
    EXTRA = 'EXTRA'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkdsm2shadow'

    def name(self):
        return 'sunshadow'

    def displayName(self):
        return self.tr('Sun shadow')

    def group(self):
        return self.tr('Raster tools')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('raster,dem,sun,shadow,mask').split(',')

    def shortHelpString(self):
        return self.tr('Creates a binary shadow mask from a digital '
                       'surface model, based on the Sun zenith and '
                       'azimuth angles.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.dataTypes = [self.tr('Use input layer data type'),
                          'Byte', 'Int16', 'UInt16', 'UInt32', 'Int32',
                          'Float32', 'Float64',
                          'CInt16', 'CInt32', 'CFloat32', 'CFloat64'
                         ]


        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input DEM')))
        self.addParameter(QgsProcessingParameterNumber(self.ZENITH_ANGLE,
                                                      self.tr('Sun zenith angle'),
                                                      type=QgsProcessingParameterNumber.Double,
                                                      minValue=0,
                                                      maxValue=360,
                                                      defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber(self.AZIMUTH_ANGLE,
                                                      self.tr('Sun azimuth angle'),
                                                      type=QgsProcessingParameterNumber.Double,
                                                      minValue=0,
                                                      maxValue=360,
                                                      defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber(self.SHADOW,
                                                      self.tr('Value for shadow pixels'),
                                                      type=QgsProcessingParameterNumber.Double,
                                                      defaultValue=0))

        params = []
        params.append(QgsProcessingParameterEnum(self.DATA_TYPE,
                                                 self.tr('Output data type'),
                                                 options=self.dataTypes,
                                                 defaultValue=0))
        params.append(QgsProcessingParameterFile(self.COLOR_TABLE,
                                                 self.tr('Color table'),
                                                 behavior=QgsProcessingParameterFile.File,
                                                 optional=True))
        params.append(QgsProcessingParameterString(self.EXTRA,
                                                   self.tr('Additional parameters'),
                                                   defaultValue=None,
                                                   optional=True))

        options = QgsProcessingParameterString(self.OPTIONS,
                                               self.tr('Raster creation options'),
                                               defaultValue=None,
                                               optional=True)
        options.setMetadata({
            'widget_wrapper': {
                'class': 'processing.algs.gdal.ui.RasterOptionsWidget.RasterOptionsWidgetWrapper'}})
        params.append(options)

        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT,
                                                                  self.tr('Output file')))

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        if layer is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))

        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(layer.source())
        arguments.append('-sza')
        arguments.append('{}'.format(self.parameterAsDouble(parameters, self.ZENITH_ANGLE, context)))
        arguments.append('-saa')
        arguments.append('{}'.format(self.parameterAsDouble(parameters, self.AZIMUTH_ANGLE, context)))
        arguments.append('-f')
        arguments.append('{}'.format(self.parameterAsDouble(parameters, self.SHADOW, context)))

        if self.COLOR_TABLE in parameters and  parameters[self.COLOR_TABLE] is not None:
            filePath = self.parameterAsString(parameters, self.COLOR_TABLE, context)
            if filePath:
                arguments.append('-ct')
                arguments.append(filePath)

        if self.OPTIONS in parameters and  parameters[self.OPTIONS] is not None:
            options = self.parameterAsString(parameters, self.OPTIONS, context)
            if options:
                arguments.extend(pktoolsUtils.parseCreationOptions(options))

        if self.EXTRA in parameters and  parameters[self.EXTRA] is not None:
            extra = self.parameterAsString(parameters, self.EXTRA, context)
            if extra:
                arguments.append(extra)

        dataType = self.parameterAsEnum(parameters, self.DATA_TYPE, context)
        if dataType:
            arguments.append('-ot')
            arguments.append(self.datatypes[dataType])

        arguments.append('-of')
        arguments.append(QgsRasterFileWriter.driverForExtension(os.path.splitext(output)[1]))

        arguments.append('-o')
        arguments.append(output)

        pktoolsUtils.execute(arguments, feedback)

        return self.algorithmResults(parameters)
