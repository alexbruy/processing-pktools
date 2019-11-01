# -*- coding: utf-8 -*-

"""
***************************************************************************
    SpatialFilter.py
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

from qgis.core import (QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class SpatialFilter(PktoolsAlgorithm):

    INPUT = 'INPUT'

    FILTER = 'FILTER'
    KERNEL_X = 'KERNEL_X'
    KERNEL_Y = 'KERNEL_Y'
    CIRCULAR = 'CIRCULAR'
    EXTRA = 'EXTRA'
    OPTIONS = 'OPTIONS'

    OUTPUT = 'OUTPUT'

    def commandName(self):
        return 'pkfilter'

    def name(self):
        return 'spatialfilter'

    def displayName(self):
        return self.tr('Spatial filter')

    def group(self):
        return self.tr('Filters')

    def groupId(self):
        return 'filters'

    def tags(self):
        return self.tr('raster,filter,spatial').split(',')

    def shortHelpString(self):
        return self.tr('Spatial filtering for rasters.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.filters = ((self.tr('Morphological dilation'), 'dilate'),
                        (self.tr('Morphological erosion'), 'erode'),
                        (self.tr('Morpholigical closing'), 'close'),
                        (self.tr('Morpholigical opening'), 'open'),
                        (self.tr('Smooth NODATA'), 'smoothnodata'),
                        (self.tr('Number of valid values'), 'nvalid'),
                        (self.tr('Median'), 'median'),
                        (self.tr('Variance'), 'var'),
                        (self.tr('Minimum'), 'min'),
                        (self.tr('Maximum'), 'max'),
                        (self.tr('Sum'), 'sum'),
                        (self.tr('Mean'), 'mean'),
                        (self.tr('Standard deviation'), 'stdev'),
                        (self.tr('Savitzky-Golay'), 'savgolay'),
                        (self.tr('Percentile'), 'percentile'),
                        (self.tr('Proportion'), 'proportion'),
                        (self.tr('Discrete wavelet transform'), 'dwt'),
                        (self.tr('Discrete inverse wavelet transform'), 'dwti'),
                        (self.tr('Discrete wavelet + inverse with cut'), 'dwt_cut'),
                        (self.tr('Markov random field'), 'mrf'),
                        (self.tr('Is minimum?'), 'ismin'),
                        (self.tr('Is maximum?'), 'ismax'),
                        (self.tr('Pixel shift'), 'shift'),
                        (self.tr('Scramble'), 'scramble'),
                        (self.tr('Mode'), 'mode'),
                        (self.tr('Horizontal edge detection'), 'sobelx'),
                        (self.tr('Vertical edge detection'), 'sobely'),
                        (self.tr('Diagonal edge detection (NE-SW)'), 'sobelxy'),
                        (self.tr('Diagonal edge detection (NW-SE)'), 'sobelyx'),
                        (self.tr('Count digital numbers'), 'countid'),
                        (self.tr('Rank pixels in order'), 'order'),
                        (self.tr('Density'), 'density'),
                        (self.tr('Homogenity'), 'homog'),
                        (self.tr('Heterogenity'), 'heterog'),
                        (self.tr('Sauvola\'s thresholding'), 'sauvola'),
                       )

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterEnum(self.FILTER,
                                                     self.tr('Post-processing filter'),
                                                     options=[i[0] for i in self.filters],
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.KERNEL_X,
                                                      self.tr('Kernel size in X'),
                                                      type=QgsProcessingParameterNumber.Integer,
                                                      minValue=0,
                                                      defaultValue=3))
        self.addParameter(QgsProcessingParameterNumber(self.KERNEL_Y,
                                                      self.tr('Kernel size in Y'),
                                                      type=QgsProcessingParameterNumber.Integer,
                                                      minValue=0,
                                                      defaultValue=3))

        params = []
        params.append(QgsProcessingParameterBoolean(self.CIRCULAR,
                                                    self.tr('Use circular disc kernel for dilation and erosion'),
                                                    defaultValue=False))
        params.append(QgsProcessingParameterString(self.EXTRA,
                                                   self.tr('Additional parameters'),
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

        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        arguments.append('-i')
        arguments.append(layer.source())
        arguments.append('-f')
        arguments.append(self.filters[self.parameterAsEnum(parameters, self.FILTER, context)][1])
        arguments.append('-dx')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.KERNEL_X, context)))
        arguments.append('-dy')
        arguments.append('{}'.format(self.parameterAsInt(parameters, self.KERNEL_Y, context)))

        if self.parameterAsBoolean(parameters, self.CIRCULAR, context):
            arguments.append('-circ')

        if self.EXTRA in parameters and  parameters[self.EXTRA] is not None:
            extra = self.parameterAsString(parameters, self.EXTRA, context)
            if extra:
                arguments.append(extra)

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
