# -*- coding: utf-8 -*-

"""
***************************************************************************
    RasterFromText.py
    ---------------------
    Date                 : May 2019
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
__date__ = 'May 2019'
__copyright__ = '(C) 2019, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import (QgsRasterFileWriter,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class RasterFromText(PktoolsAlgorithm):

    INPUT = 'INPUT'
    UL_POINT = 'UL_POINT'
    SIZE_X = 'SIZE_X'
    SIZE_Y = 'SIZE_Y'
    CRS = 'CRS'
    ARGUMENTS = 'ARGUMENTS'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkascii2img'

    def name(self):
        return 'rasterfromtext'

    def displayName(self):
        return self.tr('Raster from text file')

    def group(self):
        return self.tr('Conversion')

    def groupId(self):
        return 'conversion'

    def tags(self):
        return self.tr('ascii,raster,convert,text').split(',')

    def shortHelpString(self):
        return self.tr('Creates a raster dataset from an ASCII text '
                       'file. The text file is in matrix format (rows '
                       'and columns). The dimensions in X and Y are '
                       'defined by the number of columns and rows '
                       'respectively.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input ASCII file'),
                                                     behavior=QgsProcessingParameterFile.File))
        self.addParameter(QgsProcessingParameterPoint(self.UL_POINT,
                                                      self.tr('Upper left corner of bounding box')))
        self.addParameter(QgsProcessingParameterNumber(self.SIZE_X,
                                                      self.tr('Output X resolution, meters'),
                                                      type=QgsProcessingParameterNumber.Double,
                                                      minValue=0,
                                                      defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber(self.SIZE_Y,
                                                      self.tr('Output Y resolution, meters'),
                                                      type=QgsProcessingParameterNumber.Double,
                                                      minValue=0,
                                                      defaultValue=None))
        self.addParameter(QgsProcessingParameterCrs(self.CRS,
                                                    self.tr('Output coordinate reference system'),
                                                    defaultValue='EPSG:4326'))
        params = []
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
                                                                  self.tr('Output raster')))

    def processAlgorithm(self, parameters, context, feedback):
        point = self.parameterAsPoint(parameters, self.UL_POINT, context)
        crs = self.parameterAsCrs(parameters, self.CRS, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(self.parameterAsFile(parameters, self.INPUT, context))

        arguments.append('-ulx')
        arguments.append('{}'.format(point.x()))
        arguments.append('-uly')
        arguments.append('{}'.format(point.y()))
        arguments.append('-dx')
        arguments.append('{}'.format(self.parameterAsDouble(parameters, self.SIZE_X, context)))
        arguments.append('-dy')
        arguments.append('{}'.format(self.parameterAsDouble(parameters, self.SIZE_Y, context)))
        arguments.append('-a_srs')
        arguments.append(crs.authid())

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
