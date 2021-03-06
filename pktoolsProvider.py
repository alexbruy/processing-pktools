# -*- coding: utf-8 -*-

"""
***************************************************************************
    pktoolsProvider.py
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

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import QgsProcessingProvider

from processing.core.ProcessingConfig import ProcessingConfig, Setting

from processing_pktools.algs.ApplyColorTable import ApplyColorTable
from processing_pktools.algs.CreateColorTable import CreateColorTable
from processing_pktools.algs.FillNoData import FillNoData
from processing_pktools.algs.FilterDem import FilterDem
from processing_pktools.algs.LasToRaster import LasToRaster
from processing_pktools.algs.RandomSampling import RandomSampling
from processing_pktools.algs.RasterAnn import RasterAnn
from processing_pktools.algs.RasterComposite import RasterComposite
from processing_pktools.algs.RasterFromText import RasterFromText
from processing_pktools.algs.RasterSampling import RasterSampling
from processing_pktools.algs.RasterSvm import RasterSvm
from processing_pktools.algs.RasterToTextExtent import RasterToTextExtent
from processing_pktools.algs.RasterToTextMask import RasterToTextMask
from processing_pktools.algs.RasterToVector import RasterToVector
from processing_pktools.algs.RegularSampling import RegularSampling
from processing_pktools.algs.Sieve import Sieve
from processing_pktools.algs.SpatialFilter import SpatialFilter
from processing_pktools.algs.SpectralFilter import SpectralFilter
from processing_pktools.algs.SunShadow import SunShadow
from processing_pktools.algs.VectorFromText import VectorFromText
from processing_pktools.algs.VectorSampling import VectorSampling
from processing_pktools.algs.VectorToText import VectorToText

from processing_pktools import pktoolsUtils

pluginPath = os.path.dirname(__file__)


class PktoolsProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()
        self.algs = []

    def id(self):
        return 'pktools'

    def name(self):
        return 'pktools'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'icons', 'pktools.svg'))

    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.name(),
                                            pktoolsUtils.PKTOOLS_DIRECTORY,
                                            self.tr('pktools directory'),
                                            pktoolsUtils.pktoolsDirectory(),
                                            valuetype=Setting.FOLDER))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        ProcessingConfig.removeSetting(pktoolsUtils.PKTOOLS_DIRECTORY)

    def supportsNonFileBasedOutput(self):
        return False

    def getAlgs(self):
        algs = [
                ApplyColorTable(),
                CreateColorTable(),
                FillNoData(),
                FilterDem(),
                LasToRaster(),
                RandomSampling(),
                RasterAnn(),
                RasterComposite(),
                RasterFromText(),
                RasterSampling(),
                RasterSvm(),
                RasterToTextExtent(),
                RasterToTextMask(),
                RasterToVector(),
                RegularSampling(),
                Sieve(),
                SpatialFilter(),
                SpectralFilter(),
                SunShadow(),
                VectorFromText(),
                VectorSampling(),
                VectorToText(),
               ]

        return algs

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

    def tr(self, string):
        return QCoreApplication.translate(self.__class__.__name__, string)
