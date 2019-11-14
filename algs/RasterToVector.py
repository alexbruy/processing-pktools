# -*- coding: utf-8 -*-

"""
***************************************************************************
    RasterToVector.py
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

import os

from qgis.core import (QgsVectorFileWriter,
                       QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBand,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterVectorDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class RasterToVector(PktoolsAlgorithm):

    INPUT = 'INPUT'
    BAND = 'BAND'
    MASK = 'MASK'
    FIELD_NAME = 'FIELD_NAME'
    NODATA = 'NODATA'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkpolygonize'

    def name(self):
        return 'rastertovector'

    def displayName(self):
        return self.tr('Raster to vector (polygonize)')

    def group(self):
        return self.tr('Conversion')

    def groupId(self):
        return 'conversion'

    def tags(self):
        return self.tr('raster,convert,vector,polygonize').split(',')

    def shortHelpString(self):
        return self.tr('Converts a raster to a vector dataset.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input raster')))
        self.addParameter(QgsProcessingParameterBand(self.BAND,
                                                     self.tr('Band to use'),
                                                     defaultValue=1,
                                                     parentLayerParameterName=self.INPUT))
        self.addParameter(QgsProcessingParameterRasterLayer(self.MASK,
                                                            self.tr('Mask layer'),
                                                            optional=True))
        params = []
        params.append(QgsProcessingParameterString(self.FIELD_NAME,
                                                   self.tr('Field name'),
                                                   defaultValue='DN'))
        params.append(QgsProcessingParameterNumber(self.NODATA,
                                                   self.tr('Discard this NODATA value when creating polygons'),
                                                   type=QgsProcessingParameterNumber.Double,
                                                   defaultValue=0))
        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT,
                                                                  self.tr('Output file'),
                                                                  QgsProcessing.TypeVectorPolygon))

    def generateCommand(self, parameters, context, feedback):
        layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        if layer is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))

        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(layer.source())
        arguments.append('-b')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.BAND, context) - 1))

        if self.MASK in parameters and parameters[self.MASK] is not None:
            mask = self.parameterAsRasterLayer(parameters, self.MASK, context)
            if mask:
                arguments.append('-m')
                arguments.append(mask.source())

        arguments.append('-n')
        arguments.append(self.parameterAsString(parameters, self.FIELD_NAME, context))

        if self.NODATA in parameters and parameters[self.NODATA] is not None:
            arguments.append('-nodata')
            arguments.append('{}'.format(self.parameterAsDouble(parameters, self.NODATA, context)))

        arguments.append('-f')
        arguments.append(QgsVectorFileWriter.driverForExtension(os.path.splitext(output)[1]))
        arguments.append('-o')
        arguments.append(output)

        return arguments
