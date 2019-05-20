# -*- coding: utf-8 -*-

"""
***************************************************************************
    pktoolsAlgorithm.py
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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsProcessingAlgorithm

from processing_pktools import pktoolsUtils

pluginPath = os.path.dirname(__file__)


class PktoolsAlgorithm(QgsProcessingAlgorithm):

    def __init__(self):
        super().__init__()

    def createInstance(self):
        return type(self)()

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'icons', 'pktools.svg'))

    def commandName(self):
        return self.name()

    def command(self):
        return os.path.join(pktoolsUtils.pktoolsDirectory(), self.commandName())

    def algorithmResults(self, parameters):
        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results

    def helpUrl(self):
        return 'http://pktools.nongnu.org/html/{}.html'.format(self.name())

    def tr(self, text):
        return QCoreApplication.translate(self.__class__.__name__, text)
