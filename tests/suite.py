# -*- coding: utf-8 -*-

"""
***************************************************************************
    suite.py
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

import sys
import unittest


def _run_tests(test_suite, package_name):
    count = test_suite.countTestCases()
    print('########')
    print('{} tests has been discovered in {}'.format(count, package_name))
    print('########')

    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(test_suite)


def test_all(package='.'):
    test_loader = unittest.defaultTestLoader
    test_suite = test_loader.discover(package)
    _run_tests(test_suite, package)


if __name__ == '__main__':
    test_all()
