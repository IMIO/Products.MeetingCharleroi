# -*- coding: utf-8 -*-
#
# File: testMeetingItem.py
#
# Copyright (c) 2013 by Imio.be
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


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testMeetingItem, prefix="test_pm_"))
    return suite
