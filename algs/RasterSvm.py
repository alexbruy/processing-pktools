# -*- coding: utf-8 -*-

"""
***************************************************************************
    RasterSvm.py
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
                       QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class RasterSvm(PktoolsAlgorithm):

    INPUT = 'INPUT'
    TRAINING = 'TRAINING'
    FIELD = 'FIELD'
    SVM = 'SVM'
    KERNEL = 'KERNEL'
    DEGREE = 'DEGREE'
    COEF_0 = 'COEF_0'
    GAMMA = 'GAMMA'
    ARGUMENTS = 'ARGUMENTS'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pksvm'

    def name(self):
        return 'rastersvm'

    def displayName(self):
        return self.tr('Raster SVM classification')

    def group(self):
        return self.tr('Classification')

    def groupId(self):
        return 'classification'

    def tags(self):
        return self.tr('raster,classification,svm').split(',')

    def shortHelpString(self):
        return self.tr('Supervised raster classification using '
                       'support vector machine (SVM).')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.svms = ((self.tr('C-SVC'), 'C_SVC'),
                     (self.tr('nu-SVC'), 'nu_SVC'),
                     (self.tr('one-class SVM'), 'one_class'),
                     (self.tr('epsilon-SVR'), 'epsilon_SVR'),
                     (self.tr('nu-SVR'), 'nu_SVR'),
                    )

        self.kernels = ((self.tr('Linear'), 'linear'),
                        (self.tr('Polynomial'), 'polynomial'),
                        (self.tr('Radial basis function'), 'radial'),
                        (self.tr('Sigmoid'), 'sigmoid'),
                       )

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input raster')))
        self.addParameter(QgsProcessingParameterFeatureSource(self.TRAINING,
                                                              self.tr('Training vector'),
                                                              types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterField(self.FIELD,
                                                      self.tr('Class field'),
                                                      parentLayerParameterName=self.TRAINING))

        params = []
        params.append(QgsProcessingParameterEnum(self.SVM,
                                                 self.tr('Type of SVM'),
                                                 options=[i[0] for i in self.svms],
                                                 defaultValue=0))
        params.append(QgsProcessingParameterEnum(self.KERNEL,
                                                 self.tr('Kernel function'),
                                                 options=[i[0] for i in self.kernels],
                                                 defaultValue=2))
        params.append(QgsProcessingParameterNumber(self.DEGREE,
                                                   self.tr('Degree in kernel function'),
                                                   type=QgsProcessingParameterNumber.Integer,
                                                   minValue=0,
                                                   defaultValue=3,
                                                   optional=True))
        params.append(QgsProcessingParameterNumber(self.GAMMA,
                                                   self.tr('Gamma in kernel function'),
                                                   type=QgsProcessingParameterNumber.Double,
                                                   minValue=0,
                                                   defaultValue=1.0,
                                                   optional=True))
        params.append(QgsProcessingParameterNumber(self.COEF_0,
                                                   self.tr('Coef0 in kernel function'),
                                                   type=QgsProcessingParameterNumber.Double,
                                                   minValue=0,
                                                   defaultValue=0,
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

    def processAlgorithm(self, parameters, context, feedback):
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
        arguments.append('-tln')
        arguments.append(trainLayerName)
        arguments.append('-svmt')
        arguments.append(self.svms[self.parameterAsEnum(parameters, self.SVM, context)][1])
        arguments.append('-kt')
        arguments.append(self.kernels[self.parameterAsEnum(parameters, self.KERNEL, context)][1])

        if self.DEGREE in parameters and  parameters[self.DEGREE] is not None:
            arguments.append('-kd')
            arguments.append('{}'.format(self.parameterAsInt(parameters, self.DEGREE, context)))

        if self.GAMMA in parameters and  parameters[self.GAMMA] is not None:
            arguments.append('-g')
            arguments.append('{}'.format(self.parameterAsDouble(parameters, self.GAMMA, context)))

        if self.COEF_0 in parameters and  parameters[self.COEF_0] is not None:
            arguments.append('-c0')
            arguments.append('{}'.format(self.parameterAsDouble(parameters, self.COEF_0, context)))

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

        pktoolsUtils.execute(arguments, feedback)

        return self.algorithmResults(parameters)
