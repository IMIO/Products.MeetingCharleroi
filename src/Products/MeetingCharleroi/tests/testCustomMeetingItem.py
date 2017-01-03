# -*- coding: utf-8 -*-
#
# File: testCustomMeetingItem.py
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

from DateTime import DateTime
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.MeetingCommunes.tests.testCustomMeetingItem import testCustomMeetingItem as mctcmi
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCharleroi.setuphandlers import _configureCollegeCustomAdvisers
from Products.MeetingCharleroi.setuphandlers import _createFinancesGroup


class testCustomMeetingItem(MeetingCharleroiTestCase, mctcmi):
    """
        Tests the MeetingItem adapted methods
    """
    def test_FinancesAdviserOnlyMayEvaluateCompleteness(self):
        '''Only finances adviser may evaluate completeness when item is 'waiting_advices'.'''
        self.changeUser('admin')
        # configure customAdvisers for 'meeting-config-college'
        _configureCollegeCustomAdvisers(self.portal)
        # add finances group
        _createFinancesGroup(self.portal)
        # put users in finances group
        self._setupFinancesGroup()
        # completeness widget is disabled for items of the config
        cfg = self.meetingConfig
        self.changeUser('siteadmin')
        recurringItem = cfg.getRecurringItems()[0]
        templateItem = cfg.getItemTemplates(as_brains=False)[0]
        self.assertFalse(recurringItem.adapted().mayEvaluateCompleteness())
        self.assertFalse(templateItem.adapted().mayEvaluateCompleteness())
        self.assertFalse(recurringItem.adapted().mayAskCompletenessEvalAgain())
        self.assertFalse(templateItem.adapted().mayAskCompletenessEvalAgain())

        # creator may not evaluate
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        self.assertTrue(item.getCompleteness() == 'completeness_not_yet_evaluated')
        self.assertTrue(self.hasPermission(ModifyPortalContent, item))
        self.assertFalse(item.adapted().mayEvaluateCompleteness())

        # reviewer may not evaluate
        self.proposeItem(item)
        self.changeUser('pmReviewer1')
        self.assertTrue(self.hasPermission(ModifyPortalContent, item))
        self.assertFalse(item.adapted().mayEvaluateCompleteness())

        # not sendable to 'waiting_advices' if finances advice not asked
        self.assertFalse('wait_advices' in self.transitions(item))
        item.setOptionalAdvisers(('dirfin__rowid__2016-05-01.0', ))
        item.at_post_edit_script()
        self.do(item, 'wait_advices_from_prevalidated')
        self.assertFalse(item.adapted().mayEvaluateCompleteness())

        # finances controller is able to evaluate
        self.changeUser('pmFinController')
        self.assertTrue(self.hasPermission(View, item))
        self.assertTrue(item.adapted().mayEvaluateCompleteness())
        itemCompletenessView = item.restrictedTraverse('item-completeness')
        # and even able to change it
        self.assertTrue(itemCompletenessView.listSelectableCompleteness())

    def test_LateExtraCollege(self):
        """When an item is presented into a Council meeting and is coming from
           a College item that is presented to a College meeting, the listType used
           is not 'late' but 'lateextracollege'."""
        cfg = self.meetingConfig
        cfgId = cfg.getId()
        cfg2 = self.meetingConfig2
        cfg2Id = cfg2.getId()
        # items will be immediatelly presented to the Council meeting while sent
        self.setupCouncilWorkflows()
        cfg.setMeetingConfigsToCloneTo(
            ({'meeting_config': cfg2Id,
              'trigger_workflow_transitions_until': '%s.%s' % (cfg2Id, 'validate')}, ))
        cfg.setItemAutoSentToOtherMCStates(('itemfrozen', ))
        # create 2 College meetings, one extraordinarySession and one normal session
        # then send an item from each to a Council meeting
        self.changeUser('pmManager')
        # create the Council meeting
        self.setMeetingConfig(cfg2Id)
        councilMeeting = self.create('Meeting', date=DateTime('2017/01/01'))
        self.freezeMeeting(councilMeeting)
        # create elements in College
        self.setMeetingConfig(cfgId)
        collegeMeeting1 = self.create('Meeting', date=DateTime('2016/12/15'))
        item1 = self.create('MeetingItem')
        item1.setDecision(self.decisionText)
        item1.setOtherMeetingConfigsClonableTo((cfg2Id,))
        self.presentItem(item1)
        self.freezeMeeting(collegeMeeting1)
        collegeMeeting2 = self.create('Meeting', date=DateTime('2016/12/20'))
        collegeMeeting2.setExtraordinarySession(True)
        item2 = self.create('MeetingItem')
        item2.setDecision(self.decisionText)
        item2.setOtherMeetingConfigsClonableTo((cfg2Id,))
        self.presentItem(item2)
        self.freezeMeeting(collegeMeeting2)

        # now in the council, present the new items
        self.setCurrentMeeting(councilMeeting)

        itemFromExtraSession = item2.getItemClonedToOtherMC(cfg2Id)
        itemFromExtraSession.setPreferredMeeting(councilMeeting.UID())
        itemFromExtraSession.setCategory('deployment')
        self.presentItem(itemFromExtraSession)
        self.assertEqual(itemFromExtraSession.getListType(), 'lateextracollege')

        itemNotFromExtraSession = item1.getItemClonedToOtherMC(cfg2Id)
        itemNotFromExtraSession.setPreferredMeeting(councilMeeting.UID())
        itemNotFromExtraSession.setCategory('deployment')
        self.presentItem(itemNotFromExtraSession)
        self.assertEqual(itemNotFromExtraSession.getListType(), 'late')

        # items are inserted following listType and listType 'lateextracollege'
        # will be after 'late'
        self.assertEqual([item.getListType() for item in councilMeeting.getItems(ordered=True)],
                         ['lateextracollege', 'late'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeetingItem, prefix='test_'))
    return suite
