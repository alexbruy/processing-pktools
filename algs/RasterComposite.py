# -*- coding: utf-8 -*-

"""
***************************************************************************
    RasterComposite.py
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
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterDestination
                      )

from processing_pktools.pktoolsAlgorithm import PktoolsAlgorithm
from processing_pktools import pktoolsUtils


class RasterComposite(PktoolsAlgorithm):

    INPUT = 'INPUT'
    RULE = 'RULE'
    BANDS = 'BANDS'
    ARGUMENTS = 'ARGUMENTS'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'pkcomposite'

    def displayName(self):
        return self.tr('Composite')

    def group(self):
        return self.tr('Utilities')

    def groupId(self):
        return 'utilities'

    def tags(self):
        return self.tr('raster,composite').split(',')

    def shortHelpString(self):
        return self.tr('Composite multiple raster datasets. Compositing '
                       'resolves the overlapping pixels according to '
                       'some rule (e.g, the median of all overlapping pixels).')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.rules = ((self.tr('Overwrite overlapping pixels'), 'overwrite'),
                      (self.tr('Maximum NDVI'), 'maxndvi'),
                      (self.tr('Maximum value'), 'maxband'),
                      (self.tr('Minimum value'), 'minband'),
                      (self.tr('Mean (average) of overlapping pixels'), 'mean'),
                      (self.tr('Standard deviation of overlapping pixels'), 'stdev'),
                      (self.tr('Median of overlapping pixels'), 'median'),
                      (self.tr('Mode of overlapping pixels'), 'mode'),
                      (self.tr('Arithmetic sum of overlapping pixels'), 'sum'),
                      (self.tr('Maximum value found in all overlapping pixels'), 'maxallbands'),
                      (self.tr('Minimum value found in all overlapping pixels'), 'minallbands'))

        self.addParameter(QgsProcessingParameterMultipleLayers(self.INPUT,
                                                               self.tr('Input rasters'),
                                                               layerType=QgsProcessing.TypeRaster))
        self.addParameter(QgsProcessingParameterString(self.BANDS,
                                                       self.tr('Bands used in the composite rule (comma-separated)'),
                                                       defaultValue=None))
        self.addParameter(QgsProcessingParameterEnum(self.RULE,
                                                      self.tr('Composite rule'),
                                                      options=[i[0] for i in self.rules],
                                                      defaultValue=0))

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
        layers = self.parameterAsLayerList(parameters, self.INPUT, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        arguments = []
        arguments.append(self.commandName())
        for l in layers:
            arguments.append('-i')
            arguments.append(l.source())

        arguments.append('-cr')
        arguments.append(self.rules[self.parameterAsEnum(parameters, self.RULE, context)][1])

        bands = self.parameterAsString(parameters, self.RULE_BANDS, context)
        if bands == '':
            raise QgsProcessingException(self.tr('Please specify bands to use in composite rule.'))
        else:
            arguments.extend(pktoolsUtils.parseCompositeOption('-cb', bands))

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
