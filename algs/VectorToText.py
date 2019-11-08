# -*- coding: utf-8 -*-

"""
***************************************************************************
    VectorToText.py
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
                       QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFileDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class VectorToText(PktoolsAlgorithm):

    INPUT = 'INPUT'
    FIELDS = 'FIELDS'
    SEPARATOR = 'SEPARATOR'
    POSITION = 'POSITION'
    TRANSPOSE = 'TRANSPOSE'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkdumpogr'

    def name(self):
        return 'vectortotext'

    def displayName(self):
        return self.tr('Vector to text file')

    def group(self):
        return self.tr('Conversion')

    def groupId(self):
        return 'conversion'

    def tags(self):
        return self.tr('ascii,vector,convert,text').split(',')

    def shortHelpString(self):
        return self.tr('Dumps the content of a vector dataset to the text file.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr('Input vector')))

        params = []
        params.append(QgsProcessingParameterString(self.FIELDS,
                                                   self.tr('Fields to export'),
                                                   defaultValue=None,
                                                   optional=True))
        params.append(QgsProcessingParameterString(self.SEPARATOR,
                                                   self.tr('Field separator'),
                                                   defaultValue=None,
                                                   optional=True))
        params.append(QgsProcessingParameterBoolean(self.POSITION,
                                                    self.tr('Include position (X and Y)'),
                                                    defaultValue=False,
                                                    optional=True))
        params.append(QgsProcessingParameterBoolean(self.TRANSPOSE,
                                                    self.tr('Transpose output'),
                                                    defaultValue=False,
                                                    optional=True))

        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output file'),
                                                                self.tr('Text files (*.txt *.TXT)')))

    def generateCommand(self, parameters, context, feedback):
        layer, layerName = self.parameterAsCompatibleSourceLayerPathAndLayerName(parameters,
                                                                                 self.INPUT,
                                                                                 context,
                                                                                 QgsVectorFileWriter.supportedFormatExtensions(),
                                                                                 'gpkg',
                                                                                 feedback)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(layer)
        arguments.append('-ln')
        arguments.append(layerName)

        useFields = False
        if self.FIELDS in parameters and parameters[self.FIELDS] is not None:
            fields = self.parameterAsString(parameters, self.FIELDS, context)
            if fields:
                arguments.append(fields)
                useFields = True

        if self.parameterAsBoolean(parameters, self.POSITION, context):
            arguments.append('-pos')

        if self.parameterAsBoolean(parameters, self.TRANSPOSE, context):
            if not useFields:
                raise QgsProcessingException(self.tr('Transposing output only possible in combination with "-n" parameter.'))
            else:
                arguments.append('-t')

        arguments.append('-o')
        arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))

        return arguments
