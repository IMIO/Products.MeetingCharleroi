# -*- coding: utf-8 -*-
#
# File: testMeetingConfig.py
#
# GNU General Public License (GPL)
#

from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCommunes.tests.testMeetingConfig import testMeetingConfig as mctmc


class testMeetingConfig(MeetingCharleroiTestCase, mctmc):
    '''Tests the MeetingConfig class methods.'''

    def _usersToRemoveFromGroupsForUpdatePersonalLabels(self):
        """ """
        return ['pmReviewerLevel1', 'pmServiceHead1']

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
