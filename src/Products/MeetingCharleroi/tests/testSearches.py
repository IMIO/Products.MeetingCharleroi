# -*- coding: utf-8 -*-
#
# File: testMeetingConfig.py
#
# GNU General Public License (GPL)
#

from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCommunes.tests.testSearches import testSearches as mcts


class testSearches(MeetingCharleroiTestCase, mcts):
    """Test searches."""

    def test_pm_SearchItemsToCorrectToValidateOfEveryReviewerGroups(self):
        """Bypass users are different"""
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSearches, prefix='test_'))
    return suite
