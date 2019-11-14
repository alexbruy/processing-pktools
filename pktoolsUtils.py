# -*- coding: utf-8 -*-

"""
***************************************************************************
    pktoolsUtils.py
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
import sys
import shlex
import subprocess

from qgis.core import Qgis, QgsMessageLog, QgsProcessingFeedback
from processing.core.ProcessingLog import ProcessingLog
from processing.core.ProcessingConfig import ProcessingConfig

PKTOOLS_DIRECTORY = 'PKTOOLS_DIRECTORY'


def pktoolsDirectory():
    filePath = ProcessingConfig.getSetting(PKTOOLS_DIRECTORY)
    return filePath if filePath is not None else ''


def prepareArguments(arguments):
    if sys.platform == 'win32':
        return subprocess.list2cmdline(arguments)
    else:
        prepared = []
        for a in arguments:
            prepared.append(shlex.quote(a))
        return ' '.join(prepared)


def parseCreationOptions(value):
    return parseCompositeOption('-co', value, '|')


def parseCompositeOption(switch, value, separator=','):
    options = []

    if isinstance(value, list):
        for v in value:
            options.extend([switch, str(v)])
    else:
        parts = value.split(separator)
        for p in parts:
            options.extend([switch, p.strip()])

    return options


def execute(commands, feedback=None):
    command = prepareArguments(commands)

    if feedback is None:
        feedback = QgsProcessingFeedback()

    QgsMessageLog.logMessage(command, 'Processing', Qgis.Info)
    feedback.pushInfo('pktools command:')
    feedback.pushCommandInfo(command)
    feedback.pushInfo('pktools command output:')

    loglines = []
    with subprocess.Popen(command,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stdin=subprocess.DEVNULL,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True) as proc:
        try:
            for line in iter(proc.stdout.readline, ''):
                feedback.pushConsoleInfo(line)
                loglines.append(line)
        except:
            pass
