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
from Products.MeetingCharleroi.config import COMMUNICATION_CAT_ID
from Products.MeetingCharleroi.config import COUNCIL_DEFAULT_CATEGORY
from Products.MeetingCharleroi.config import DECISION_ITEM_SENT_TO_COUNCIL
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.MeetingCommunes.tests.testCustomMeetingItem import testCustomMeetingItem as mctcmi
from Products.PloneMeeting.utils import org_id_to_uid
from zope.i18n import translate


class testCustomMeetingItem(MeetingCharleroiTestCase, mctcmi):
    """
        Tests the MeetingItem adapted methods
    """
    def test_FinancesAdviserOnlyMayEvaluateCompleteness(self):
        '''Only finances adviser may evaluate completeness when item is 'waiting_advices'.'''
        self.changeUser('admin')
        self._configureFinancesAdvice(self.meetingConfig)
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
        item.setOptionalAdvisers(('{0}__rowid__unique_id_002'.format(finance_group_uid()), ))
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

        cfg.setItemAutoSentToOtherMCStates(('itemfrozen', ))
        # create 2 College meetings, one extraordinarySession and one normal session
        # then send an item from each to a Council meeting
        # create the Council meeting
        self.setMeetingConfig(cfg2Id)
        self.setupCouncilConfig()
        councilMeeting = self.create('Meeting', date=DateTime('2017/01/01').asdatetime())
        self.freezeMeeting(councilMeeting)
        # create elements in College
        self.setMeetingConfig(cfgId)
        collegeMeeting1 = self.create('Meeting', date=DateTime('2016/12/15').asdatetime())
        item1 = self.create('MeetingItem')
        item1.setDecision(self.decisionText)
        item1.setOtherMeetingConfigsClonableTo((cfg2Id,))
        gic2_uid = org_id_to_uid('groupincharge2')
        dev_group_in_charge = '{0}__groupincharge__{1}'.format(self.developers_uid, gic2_uid)
        item1.setProposingGroupWithGroupInCharge(dev_group_in_charge)
        self.presentItem(item1)
        self.freezeMeeting(collegeMeeting1)
        collegeMeeting2 = self.create('Meeting', date=DateTime('2016/12/20').asdatetime())
        collegeMeeting2.extraordinary_session = True
        item2 = self.create('MeetingItem')
        item2.setDecision(self.decisionText)
        item2.setOtherMeetingConfigsClonableTo((cfg2Id,))
        item2.setProposingGroupWithGroupInCharge(dev_group_in_charge)

        self.presentItem(item2)
        self.freezeMeeting(collegeMeeting2)

        # now in the council, present the new items
        self.setCurrentMeeting(councilMeeting)

        itemFromExtraSession = item2.getItemClonedToOtherMC(cfg2Id)
        itemFromExtraSession.setPreferredMeeting(councilMeeting.UID())
        itemFromExtraSession.setCategory('deployment')

        communicationitem = itemFromExtraSession.clone()
        communicationitem.setCategory(COMMUNICATION_CAT_ID)

        self.presentItem(itemFromExtraSession)
        self.assertEqual(itemFromExtraSession.getListType(), 'lateextracollege')
        self.presentItem(communicationitem)
        self.assertNotEqual(communicationitem.getListType(), 'lateextracollege')

        itemNotFromExtraSession = item1.getItemClonedToOtherMC(cfg2Id)
        itemNotFromExtraSession.setPreferredMeeting(councilMeeting.UID())
        itemNotFromExtraSession.setCategory('deployment')

        self.presentItem(itemNotFromExtraSession)
        self.assertEqual(itemNotFromExtraSession.getListType(), 'late')

        # items are inserted following listType and listType 'lateextracollege'
        # will be after 'late'
        self.assertEqual([item.getListType() for item in councilMeeting.get_items(ordered=True)],
                         ['late', 'lateextracollege'])

    def test_ListTypeCommunication(self):
        self.setupCouncilConfig()
        self.setMeetingConfig(self.meetingConfig2.getId())
        self.create('meetingcategory',
                    id='%ss' % COMMUNICATION_CAT_ID,
                    title='Communications')
        gic2_uid = org_id_to_uid('groupincharge2')
        dev_group_in_charge = '{0}__groupincharge__{1}'.format(self.developers_uid, gic2_uid)

        self.changeUser('pmManager')
        councilMeeting = self.create('Meeting', date=DateTime('2017/01/01').asdatetime())
        self.setCurrentMeeting(councilMeeting)

        item1 = self.create('MeetingItem')
        item1.setProposingGroupWithGroupInCharge(dev_group_in_charge)
        self.presentItem(item1)
        item2 = self.create('MeetingItem', category=COMMUNICATION_CAT_ID)
        item2.setProposingGroupWithGroupInCharge(dev_group_in_charge)
        self.presentItem(item2)
        self.assertEqual(item2.getListType(), 'communication')
        self.freezeMeeting(councilMeeting)
        item3 = self.create('MeetingItem',
                            category='%ss' % COMMUNICATION_CAT_ID,
                            preferredMeeting=councilMeeting.UID())
        item3.setProposingGroupWithGroupInCharge(dev_group_in_charge)
        self.presentItem(item3)
        self.assertEqual(item3.getListType(), 'communication')
        item4 = self.create('MeetingItem', preferredMeeting=councilMeeting.UID())
        item4.setProposingGroupWithGroupInCharge(dev_group_in_charge)
        self.presentItem(item4)

        self.assertEqual([item.getListType() for item in councilMeeting.get_items(ordered=True)],
                         ['normal', 'late', 'communication', 'communication'])

    def test_ItemRefForActeCollege(self):
        """Test the method rendering the item reference of items in a College meeting."""
        collegeMeeting, collegeExtraMeeting = self.setupCollegeDemoData()
        self.changeUser('pmManager')
        items = collegeMeeting.get_items(ordered=True)
        year = collegeMeeting.date.year
        self.assertEqual(
            [item.getItemReference() for item in items],
            ['{0}/1/ZP/1'.format(year), '{0}/1/ZP/2'.format(year), '{0}/1/ZP/3'.format(year),
             '{0}/1/ZP/4'.format(year), '{0}/1/ZP/5'.format(year),  # ZP items
             '{0}/1/ZP/C/1'.format(year), '{0}/1/ZP/C/2'.format(year),
             '{0}/1/ZP/C/3'.format(year), '{0}/1/ZP/C/4'.format(year),  # ZP items to Council
             '{0}/1/ZP/C/5'.format(year), '{0}/1/ZP/C/6'.format(year),
             '{0}/1/ZP/C/7'.format(year), '{0}/1/ZP/C/8'.format(year),
             '-', '-', '-',  # ZP Communications
             '{0}/1/1'.format(year), '{0}/1/2'.format(year), '{0}/1/3'.format(year),
             '{0}/1/4'.format(year), '{0}/1/5'.format(year), '{0}/1/6'.format(year),
             '{0}/1/7'.format(year),  # normal items
             '{0}/1/C/1'.format(year), '{0}/1/C/2'.format(year), '{0}/1/C/3'.format(year),
             '{0}/1/C/4'.format(year), '{0}/1/C/5'.format(year),  # items to Council
             '{0}/1/C/6'.format(year), '{0}/1/C/7'.format(year), '{0}/1/C/8'.format(year),
             '{0}/1/C/9'.format(year), '{0}/1/C/10'.format(year), '{0}/1/8'.format(year),  # OJ Council
             '-', '-', '-'])  # communications

        # now check with 'pmCreator1' that may only see items of 'developers'
        # compare with what is returned for a user that may see everything
        dev_items = collegeMeeting.get_items(
            ordered=True, additional_catalog_query={'getProposingGroup': self.developers_uid})
        dev_refs = [item.getItemReference() for item in dev_items]
        self.assertEqual(
            dev_refs,
            ['{0}/1/3'.format(year), '{0}/1/4'.format(year),
             '{0}/1/C/4'.format(year), '{0}/1/C/5'.format(year), '{0}/1/C/6'.format(year),
             '{0}/1/C/7'.format(year), '{0}/1/C/8'.format(year), '{0}/1/C/9'.format(year),
             '{0}/1/C/10'.format(year), '{0}/1/8'.format(year),  # OJ Council
             '-', '-', '-'])
        self.changeUser('pmCreator1')
        dev_items_for_creator = collegeMeeting.get_items(
            ordered=True, additional_catalog_query={'getProposingGroup': self.developers_uid})
        dev_refs_for_creator = [item.getItemReference() for item in dev_items_for_creator]
        self.assertEqual(dev_refs, dev_refs_for_creator)

    def test_ItemRefForActeCouncil(self):
        """Test the method rendering the item reference of items in a College meeting."""
        meeting = self.setupCouncilDemoData()
        self.changeUser('pmManager')
        items = meeting.get_items(ordered=True)
        year = meeting.date.year

        result = [item.getItemReference() for item in items]
        expected = ['{0}/1/1'.format(year),
             '{0}/1/2'.format(year),
             '{0}/1/U/1'.format(year),
             '{0}/1/3'.format(year),
             '{0}/1/S/1'.format(year),
             '{0}/1/S/2'.format(year),
             '{0}/1/S/3'.format(year),
             '{0}/1/S/4'.format(year),
             '{0}/1/S/5'.format(year),
             '{0}/1/S/6'.format(year),
             '{0}/1/S/7'.format(year),
             '{0}/1/S/8'.format(year),
             '{0}/1/4'.format(year),
             '{0}/1/5'.format(year),
             '{0}/1/6'.format(year),
             '{0}/1/7'.format(year),
             '{0}/1/8'.format(year),
             '{0}/1/9'.format(year),
             '{0}/1/10'.format(year),
             '{0}/1/U/2'.format(year),
             '{0}/1/U/3'.format(year),
             '{0}/1/U/4'.format(year),
             '{0}/1/11'.format(year),
             '{0}/1/12'.format(year),
             '{0}/1/13'.format(year),
             '{0}/1/14'.format(year),
             '{0}/1/15'.format(year),
             '{0}/1/16'.format(year),
             '{0}/1/17'.format(year),
             '{0}/1/18'.format(year),
             '{0}/1/U/5'.format(year),
             '{0}/1/U/6'.format(year)]
        self.assertEqual(result, expected)

        # now check with 'pmCreator1' that may only see items of 'developers'
        # compare with what is returned for a user that may see everything
        dev_items = meeting.get_items(
            ordered=True, additional_catalog_query={'getProposingGroup': self.developers_uid})
        dev_refs = [item.getItemReference() for item in dev_items]
        self.assertEqual(
            dev_refs,
            ['{0}/1/1'.format(year),
             '{0}/1/2'.format(year),
             '{0}/1/U/1'.format(year),
             '{0}/1/3'.format(year),
             '{0}/1/S/1'.format(year),
             '{0}/1/S/2'.format(year),
             '{0}/1/S/3'.format(year),
             '{0}/1/S/4'.format(year),
             '{0}/1/S/5'.format(year),
             '{0}/1/S/6'.format(year),
             '{0}/1/S/7'.format(year),
             '{0}/1/S/8'.format(year),
             '{0}/1/4'.format(year),
             '{0}/1/5'.format(year),
             '{0}/1/U/2'.format(year),
             '{0}/1/11'.format(year),
             '{0}/1/12'.format(year),
             '{0}/1/15'.format(year),
             '{0}/1/17'.format(year),
             '{0}/1/U/5'.format(year)])
        self.changeUser('pmCreator1')
        dev_items_for_creator = meeting.get_items(
            ordered=True,
            additional_catalog_query={'getProposingGroup': self.developers_uid})
        dev_refs_for_creator = [item.getItemReference() for item in dev_items_for_creator]
        self.assertEqual(dev_refs, dev_refs_for_creator)

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

    def test_ValidateCategoryIfCollegeItemToSendToCouncil(self):
        """Use of category 'indeterminee' on MeetingItemCollege is not allowed
           if item will be sent to Council."""
        self.setupCouncilConfig()
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        item.setOtherMeetingConfigsClonableTo(('meeting-config-council',))

        msg_not_allowed = translate(
            msgid='category_indeterminee_not_allowed',
            domain='PloneMeeting',
            context=self.request)

        msg_mandatory = translate(
            msgid='category_must_be_indeterminee',
            domain='PloneMeeting',
            context=self.request)

        # as item is to send to Council, category 'indeterminee' must be used
        self.failIf(item.validate_category(COUNCIL_DEFAULT_CATEGORY))
        self.assertEqual(item.validate_category('development'), msg_mandatory)

        # but can not be used for items not to send to Council
        item.setOtherMeetingConfigsClonableTo(())
        self.assertEqual(item.validate_category(COUNCIL_DEFAULT_CATEGORY), msg_not_allowed)
        self.failIf(item.validate_category('development'))

        # does not fail when used on MeetingItemCouncil
        self.setMeetingConfig(self.meetingConfig2.getId())
        # make sure the COUNCIL_DEFAULT_CATEGORY exists or it does not pass validation
        self.changeUser('siteadmin')
        self._createCategories()
        self.changeUser('pmManager')
        council_item = self.create('MeetingItem')
        self.assertEqual(council_item.portal_type, 'MeetingItemCouncil')
        self.failIf(council_item.validate_category(COUNCIL_DEFAULT_CATEGORY))

    def test_KeepPollTypeIfCollegeItemToSendToCouncil(self):
        """When item is sent to Council, keep the poll type."""
        cfg = self.meetingConfig
        cfg.setItemManualSentToOtherMCStates(('itemcreated', ))
        cfg2Id = self.meetingConfig2.getId()

        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        item.setPollType('secret_separated')
        item.setOtherMeetingConfigsClonableTo((cfg2Id,))
        councilItem = item.cloneToOtherMeetingConfig(cfg2Id)
        self.assertEqual(item.getPollType(), 'secret_separated')
        self.assertEqual(councilItem.getPollType(), 'secret_separated')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeetingItem, prefix='test_'))
    return suite
