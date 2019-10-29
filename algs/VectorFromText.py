# -*- coding: utf-8 -*-

"""
***************************************************************************
    VectorFromText.py
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
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterVectorDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class VectorFromText(PktoolsAlgorithm):

    INPUT = 'INPUT'
    COLUMN_X = 'COLUMN_X'
    COLUMN_Y = 'COLUMN_Y'
    CRS = 'CRS'
    FIELDS = 'FIELDS'
    SEPARATOR = 'SEPARATOR'
    CREATE_POLYGON = 'CREATE_POLYGON'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkascii2ogr'

    def name(self):
        return 'vectorfromtext'

    def displayName(self):
        return self.tr('Vector from text file')

    def group(self):
        return self.tr('Conversion')

    def groupId(self):
        return 'conversion'

    def tags(self):
        return self.tr('ascii,vector,convert,text').split(',')

    def shortHelpString(self):
        return self.tr('Creates a vector dataset (points or single '
                       'polygon) from an ASCII textfile.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input ASCII file'),
                                                     behavior=QgsProcessingParameterFile.File))
        self.addParameter(QgsProcessingParameterNumber(self.COLUMN_X,
                                                      self.tr('Number of column with X values'),
                                                      type=QgsProcessingParameterNumber.Integer,
                                                      minValue=0,
                                                      maxValue=99999999,
                                                      defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.COLUMN_Y,
                                                      self.tr('Number of column with Y values'),
                                                      type=QgsProcessingParameterNumber.Integer,
                                                      minValue=0,
                                                      maxValue=99999999,
                                                      defaultValue=1))
        self.addParameter(QgsProcessingParameterCrs(self.CRS,
                                                    self.tr('Output coordinate reference system'),
                                                    defaultValue='EPSG:4326'))

        params = []
        params.append(QgsProcessingParameterString(self.FIELDS,
                                                   self.tr('Field names and types'),
                                                   defaultValue=None,
                                                   optional=True))
        params.append(QgsProcessingParameterString(self.SEPARATOR,
                                                   self.tr('Field separator'),
                                                   defaultValue=None,
                                                   optional=True))
        params.append(QgsProcessingParameterBoolean(self.CREATE_POLYGON,
                                                    self.tr('Create polygon instead of points'),
                                                    defaultValue=False,
                                                    optional=True))
        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT,
                                                                  self.tr('Output vector')))

    def processAlgorithm(self, parameters, context, feedback):
        crs = self.parameterAsCrs(parameters, self.CRS, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(self.parameterAsFile(parameters, self.INPUT, context))
        arguments.append('-x')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.COLUMN_X, context)))
        arguments.append('-y')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.COLUMN_Y, context)))
        arguments.append('-a_srs')
        arguments.append(crs.authid())

        if self.FIELDS in parameters and parameters[self.FIELDS] is not None:
            fields = self.parameterAsString(parameters, self.FIELDS, context)
            if fields:
                arguments.append(fields)

        if self.SEPARATOR in parameters and  parameters[self.SEPARATOR] is not None:
            sep = self.parameterAsString(parameters, self.SEPARATOR, context)
            if sep:
                arguments.append('-fs')
                arguments.append(sep)

        if self.parameterAsBoolean(parameters, self.CREATE_POLYGON, context):
            arguments.append('-l')

        arguments.append('-of')
        arguments.append(QgsVectorFileWriter.driverForExtension(os.path.splitext(output)[1]))

        arguments.append('-o')
        arguments.append(output)

        pktoolsUtils.execute(arguments, feedback)

        return self.algorithmResults(parameters)
