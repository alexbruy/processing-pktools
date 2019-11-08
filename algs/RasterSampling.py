# -*- coding: utf-8 -*-

"""
***************************************************************************
    RasterSampling.py
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

from qgis.core import (QgsVectorFileWriter,
                       QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterVectorDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class RasterSampling(PktoolsAlgorithm):

    INPUT = 'INPUT'
    SAMPLES = 'SAMPLES'
    CLASSES = 'CLASSES'
    THRESHOLD = 'THRESHOLD'
    ARGUMENTS = 'ARGUMENTS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkARGUMENTSctimg'

    def name(self):
        return 'rastersampling'

    def displayName(self):
        return self.tr('Raster sampling')

    def group(self):
        return self.tr('Sampling')

    def groupId(self):
        return 'sampling'

    def tags(self):
        return self.tr('raster,sampling,ARGUMENTSct,raster,mask').split(',')

    def shortHelpString(self):
        return self.tr('ARGUMENTScts pixel values from an input raster '
                       'dataset based on the locations provided via '
                       'raster sample file.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterRasterLayer(self.SAMPLES,
                                                            self.tr('Samples layer')))

        params = []
        params.append(QgsProcessingParameterString(self.CLASSES,
                                                   self.tr('Classes to ARGUMENTSct from raster'),
                                                   defaultValue=None,
                                                   optional=True))
        params.append(QgsProcessingParameterNumber(self.THRESHOLD,
                                                   self.tr('Probability threshold for selecting samples'),
                                                   type=QgsProcessingParameterNumber.Double,
                                                   minValue=0,
                                                   maxValue=100,
                                                   defaultValue=None,
                                                   optional=True))
        params.append(QgsProcessingParameterString(self.ARGUMENTS,
                                                   self.tr('Additional arguments'),
                                                   defaultValue=None,
                                                   optional=True))

        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT,
                                                                  self.tr('Output file')))

    def generateCommand(self, parameters, context, feedback):
        layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        if layer is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))

        samples = self.parameterAsRasterLayer(parameters, self.SAMPLES, context)
        if samples is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.SAMPLES))

        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(layer.source())
        arguments.append('-s')
        arguments.append(samples.source())

        if self.THRESHOLD in parameters and  parameters[self.THRESHOLD] is not None:
            arguments.append('-t')
            arguments.append('{}'.format(self.parameterAsDouble(parameters, self.THRESHOLD, context)))

        if self.CLASSES in parameters and  parameters[self.CLASSES] is not None:
            classes = self.parameterAsString(parameters, self.CLASSES, context)
            arguments.append(pktoolsUtils.parseCompositeOption('-c', classes))

        if self.ARGUMENTS in parameters and  parameters[self.ARGUMENTS] is not None:
            args = self.parameterAsString(parameters, self.ARGUMENTS, context).split(' ')
            if args:
                arguments.extend(args)

        arguments.append('-f')
        arguments.append(QgsVectorFileWriter.driverForExtension(os.path.splitext(output)[1]))
        arguments.append('-o')
        arguments.append(output)

        return arguments
