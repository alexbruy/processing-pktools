# -*- coding: utf-8 -*-

"""
***************************************************************************
    LasToRaster.py
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

from qgis.core import (QgsRasterFileWriter,
                       QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class LasToRaster(PktoolsAlgorithm):

    INPUT = 'INPUT'
    ATTRIBUTE = 'ATTRIBUTE'
    COMPOSITE = 'COMPOSITE'
    FILTER = 'FILTER'
    EXTENT = 'EXTENT'
    SIZE_X = 'SIZE_X'
    SIZE_Y = 'SIZE_Y'
    CRS = 'CRS'
    CLASSES = 'CLASSES'
    ARGUMENTS = 'ARGUMENTS'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pklas2img'

    def name(self):
        return 'lastoraster'

    def displayName(self):
        return self.tr('LAS to raster')

    def group(self):
        return self.tr('Conversion')

    def groupId(self):
        return 'conversion'

    def tags(self):
        return self.tr('raster,convert,las,rasterize').split(',')

    def shortHelpString(self):
        return self.tr('Converts a LAS/LAZ point cloud into a gridded '
                       'raster dataset. Based on the liblas.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.attributes = ((self.tr('Intensity'), 'intensity'),
                           (self.tr('Angle'), 'angle'),
                           (self.tr('Return'), 'return'),
                           (self.tr('Number of returns'), 'nreturn'),
                           (self.tr('Spacing'), 'spacing'),
                           (self.tr('Height'), 'z'),
                          )

        self.composites = ((self.tr('Minimum'), 'min'),
                           (self.tr('Maximum'), 'max'),
                           (self.tr('Absolute minimum'), 'absmin'),
                           (self.tr('Absolute maximum'), 'absmax'),
                           (self.tr('Median'), 'median'),
                           (self.tr('Mean'), 'mean'),
                           (self.tr('Sum'), 'sum'),
                           (self.tr('First'), 'first'),
                           (self.tr('Last'), 'last'),
                           (self.tr('Percentile height values'), 'profile'),
                           (self.tr('Percentile'), 'percentile'),
                           (self.tr('Point density'), 'number'),
                          )

        self.filters = ((self.tr('First'), 'first'),
                        (self.tr('Last'), 'last'),
                        (self.tr('Single'), 'single'),
                        (self.tr('Multiple'), 'multiple'),
                        (self.tr('All'), 'all'),
                       )

        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input LAS file'),
                                                     behavior=QgsProcessingParameterFile.File,
                                                     fileFilter=self.tr('Point cloud (*.las *.LAS *.laz *.LAZ)')))
        self.addParameter(QgsProcessingParameterEnum(self.ATTRIBUTE,
                                                     self.tr('Attribute to select'),
                                                     options=[i[0] for i in self.attributes],
                                                     defaultValue=5))
        self.addParameter(QgsProcessingParameterEnum(self.COMPOSITE,
                                                     self.tr('Composite for multiple points in the cell'),
                                                     options=[i[0] for i in self.composites],
                                                     defaultValue=8))
        self.addParameter(QgsProcessingParameterEnum(self.FILTER,
                                                     self.tr('Returns to selects'),
                                                     options=[i[0] for i in self.filters],
                                                     defaultValue=4))
        self.addParameter(QgsProcessingParameterExtent(self.EXTENT,
                                                       self.tr('Extent to process'),
                                                       optional=True))
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
                                                    self.tr('Output coordinate reference system')))

        params = []
        params.append(QgsProcessingParameterString(self.CLASSES,
                                                   self.tr('Classes to keep'),
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
        crs = self.parameterAsCrs(parameters, self.CRS, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(self.parameterAsFile(parameters, self.INPUT, context))
        arguments.append('-n')
        arguments.append(self.attributes[self.parameterAsEnum(parameters, self.ATTRIBUTE, context)][1])
        arguments.append('-comp')
        arguments.append(self.composites[self.parameterAsEnum(parameters, self.COMPOSITE, context)][1])
        arguments.append('-fir')
        arguments.append(self.filters[self.parameterAsEnum(parameters, self.FILTER, context)][1])

        if self.EXTENT in parameters and  parameters[self.EXTENT] is not None:
            bbox = self.parameterAsExtent(parameters, self.EXTENT, context, crs)
            arguments.append('-ulx')
            arguments.append('{}'.format(bbox.xMinimum()))
            arguments.append('-uly')
            arguments.append('{}'.format(bbox.yMaximum()))
            arguments.append('-lrx')
            arguments.append('{}'.format(bbox.xMaximum()))
            arguments.append('-lry')
            arguments.append('{}'.format(bbox.yMinimum()))

        arguments.append('-dx')
        arguments.append('{}'.format(self.parameterAsDouble(parameters, self.SIZE_X, context)))
        arguments.append('-dy')
        arguments.append('{}'.format(self.parameterAsDouble(parameters, self.SIZE_Y, context)))
        arguments.append('-a_srs')
        arguments.append(crs.authid())

        if self.CLASSES in parameters and  parameters[self.CLASSES] is not None:
            classes = self.parameterAsString(parameters, self.CLASSES, context)
            if classes != '':
                arguments.extend(pktoolsUtils.parseCompositeOption('-class', classes))

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
