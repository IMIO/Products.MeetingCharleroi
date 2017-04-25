# -*- coding: utf-8 -*-
#
# File: testPerformances.py
#
# Copyright (c) 2017 by Imio.be
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.PloneMeeting.tests.testPerformances import testPerformances as pmtp


class testPerformances(MeetingCharleroiTestCase, pmtp):
    ''' '''

    def _setItemReferenceFormat(self):
        """Compute item ref for acte College."""
        self.meetingConfig.setItemReferenceFormat(
            "python: context.adapted().getItemRefForActe()")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # this will only launch the 'test_pm_Update250ItemsItemReference' test
    suite.addTest(makeSuite(testPerformances, prefix='test_pm_Update250ItemsItemReference'))
    return suite
