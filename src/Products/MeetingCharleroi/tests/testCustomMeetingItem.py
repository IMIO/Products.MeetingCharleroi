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
from zope.i18n import translate
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.MeetingCommunes.tests.testCustomMeetingItem import testCustomMeetingItem as mctcmi
from Products.MeetingCharleroi.config import COUNCIL_DEFAULT_CATEGORY
from Products.MeetingCharleroi.config import DECISION_ITEM_SENT_TO_COUNCIL
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
        self.setupCollegeConfig()
        self.setupCouncilConfig()
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
        item1.setProposingGroupWithGroupInCharge('developers__groupincharge__groupincharge2')
        self.presentItem(item1)
        self.freezeMeeting(collegeMeeting1)
        collegeMeeting2 = self.create('Meeting', date=DateTime('2016/12/20'))
        collegeMeeting2.setExtraordinarySession(True)
        item2 = self.create('MeetingItem')
        item2.setDecision(self.decisionText)
        item2.setOtherMeetingConfigsClonableTo((cfg2Id,))
        item2.setProposingGroupWithGroupInCharge('developers__groupincharge__groupincharge2')
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
                         ['late', 'lateextracollege'])

    def test_ItemRefForActeCollege(self):
        """Test the method rendering the item reference of items in a College meeting."""
        collegeMeeting, collegeExtraMeeting = self.setupCollegeDemoData()
        self.changeUser('pmManager')
        orderedBrains = collegeMeeting.getItems(ordered=True, useCatalog=True)
        self.assertEqual(
            [brain.getObject().getItemReference() for brain in orderedBrains],
            ['2017/2/ZP/1', '2017/2/ZP/2', '2017/2/ZP/3', '2017/2/ZP/4', '2017/2/ZP/5',  # ZP items
             '2017/2/ZP/C/1', '2017/2/ZP/C/2', '2017/2/ZP/C/3', '2017/2/ZP/C/4',  # ZP items to Council
             '2017/2/ZP/C/5', '2017/2/ZP/C/6', '2017/2/ZP/C/7', '2017/2/ZP/C/8',
             '-', '-', '-',  # ZP Communications
             '2017/2/1', '2017/2/2', '2017/2/3', '2017/2/4', '2017/2/5', '2017/2/6', '2017/2/7',  # normal items
             '2017/2/C/1', '2017/2/C/2', '2017/2/C/3', '2017/2/C/4', '2017/2/C/5',  # items to Council
             '2017/2/C/6', '2017/2/C/7', '2017/2/C/8', '2017/2/C/9', '2017/2/C/10',
             '2017/2/8',  # OJ Council
             '-', '-', '-']  # communications
            )

        # now check with 'pmCreator1' that may only see items of 'developers'
        # compare with what is returned for a user that may see everything
        orderedDevelopersBrains = collegeMeeting.getItems(
            ordered=True, useCatalog=True,
            additional_catalog_query={'getProposingGroup': 'developers'})
        devRefs = [brain.getObject().getItemReference() for brain in orderedDevelopersBrains]
        self.assertEqual(
            devRefs,
            ['2017/2/3', '2017/2/4',
             '2017/2/C/4', '2017/2/C/5', '2017/2/C/6',
             '2017/2/C/7', '2017/2/C/8', '2017/2/C/9', '2017/2/C/10',
             '2017/2/8',  # OJ Council
             '-', '-', '-'])
        self.changeUser('pmCreator1')
        orderedDevelopersBrains = collegeMeeting.getItems(
            ordered=True, useCatalog=True,
            additional_catalog_query={'getProposingGroup': 'developers'})
        creator1DevRefs = [brain.getObject().getItemReference() for brain in orderedDevelopersBrains]
        self.assertEqual(devRefs, creator1DevRefs)

    def test_ItemRefForActeCouncil(self):
        """Test the method rendering the item reference of items in a College meeting."""
        meeting = self.setupCouncilDemoData()
        self.changeUser('pmManager')
        orderedBrains = meeting.getItems(ordered=True, useCatalog=True)
        self.assertEqual(
            [brain.getObject().getItemReference() for brain in orderedBrains],
            ['2017/1/1',
             '2017/1/2',
             '2017/1/U/1',
             '2017/1/3',
             '2017/1/S/1',
             '2017/1/S/2',
             '2017/1/S/3',
             '2017/1/S/4',
             '2017/1/S/5',
             '2017/1/S/6',
             '2017/1/S/7',
             '2017/1/S/8',
             '2017/1/4',
             '2017/1/5',
             '2017/1/6',
             '2017/1/7',
             '2017/1/8',
             '2017/1/9',
             '2017/1/10',
             '2017/1/U/2',
             '2017/1/U/3',
             '2017/1/U/4',
             '2017/1/11',
             '2017/1/12',
             '2017/1/13',
             '2017/1/14',
             '2017/1/15',
             '2017/1/16',
             '2017/1/17',
             '2017/1/18',
             '2017/1/U/5',
             '2017/1/U/6'])

        # now check with 'pmCreator1' that may only see items of 'developers'
        # compare with what is returned for a user that may see everything
        orderedDevelopersBrains = meeting.getItems(ordered=True, useCatalog=True,
                                                   additional_catalog_query={'getProposingGroup': 'developers'})
        devRefs = [brain.getObject().getItemReference() for brain in orderedDevelopersBrains]
        self.assertEqual(
            devRefs,
            ['2017/1/1',
             '2017/1/2',
             '2017/1/U/1',
             '2017/1/3',
             '2017/1/S/1',
             '2017/1/S/2',
             '2017/1/S/3',
             '2017/1/S/4',
             '2017/1/S/5',
             '2017/1/S/6',
             '2017/1/S/7',
             '2017/1/S/8',
             '2017/1/6',
             '2017/1/7',
             '2017/1/U/2',
             '2017/1/11',
             '2017/1/13',
             '2017/1/15',
             '2017/1/17',
             '2017/1/U/5'])
        self.changeUser('pmCreator1')
        orderedDevelopersBrains = meeting.getItems(ordered=True, useCatalog=True,
                                                   additional_catalog_query={'getProposingGroup': 'developers'})
        creator1DevRefs = [brain.getObject().getItemReference() for brain in orderedDevelopersBrains]
        self.assertEqual(devRefs, creator1DevRefs)

    def test_ItemDecisionWhenSentToCouncil(self):
        """When a College item is sent to Council, the decision field displays a special sentence."""
        cfg = self.meetingConfig
        cfg.setItemManualSentToOtherMCStates(('itemcreated', ))
        cfg2Id = self.meetingConfig2.getId()

        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        item.setDecision(self.decisionText)
        self.assertNotEqual(item.getDecision(), DECISION_ITEM_SENT_TO_COUNCIL)
        item.setOtherMeetingConfigsClonableTo((cfg2Id,))
        item.cloneToOtherMeetingConfig(cfg2Id)
        councilItem = item.getItemClonedToOtherMC(cfg2Id)

        # College item decision is different
        self.assertEqual(item.getDecision(), DECISION_ITEM_SENT_TO_COUNCIL)
        self.assertEqual(councilItem.getDecision(), self.decisionText)

        # if College item is duplicated, the original decision is used
        duplicatedItem = item.clone()
        self.assertEqual(duplicatedItem.getDecision(), self.decisionText)

        # if item sent to Council is removed, the original decision
        # is displayed again on the College item
        self.deleteAsManager(councilItem.UID())
        self.assertEqual(item.getDecision(), self.decisionText)

    def test_ItemDecisionNotLostWhenItemNotToSendToCouncilAnymore(self):
        """When a College item is to send to Council, the decision field displays a special sentence.
           Make sure when removing fact that item is to send to Council, original decision is not lost."""
        cfg = self.meetingConfig
        cfg.setItemManualSentToOtherMCStates(('itemcreated', ))
        cfg2Id = self.meetingConfig2.getId()

        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        item.setDecision(self.decisionText)
        item.setOtherMeetingConfigsClonableTo((cfg2Id,))
        councilItem = item.cloneToOtherMeetingConfig(cfg2Id)
        self.assertEqual(item.getDecision(), DECISION_ITEM_SENT_TO_COUNCIL)

        # editing the item should not lose the original decision
        item.processForm(
            values={'otherMeetingConfigsClonableTo': (cfg2Id, ),
                    'decision': DECISION_ITEM_SENT_TO_COUNCIL})
        self.assertEqual(item.getDecision(), DECISION_ITEM_SENT_TO_COUNCIL)
        # not thru the accessor
        self.assertEqual(item.decision(), self.decisionText)

        # now, removing to send to Council will not lose original decision neither
        item.processForm(
            values={'otherMeetingConfigsClonableTo': (),
                    'decision': DECISION_ITEM_SENT_TO_COUNCIL})
        self.assertEqual(item.getDecision(), DECISION_ITEM_SENT_TO_COUNCIL)
        # not thru the accessor
        self.assertEqual(item.decision(), self.decisionText)

        # if item sent to Council is removed, the original decision
        # is displayed again on the College item
        self.deleteAsManager(councilItem.UID())
        self.assertEqual(item.getDecision(), self.decisionText)

    def test_CategoryIndetermineeNotAllowedIfCollegeItemToSendToCouncil(self):
        """Use of category 'indeterminee' on MeetingItemCollege is not allowed
           if item will be sent to Council."""
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        item.setOtherMeetingConfigsClonableTo(('meeting-config-council',))
        msg = translate(msgid='category_indeterminee_not_allowed',
                        domain='PloneMeeting',
                        context=self.request)
        # as item is to send to Council, category 'indeterminee' can be used
        self.failIf(item.validate_category(COUNCIL_DEFAULT_CATEGORY))
        self.failIf(item.validate_category('another_category'))

        # but can not be used for items not to send to Council
        item.setOtherMeetingConfigsClonableTo(())
        self.assertEqual(item.validate_category(COUNCIL_DEFAULT_CATEGORY), msg)
        self.failIf(item.validate_category('another_category'))

        # does not fail when used on MeetingItemCouncil
        self.setMeetingConfig(self.meetingConfig2.getId())
        self.changeUser('pmManager')
        council_item = self.create('MeetingItem')
        self.assertEqual(council_item.portal_type, 'MeetingItemCouncil')
        self.failIf(council_item.validate_category(COUNCIL_DEFAULT_CATEGORY))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeetingItem, prefix='test_'))
    return suite
