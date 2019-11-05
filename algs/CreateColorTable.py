# -*- coding: utf-8 -*-

"""
***************************************************************************
    CreateColorTable.py
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
                       QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRange,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class CreateColorTable(PktoolsAlgorithm):

    INPUT = 'INPUT'
    RANGE = 'RANGE'
    GRAYSCALE = 'GRAYSCALE'
    ARGUMENTS = 'ARGUMENTS'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkcreatect'

    def name(self):
        return 'createcolortable'

    def displayName(self):
        return self.tr('Create color table')

    def group(self):
        return self.tr('Raster tools')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('raster,color,table,apply').split(',')

    def shortHelpString(self):
        return self.tr('Creates and adds a color table to the raster.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input raster')))
        self.addParameter(QgsProcessingParameterRange(self.RANGE,
                                                     self.tr('Min and max values for color table'),
                                                     type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterBoolean(self.GRAYSCALE,
                                                        self.tr('Greyscale color table'),
                                                        defaultValue=False))

        params = []
        params.append(QgsProcessingParameterString(self.ARGUMENTS,
                                                   self.tr('Additional arguments'),
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

        interval = self.parameterAsRange(parameters, self.RANGE, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(layer.source())
        arguments.append('-min')
        arguments.append('{}'.format(interval[0]))
        arguments.append('-max')
        arguments.append('{}'.format(interval[1]))

        if self.parameterAsBoolean(parameters, self.GRAYSCALE, context):
            arguments.append('-g')

        if self.ARGUMENTS in parameters and  parameters[self.ARGUMENTS] is not None:
            args = self.parameterAsString(parameters, self.ARGUMENTS, context)
            if args:
                arguments.extend(args)

        if self.OPTIONS in parameters and  parameters[self.OPTIONS] is not None:
            options = self.parameterAsString(parameters, self.OPTIONS, context)
            if options:
                arguments.extend(pktoolsUtils.parseCreationOptions(options))

        arguments.append('-of')
        arguments.append(QgsRasterFileWriter.driverForExtension(os.path.splitext(output)[1]))
        arguments.append('-o')
        arguments.append(output)

        pktoolsUtils.execute(arguments, feedback)

        return self.algorithmResults(parameters)
