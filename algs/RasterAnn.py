# -*- coding: utf-8 -*-

"""
***************************************************************************
    RasterAnn.py
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

from qgis.core import (QgsRasterFileWriter,
                       QgsVectorFileWriter,
                       QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class RasterAnn(PktoolsAlgorithm):

    INPUT = 'INPUT'
    TRAINING = 'TRAINING'
    FIELD = 'FIELD'
    NEURONS = 'NEURONS'
    N_FOLD = 'N_FOLD'
    ARGUMENTS = 'ARGUMENTS'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkann'

    def name(self):
        return 'rasterann'

    def displayName(self):
        return self.tr('Raster ANN classification')

    def group(self):
        return self.tr('Classification')

    def groupId(self):
        return 'classification'

    def tags(self):
        return self.tr('raster,classification,ann').split(',')

    def shortHelpString(self):
        return self.tr('Supervised raster classification using '
                       'artificial neural network (ANN).')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input raster')))
        self.addParameter(QgsProcessingParameterFeatureSource(self.TRAINING,
                                                              self.tr('Training vector'),
                                                              types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterField(self.FIELD,
                                                      self.tr('Class field'),
                                                      parentLayerParameterName=self.TRAINING))

        params = []
        params.append(QgsProcessingParameterString(self.NEURONS,
                                                   self.tr('Number of neurons'),
                                                   defaultValue=None,
                                                   optional=True))
        params.append(QgsProcessingParameterNumber(self.N_FOLD,
                                                   self.tr('N-fold cross validation'),
                                                   type=QgsProcessingParameterNumber.Integer,
                                                   minValue=0,
                                                   defaultValue=None,
                                                   optional=True))
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

    def generateCommand(self, parameters, context, feedback):
        layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        if layer is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))

        training = self.parameterAsSource(parameters, self.TRAINING, context)
        if training is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.TRAINING))

        trainLayer, trainLayerName = self.parameterAsCompatibleSourceLayerPathAndLayerName(parameters,
                                                                                           self.TRAINING,
                                                                                           context,
                                                                                           QgsVectorFileWriter.supportedFormatExtensions(),
                                                                                           'gpkg',
                                                                                           feedback)

        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(layer.source())
        arguments.append('-t')
        arguments.append(trainLayer)
        if trainLayerName:
            arguments.append('-tln')
            arguments.append(trainLayerName)
        arguments.append('-label')
        arguments.append(self.parameterAsString(parameters, self.FIELD, context))

        if self.NEURONS in parameters and  parameters[self.NEURONS] is not None:
            neurons = self.parameterAsString(parameters, self.NEURONS, context)
            arguments.extend(pktoolsUtils.parseCompositeOption('-nn', neurons))

        if self.N_FOLD in parameters and  parameters[self.N_FOLD] is not None:
            arguments.append('-cv')
            arguments.append('{}'.format(self.parameterAsInt(parameters, self.N_FOLD, context)))

        if self.ARGUMENTS in parameters and  parameters[self.ARGUMENTS] is not None:
            args = self.parameterAsString(parameters, self.ARGUMENTS, context).split(' ')
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

        return arguments
