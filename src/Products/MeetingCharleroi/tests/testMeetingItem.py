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

from DateTime import DateTime


class testMeetingItem(MeetingCharleroiTestCase, mctmi):
    """
        Tests the MeetingItem class methods.
    """

    def test_pm_SendItemToOtherMCTriggeredTransitionsAreUnrestricted(self):
        '''When the item is sent automatically to the other MC, if current user,
           most of time a MeetingManager, is not able to trigger the transition,
           it is triggered nevertheless.'''
        # create an item with group 'vendors', pmManager is not able to trigger
        # any transition on it
        cfg = self.meetingConfig
        cfg2 = self.meetingConfig2
        cfg2Id = cfg2.getId()
        cfg.setUseGroupsAsCategories(True)
        cfg2.setUseGroupsAsCategories(True)
        cfg2.setInsertingMethodsOnAddItem(({'insertingMethod': 'on_proposing_groups',
                                            'reverse': '0'}, ))
        cfg.setItemAutoSentToOtherMCStates(('validated', ))
        cfg.setMeetingConfigsToCloneTo(({'meeting_config': '%s' % cfg2Id,
                                         'trigger_workflow_transitions_until': '%s.%s' %
                                         (cfg2Id, 'present')},))
        self.changeUser('pmCreator2')
        self.tool.getPloneMeetingFolder(cfg2Id)
        vendorsItem = self.create('MeetingItem')
        vendorsItem.setDecision('<p>My decision</p>', mimetype='text/html')
        vendorsItem.setOtherMeetingConfigsClonableTo((cfg2Id,))

        # pmManager may not validate it
        self.changeUser('pmManager')

        # create a meeting
        self.setMeetingConfig(cfg2Id)
        self.create('Meeting', date=DateTime() + 1)
        self.assertFalse(self.transitions(vendorsItem))
        # item is automatically sent when it is validated
        self.changeUser('admin')
        self.do(vendorsItem, 'propose')
        self.do(vendorsItem, 'proposeToRefAdmin')
        self.do(vendorsItem, 'prevalidate')
        self.do(vendorsItem, 'validate')

        # and it has been presented
        sentItem = vendorsItem.getItemClonedToOtherMC(destMeetingConfigId=cfg2Id)
        self.assertTrue(sentItem.queryState() == 'presented')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testMeetingItem, prefix='test_pm_'))
    return suite
