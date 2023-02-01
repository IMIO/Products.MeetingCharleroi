# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from DateTime import DateTime
from Products.CMFCore.permissions import View
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.PloneMeeting.tests.testWorkflows import testWorkflows as pmtw
from Products.PloneMeeting.utils import org_id_to_uid
from zope.annotation import IAnnotations


class testWorkflows(MeetingCharleroiTestCase, pmtw):
    """Tests the default workflows implemented in MeetingCharleroi."""

    def test_pm_CreateItem(self):
        '''Run the test_pm_CreateItem from PloneMeeting.'''
        # we do the test for the college config
        self.meetingConfig = getattr(self.tool, 'meeting-config-college')
        super(testWorkflows, self).test_pm_CreateItem()
        # we do the test for the council config
        self.meetingConfig = getattr(self.tool, 'meeting-config-council')
        super(testWorkflows, self).test_pm_CreateItem()

    def test_pm_RemoveObjects(self):
        '''Run the test_pm_RemoveObjects from PloneMeeting.'''
        # we do the test for the college config
        self.meetingConfig = getattr(self.tool, 'meeting-config-college')
        super(testWorkflows, self).test_pm_RemoveObjects()
        # we do the test for the council config
        self.meetingConfig = getattr(self.tool, 'meeting-config-council')
        super(testWorkflows, self).test_pm_RemoveObjects()

    def test_pm_WholeDecisionProcess(self):
        """
            This test covers the whole decision workflow. It begins with the
            creation of some items, and ends by closing a meeting.
            This call 2 sub tests for each process : college and council
        """
        self._testWholeDecisionProcessCollege()
        self._testWholeDecisionProcessCouncil()

    def _testWholeDecisionProcessCollege(self):
        '''This test covers the whole decision workflow. It begins with the
           creation of some items, and ends by closing a meeting.'''
        self.setupCollegeConfig()
        self._createRecurringItems()
        # pmCreator1 creates an item with 1 annex and proposes it
        self.changeUser('pmCreator1')
        gic2_uid = org_id_to_uid('groupincharge2')
        dev_group_in_charge = '{0}__groupincharge__{1}'.format(self.developers_uid, gic2_uid)
        item1 = self.create('MeetingItem', title='The first item',
                            proposingGroupWithGroupInCharge=dev_group_in_charge)
        self.addAnnex(item1)
        self.addAnnex(item1, relatedTo='item_decision')
        self.do(item1, 'propose')
        self.assertRaises(Unauthorized, self.addAnnex, item1)
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # pmManager creates a meeting
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date=DateTime('2007/12/11 09:00:00').asdatetime())
        self.addAnnex(item1, relatedTo='item_decision')
        # pmCreator2 creates and proposes an item
        self.changeUser('pmCreator2')
        gic1_uid = org_id_to_uid('groupincharge1')
        vendors_group_in_charge = '{0}__groupincharge__{1}'.format(self.vendors_uid, gic1_uid)
        item2 = self.create('MeetingItem', title='The second item',
                            preferredMeeting=meeting.UID(),
                            proposingGroupWithGroupInCharge=vendors_group_in_charge)
        self.do(item2, 'propose')
        # pmReviewer1 validates item1 and adds an annex to it
        self.changeUser('pmServiceHead1')
        self.addAnnex(item1, relatedTo='item_decision')
        self.do(item1, 'proposeToRefAdmin')
        self.changeUser('pmRefAdmin1')
        self.do(item1, 'prevalidate')
        self.changeUser('pmReviewer1')
        self.do(item1, 'validate')
        self.assertRaises(Unauthorized, self.addAnnex, item1, relatedTo='item_decision')
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # pmManager inserts item1 into the meeting and publishes it
        self.changeUser('pmManager')
        managerAnnex = self.addAnnex(item1)
        self.portal.restrictedTraverse('@@delete_givenuid')(managerAnnex.UID())
        self.do(item1, 'present')
        # Now reviewers can't add annexes anymore
        self.changeUser('pmReviewer1')
        self.assertRaises(Unauthorized, self.addAnnex, item2)
        # meeting is frozen
        self.changeUser('pmManager')
        self.do(meeting, 'freeze')
        # pmReviewer2 validates item2
        self.changeUser('pmReviewer2')
        self.do(item2, 'proposeToRefAdmin')
        self.do(item2, 'prevalidate')
        self.do(item2, 'validate')
        # pmManager inserts item2 into the meeting, as late item, and adds an
        # annex to it
        self.changeUser('pmManager')
        self.do(item2, 'present')
        self.addAnnex(item2)
        # So now we should have 5 items, 4 normal (3 recurrings + 1 normal) and one late
        self.failUnless(len(meeting.get_items()) == 5)
        self.failUnless(len(meeting.get_items(list_types=['late'])) == 1)
        self.changeUser('pmManager')
        item1.setDecision(self.decisionText)

        # pmManager adds a decision for item2, and decides both meeting and item
        self.changeUser('pmManager')
        item2.setDecision(self.decisionText)
        self.addAnnex(item2, relatedTo='item_decision')
        self.do(meeting, 'decide')
        self.do(item1, 'accept')

        # pmCreator2/pmReviewer2 are not able to see item1
        self.changeUser('pmCreator2')
        self.failIf(self.hasPermission(View, item1))
        self.changeUser('pmReviewer2')
        self.failIf(self.hasPermission(View, item1))

        # meeting may be closed or set back to frozen
        self.changeUser('pmManager')
        self.assertEqual(self.transitions(meeting), ['backToFrozen', 'close'])
        self.changeUser('pmManager')
        self.do(meeting, 'close')

    def _testWholeDecisionProcessCouncil(self):
        """
            This test covers the whole decision workflow.
            Items are created from College directly as 'validated'.
        """
        # meeting-config-college is tested in test_pm_WholeDecisionProcessCollege
        # we do the test for the council config
        self.setMeetingConfig('meeting-config-council')
        # items come from College or could be created by a MeetingManager directly 'validated'
        # apply WFAdaptation defined in zcharleroi.import_data
        cfg = self.meetingConfig
        self.setupCouncilConfig()
        self.changeUser('pmManager')
        gic2_uid = org_id_to_uid('groupincharge2')
        dev_group_in_charge = '{0}__groupincharge__{1}'.format(self.developers_uid, gic2_uid)
        item1 = self.create('MeetingItem', title='The first item',
                            proposingGroupWithGroupInCharge=dev_group_in_charge)
        self.addAnnex(item1)
        self.addAnnex(item1, relatedTo='item_decision')
        self.validateItem(item1)
        self.assertEqual(item1.query_state(), 'validated')
        meeting = self.create('Meeting', date=DateTime('2016/12/11 09:00:00').asdatetime())
        item2 = self.create('MeetingItem', title='The second item',
                            preferredMeeting=meeting.UID(),
                            proposingGroupWithGroupInCharge=dev_group_in_charge)
        self.presentItem(item1)
        item1.setDecision(self.decisionText)
        self.decideMeeting(meeting)
        self.assertEqual(meeting.query_state(), 'decided')
        item2.setDecision(self.decisionText)
        self.presentItem(item2)
        self.do(meeting, 'close')
        self.assertEqual(item1.query_state(), 'accepted')
        self.assertEqual(item2.query_state(), 'accepted')

    def test_pm_WorkflowPermissions(self):
        """
          Pass this test...
        """
        pass

    def test_pm_RecurringItems(self):
        """
            Tests the recurring items system.
        """
        # we do the test for the college config
        self.meetingConfig = getattr(self.tool, 'meeting-config-college')
        # super(testWorkflows, self).test_pm_RecurringItems() workflow is different
        self._checkRecurringItemsCollege()
        # we do the test for the council config
        # no recurring items defined...
        self.meetingConfig = getattr(self.tool, 'meeting-config-council')
        meeting = self.create('Meeting', date=DateTime('2007/12/11 09:00:00').asdatetime())
        self.assertEqual(len(meeting.get_items()), 0)

    def _checkRecurringItemsCollege(self):
        '''Tests the recurring items system.'''
        # First, define recurring items in the meeting config
        self.changeUser('admin')
        # 2 recurring items already exist in the college config, add one supplementary for _init_
        self.create('MeetingItemRecurring', title='Rec item 1',
                    proposingGroup=self.developers_uid,
                    meetingTransitionInsertingMe='_init_')
        # add 3 other recurring items that will be inserted at other moments in the WF
        # backToCreated is not in MeetingItem.meetingTransitionsAcceptingRecurringItems
        # so it will not be added...
        self.create('MeetingItemRecurring', title='Rec item 2',
                    proposingGroup=self.developers_uid,
                    meetingTransitionInsertingMe='backToCreated')
        self.create('MeetingItemRecurring', title='Rec item 3',
                    proposingGroup=self.developers_uid,
                    meetingTransitionInsertingMe='freeze')
        self.create('MeetingItemRecurring', title='Rec item 4',
                    proposingGroup=self.developers_uid,
                    meetingTransitionInsertingMe='decide')
        self.changeUser('pmManager')
        # create a meeting without supplementary items, only the recurring items
        meeting = self.create('Meeting', date=DateTime('2019/06/28').asdatetime())
        # The recurring items must have as owner the meeting creator
        for item in meeting.get_items():
            self.assertEqual(item.getOwner().getId(), 'pmManager')
        # The meeting must contain recurring items : 2 defined and one added here above
        self.failUnless(len(meeting.get_items()) == 3)
        self.failIf(meeting.get_items(list_types=['late']))
        # After freeze, the meeting must have one recurring item more
        self.freezeMeeting(meeting)
        self.failUnless(len(meeting.get_items()) == 4)
        self.failUnless(len(meeting.get_items(list_types=['late'])) == 1)
        # Back to created: rec item 2 is inserted again
        self.backToState(meeting, 'created')
        self.failUnless(len(meeting.get_items()) == 5)
        self.failUnless(len(meeting.get_items(list_types=['late'])) == 1)
        # Recurring items can be added twice...
        self.freezeMeeting(meeting)
        self.failUnless(len(meeting.get_items()) == 6)
        self.failUnless(len(meeting.get_items(list_types=['late'])) == 2)
        # Decide the meeting, a third late item is added
        self.decideMeeting(meeting)
        self.failUnless(len(meeting.get_items()) == 7)
        self.failUnless(len(meeting.get_items(list_types=['late'])) == 3)

    def test_pm_RemoveContainer(self):
        '''Run the test_pm_RemoveContainer from PloneMeeting.'''
        # we do the test for the college config
        self.meetingConfig = getattr(self.tool, 'meeting-config-college')
        super(testWorkflows, self).test_pm_RemoveContainer()
        # we do the test for the council config
        self.meetingConfig = getattr(self.tool, 'meeting-config-council')
        # clean memoize because we test for status messages
        annotations = IAnnotations(self.portal.REQUEST)
        if 'statusmessages' in annotations:
            annotations['statusmessages'] = ''
        super(testWorkflows, self).test_pm_RemoveContainer()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWorkflows, prefix='test_pm_'))
    return suite
