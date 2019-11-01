# -*- coding: utf-8 -*-

"""
***************************************************************************
    FilterDem.py
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

from qgis.core import (QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class FilterDem(PktoolsAlgorithm):

    INPUT = 'INPUT'
    FILTER = 'FILTER'
    KERNEL_SIZE = 'KERNEL_SIZE'
    CIRCULAR = 'CIRCULAR'
    SLOPE_THRESHOLD = 'SLOPE_THRESHOLD'
    MIN_CHANGE = 'MIN_CHANGE'
    DATA_TYPE = 'DATA_TYPE'
    COLOR_TABLE = 'COLOR_TABLE'
    EXTRA = 'EXTRA'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkfilterdem'

    def name(self):
        return 'filterdem'

    def displayName(self):
        return self.tr('Filter DEM')

    def group(self):
        return self.tr('Filters')

    def groupId(self):
        return 'filters'

    def tags(self):
        return self.tr('raster,filter,dem').split(',')

    def shortHelpString(self):
        return self.tr('Filters DEM.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.dataTypes = [self.tr('Use input layer data type'),
                          'Byte', 'Int16', 'UInt16', 'UInt32', 'Int32',
                          'Float32', 'Float64',
                          'CInt16', 'CInt32', 'CFloat32', 'CFloat64'
                         ]

        self.filters = ((self.tr('vito'), 'vito'),
                        (self.tr('etew_min'), 'etew_min'),
                        (self.tr('Progressive morphological'), 'promorph'),
                        (self.tr('Morpholigical opening'), 'open'),
                        (self.tr('Morpholigical closing'), 'close')
                       )

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterEnum(self.FILTER,
                                                     self.tr('Post-processing filter'),
                                                     options=[i[0] for i in self.filters],
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.KERNEL_SIZE,
                                                      self.tr('Maximum filter kernel size'),
                                                      type=QgsProcessingParameterNumber.Integer,
                                                      minValue=0,
                                                      defaultValue=17))

        params = []
        params.append(QgsProcessingParameterBoolean(self.CIRCULAR,
                                                    self.tr('Use circular disc kernel for dilation and erosion'),
                                                    defaultValue=False))
        params.append(QgsProcessingParameterNumber(self.SLOPE_THRESHOLD,
                                                   self.tr('Slope threshold'),
                                                   type=QgsProcessingParameterNumber.Double,
                                                   minValue=0,
                                                   defaultValue=0))
        params.append(QgsProcessingParameterNumber(self.MIN_CHANGE,
                                                   self.tr('Minimum number of changes before stopping'),
                                                   type=QgsProcessingParameterNumber.Integer,
                                                   minValue=0,
                                                   defaultValue=0))
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
        arguments.append('-f')
        arguments.append(self.filters[self.parameterAsEnum(parameters, self.FILTER, context)][1])
        arguments.append('-dim')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.KERNEL_SIZE, context)))

        if self.parameterAsBoolean(parameters, self.CIRCULAR, context):
            arguments.append('-circ')

        arguments.append('-st')
        arguments.append('{}'.format(self.parameterAsDouble(parameters, self.SLOPE_THRESHOLD, context)))
        arguments.append('-minchange')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.MIN_CHANGE, context)))

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
