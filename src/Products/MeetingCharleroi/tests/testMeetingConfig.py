# -*- coding: utf-8 -*-
#
# File: testMeetingConfig.py
#
# Copyright (c) 2007-2013 by Imio.be
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
from Products.MeetingCommunes.tests.testMeetingConfig import testMeetingConfig as mctmc


class testMeetingConfig(MeetingCharleroiTestCase, mctmc):
    '''Tests the MeetingConfig class methods.'''

    def _usersToRemoveFromGroupsForUpdatePersonalLabels(self):
        """ """
        return ['pmRefAdmin1', 'pmReviewerLevel1', 'pmServiceHead1']

    def test_pm_Validate_itemWFValidationLevels_removed_used_state_in_config(self):
        """ Bypass as state label does not match """
        pass

    def test_pm_Validate_itemWFValidationLevels_removed_used_state_item(self):
        """ Bypass as state label does not match """
        pass

    def test_pm_Validate_itemWFValidationLevels_removed_depending_used_state_item(self):
        """ Bypass as state label does not match """
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testMeetingConfig, prefix='test_'))
    return suite
