# -*- coding: utf-8 -*-

"""
***************************************************************************
    RasterToTextMask.py
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

from qgis.core import (QgsVectorFileWriter,
                       QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBand,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFileDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class RasterToTextMask(PktoolsAlgorithm):

    INPUT = 'INPUT'
    BAND = 'BAND'
    MASK = 'MASK'
    FORMAT = 'FORMAT'
    SIZE_X = 'SIZE_X'
    SIZE_Y = 'SIZE_Y'
    RESAMPLING = 'RESAMPLING'
    ARGUMENTS = 'ARGUMENTS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkdumpimg'

    def name(self):
        return 'rastertotextmask'

    def displayName(self):
        return self.tr('Raster to text file by mask')

    def group(self):
        return self.tr('Conversion')

    def groupId(self):
        return 'conversion'

    def tags(self):
        return self.tr('ascii,raster,convert,text,mask').split(',')

    def shortHelpString(self):
        return self.tr('Dumps the content of a raster layer within '
                       'extent defined by mask layer to the text file.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.formats = ((self.tr('Matrix (row, col)'), 'matrix'),
                        (self.tr('List (x, y, z)'), 'list')
                       )

        self.methods = ((self.tr('Nearest neighbor)'), 'near'),
                        (self.tr('Bilinear'), 'bilinear')
                       )

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input raster')))
        self.addParameter(QgsProcessingParameterBand(self.BAND,
                                                     self.tr('Band to dump'),
                                                     defaultValue=1,
                                                     parentLayerParameterName=self.INPUT))
        self.addParameter(QgsProcessingParameterFeatureSource(self.MASK,
                                                              self.tr('Mask layer'),
                                                              types=[QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterEnum(self.FORMAT,
                                                     self.tr('Output format'),
                                                     options=[i[0] for i in self.formats],
                                                     defaultValue=0))

        params = []
        params.append(QgsProcessingParameterEnum(self.RESAMPLING,
                                                 self.tr('Resampling method'),
                                                 options=[i[0] for i in self.methods],
                                                 defaultValue=0))
        params.append(QgsProcessingParameterNumber(self.SIZE_X,
                                                   self.tr('Output X resolution, meters'),
                                                   type=QgsProcessingParameterNumber.Double,
                                                   minValue=0,
                                                   defaultValue=0))
        params.append(QgsProcessingParameterNumber(self.SIZE_Y,
                                                   self.tr('Output Y resolution, meters'),
                                                   type=QgsProcessingParameterNumber.Double,
                                                   minValue=0,
                                                   defaultValue=0))
        params.append(QgsProcessingParameterString(self.ARGUMENTS,
                                                   self.tr('Additional arguments'),
                                                   defaultValue=None,
                                                   optional=True))
        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output file'),
                                                                self.tr('Text files (*.txt *.TXT)')))

    def processAlgorithm(self, parameters, context, feedback):
        inLayer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        if inLayer is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))

        mask = self.parameterAsCompatibleSourceLayerPath(parameters,
                                                         self.MASK,
                                                         context,
                                                         QgsVectorFileWriter.supportedFormatExtensions(),
                                                         'shp',
                                                         feedback)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(inLayer.source())
        arguments.append('-b')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.BAND, context)))
        arguments.append('-of')
        arguments.append(self.formats[self.parameterAsEnum(parameters, self.FORMAT, context)][1])
        arguments.append('-e')
        arguments.append('{}'.format(mask))
        arguments.append('-dx')
        arguments.append('{}'.format(self.parameterAsDouble(parameters, self.SIZE_X, context)))
        arguments.append('-dy')
        arguments.append('{}'.format(self.parameterAsDouble(parameters, self.SIZE_Y, context)))
        arguments.append('-r')
        arguments.append(self.methods[self.parameterAsEnum(parameters, self.RESAMPLING, context)][1])

        if self.ARGUMENTS in parameters and  parameters[self.ARGUMENTS] is not None:
            args = self.parameterAsString(parameters, self.ARGUMENTS, context).split(' ')
            if args:
                arguments.extend(args)

        arguments.append('-o')
        arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))

        pktoolsUtils.execute(arguments, feedback)

        return self.algorithmResults(parameters)
