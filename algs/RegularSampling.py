# -*- coding: utf-8 -*-

"""
***************************************************************************
    RegularSampling.py
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
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterVectorDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class RegularSampling(PktoolsAlgorithm):

    INPUT = 'INPUT'
    RULE = 'RULE'
    CELL_SIZE = 'CELL_SIZE'
    BUFFER = 'BUFFER'
    CLASSES = 'CLASSES'
    THRESHOLD = 'THRESHOLD'
    PERCENTILE = 'PERCENTILE'
    ARGUMENTS = 'ARGUMENTS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkARGUMENTSctogr'

    def name(self):
        return 'regularsampling'

    def displayName(self):
        return self.tr('Regular sampling')

    def group(self):
        return self.tr('Sampling')

    def groupId(self):
        return 'sampling'

    def tags(self):
        return self.tr('raster,sampling,ARGUMENTSct,regular,grid').split(',')

    def shortHelpString(self):
        return self.tr('ARGUMENTScts pixel values from an input raster '
                       'dataset following a systematic grid with '
                       'user-defined cell size.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.rules = ((self.tr('Single pixel'), 'point'),
                      (self.tr('All pixels'), 'allpoints'),
                      (self.tr('Centroid of the polygon'), 'centroid'),
                      (self.tr('Average within polygon'), 'mean'),
                      (self.tr('Standard deviation within polygon'), 'stdev'),
                      (self.tr('Median within polygon'), 'median'),
                      (self.tr('Minimum within polygon'), 'min'),
                      (self.tr('Maximum within polygon'), 'max'),
                      (self.tr('Sum within polygon'), 'sum'),
                      (self.tr('Mode of classes within polygon'), 'mode'),
                      (self.tr('Proportion of classes within polygon'), 'proportion'),
                      (self.tr('Count of classes within polygon'), 'count'),
                      (self.tr('Percentile of values within polygon'), 'percentile'),
                     )

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterEnum(self.RULE,
                                                     self.tr('Sampling rule'),
                                                     options=[i[0] for i in self.rules],
                                                     defaultValue=2))
        self.addParameter(QgsProcessingParameterNumber(self.CELL_SIZE,
                                                       self.tr('Grid cell size'),
                                                       type=QgsProcessingParameterNumber.Double,
                                                       minValue=0,
                                                       defaultValue=100))

        params = []
        params.append(QgsProcessingParameterNumber(self.BUFFER,
                                                   self.tr('Buffer for point features, pixels'),
                                                   type=QgsProcessingParameterNumber.Integer,
                                                   minValue=0,
                                                   defaultValue=3))
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
        params.append(QgsProcessingParameterNumber(self.PERCENTILE,
                                                   self.tr('Percentile'),
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

        rule = self.rules[self.parameterAsEnum(parameters, self.RULE, context)][1]
        if rule in ('mode', 'proportion', 'count') and (self.CLASSES not in parameters or parameters[self.CLASSES] is None):
            raise QgsProcessingException(self.tr('Please specify classes to ARGUMENTSct or choose another ARGUMENTSction rule.'))

        if rule == 'percentile' and (self.PERCENTILE not in parameters or parameters[self.PERCENTILE] is None):
            raise QgsProcessingException(self.tr('Please specify percentile or choose another ARGUMENTSction rule.'))


        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(layer.source())
        arguments.append('-grid')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.CELL_SIZE, context)))
        arguments.append('-buf')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.BUFFER, context)))
        arguments.append('-r')
        arguments.append(rule)

        if rule in ('mode', 'proportion', 'count'):
            classes = self.parameterAsString(parameters, self.CLASSES, context)
            arguments.append(pktoolsUtils.parseCompositeOption('-c', classes))

        if rule == 'persentile':
            arguments.append('-perc')
            arguments.append('{}'.format(self.parameterAsDouble(parameters, self.PERCENTILE, context)))

        if self.THRESHOLD in parameters and  parameters[self.THRESHOLD] is not None:
            arguments.append('-t')
            arguments.append('{}'.format(self.parameterAsDouble(parameters, self.THRESHOLD, context)))

        if self.ARGUMENTS in parameters and  parameters[self.ARGUMENTS] is not None:
            args = self.parameterAsString(parameters, self.ARGUMENTS, context).split(' ')
            if args:
                arguments.extend(args)

        arguments.append('-f')
        arguments.append(QgsVectorFileWriter.driverForExtension(os.path.splitext(output)[1]))
        arguments.append('-o')
        arguments.append(output)

        return arguments
