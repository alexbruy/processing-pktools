# -*- coding: utf-8 -*-

"""
***************************************************************************
    FillNoData.py
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

from qgis.core import (QgsProcessingException,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBand,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class FillNoData(PktoolsAlgorithm):

    INPUT = 'INPUT'
    BANDS = 'BANDS'
    MASK = 'MASK'
    DISTANCE = 'DISTANCE'
    ITERATIONS = 'ITERATIONS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkfillnodata'

    def name(self):
        return 'fillnodata'

    def displayName(self):
        return self.tr('Fill nodata')

    def group(self):
        return self.tr('Raster tools')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('raster,nodata,fill').split(',')

    def shortHelpString(self):
        return self.tr('Fills nodata values in a raster dataset.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterBand(self.BANDS,
                                                     self.tr('Band(s) to use'),
                                                     defaultValue=1,
                                                     parentLayerParameterName=self.INPUT,
                                                     allowMultiple=True))
        self.addParameter(QgsProcessingParameterRasterLayer(self.MASK,
                                                            self.tr('Mask layer')))
        self.addParameter(QgsProcessingParameterNumber(self.DISTANCE,
                                                      self.tr('Search distance for interpolation'),
                                                      type=QgsProcessingParameterNumber.Integer,
                                                      minValue=0,
                                                      defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.ITERATIONS,
                                                      self.tr('Number of filter passes'),
                                                      type=QgsProcessingParameterNumber.Integer,
                                                      minValue=0,
                                                      defaultValue=0))

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT,
                                                                  self.tr('Output file')))

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        if layer is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))

        mask = self.parameterAsRasterLayer(parameters, self.MASK, context)
        if mask is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.MASK))

        bands = self.parameterAsInts(parameters, self.BANDS, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(layer.source())
        arguments.append('-m')
        arguments.append(mask.source())
        arguments.extend(pktoolsUtils.parseCompositeOption('-b', bands))
        arguments.append('-d')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.DISTANCE, context)))
        arguments.append('-it')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.ITERATIONS, context)))

        arguments.append('-of')
        arguments.append(QgsRasterFileWriter.driverForExtension(os.path.splitext(output)[1]))
        arguments.append('-o')
        arguments.append(output)

        pktoolsUtils.execute(arguments, feedback)

        return self.algorithmResults(parameters)
