# -*- coding: utf-8 -*-
#
# File: testMeetingItem.py
#
# GNU General Public License (GPL)
#

from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCommunes.tests.testMeetingItem import testMeetingItem as mctmi


class testMeetingItem(MeetingCharleroiTestCase, mctmi):
    """
    Tests the MeetingItem class methods.
    """

    def test_pm_Completeness(self):
        """Already tested in testCustomMeetingItem."""
        pass

    def _extraNeutralFields(self):
        """ """
        return ["bourgmestreObservations"]

    def test_pm_SendItemToOtherMCKeptFields(self):
        """Do not launch this test because it fails as College item sent to
        the council have a specific management of the getDecision accessor."""
        pass

    def test_pm_SendItemToOtherMCManually(self):
        """Bypass as final state does not match and it's tested in testCustomMeetingItem."""
        pass

    def test_pm__sendCopyGroupsMailIfRelevant(self):
        """Bypass users are different"""
        pass

    def test_pm_SendItemToOtherMCAutoReplacedFields(self):
        """Bypass as it is failing because of DECISION_ITEM_SENT_TO_COUNCIL."""
        pass


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testMeetingItem, prefix="test_pm_"))
    return suite
