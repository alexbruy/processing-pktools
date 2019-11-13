# -*- coding: utf-8 -*-

"""
***************************************************************************
    Sieve.py
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
                       QgsProcessingParameterBand,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class Sieve(PktoolsAlgorithm):

    INPUT = 'INPUT'
    BAND = 'BAND'
    SIZE = 'SIZE'
    CONNECTEDNESS = 'CONNECTEDNESS'
    MASK = 'MASK'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pksieve'

    def name(self):
        return 'sieve'

    def displayName(self):
        return self.tr('Sieve')

    def group(self):
        return self.tr('Filters')

    def groupId(self):
        return 'filters'

    def tags(self):
        return self.tr('raster,filter,sieve').split(',')

    def shortHelpString(self):
        return self.tr('Filters small objects in a raster by replacing '
                       'them with the values of the largest neighbour '
                       'object.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.directions = ((self.tr('8 directions'), '8'),
                           (self.tr('4 directions'), '4'),
                          )

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterBand(self.BAND,
                                                     self.tr('Band to use'),
                                                     defaultValue=1,
                                                     parentLayerParameterName=self.INPUT))
        self.addParameter(QgsProcessingParameterNumber(self.SIZE,
                                                      self.tr('Maximum size of small objects'),
                                                      type=QgsProcessingParameterNumber.Integer,
                                                      minValue=0,
                                                      defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.CONNECTEDNESS,
                                                     self.tr('Connectedness'),
                                                     options=[i[0] for i in self.directions],
                                                     defaultValue=0))


        params = []
        params.append(QgsProcessingParameterRasterLayer(self.MASK,
                                                        self.tr('Mask layer'),
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
        arguments.append('-b')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.BAND, context)))
        arguments.append('-s')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.SIZE, context)))
        arguments.append('-c')
        arguments.append(self.directions[self.parameterAsEnum(parameters, self.CONNECTEDNESS, context)][1])

        if self.MASK in parameters and  parameters[self.MASK] is not None:
            mask = self.parameterAsString(parameters, self.MASK, context)
            if mask:
                arguments.append('-m')
                arguments.append(filePath)

        if self.OPTIONS in parameters and  parameters[self.OPTIONS] is not None:
            options = self.parameterAsString(parameters, self.OPTIONS, context)
            if options:
                arguments.extend(pktoolsUtils.parseCreationOptions(options))

        arguments.append('-of')
        arguments.append(QgsRasterFileWriter.driverForExtension(os.path.splitext(output)[1]))
        arguments.append('-o')
        arguments.append(output)

        return arguments
