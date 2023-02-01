# -*- coding: utf-8 -*-
#
# File: testWorkflows.py
#
# Copyright (c) 2019 by Imio.be
#

import datetime
from DateTime import DateTime
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.permissions import ModifyPortalContent
from Products.MeetingCharleroi.profiles.zcharleroi import import_data as charleroi_import_data
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.PloneMeeting.config import ADVICE_STATES_ENDED
from zope.i18n import translate


class testCustomWorkflows(MeetingCharleroiTestCase):
    """Tests the default workflows implemented in MeetingCharleroi."""

    def setUp(self):
        """ """
        super(testCustomWorkflows, self).setUp()
        cfg = self.meetingConfig
        cfg.setWorkflowAdaptations(charleroi_import_data.collegeMeeting.workflowAdaptations)
        cfg.at_post_edit_script()

    def test_FreezeMeeting(self):
        """
           When we freeze a meeting, every presented items will be frozen
           too and their state will be set to 'itemfrozen'.  When the meeting
           come back to 'created', every items will be corrected and set in the
           'presented' state
        """
        # First, define recurring items in the meeting config
        self.changeUser('pmManager')
        # create a meeting
        meeting = self.create('Meeting', date=DateTime('2007/12/11 09:00:00').asdatetime())
        # create 2 items and present it to the meeting
        item1 = self.create('MeetingItem', title='The first item')
        self.presentItem(item1)
        item2 = self.create('MeetingItem', title='The second item')
        self.presentItem(item2)
        wftool = self.portal.portal_workflow
        # every presented items are in the 'presented' state
        self.assertEqual('presented', wftool.getInfoFor(item1, 'review_state'))
        self.assertEqual('presented', wftool.getInfoFor(item2, 'review_state'))
        # every items must be in the 'itemfrozen' state if we freeze the meeting
        self.freezeMeeting(meeting)
        self.assertEqual('itemfrozen', wftool.getInfoFor(item1, 'review_state'))
        self.assertEqual('itemfrozen', wftool.getInfoFor(item2, 'review_state'))
        # when an item is 'itemfrozen' it will stay itemfrozen if nothing
        # is defined in the meetingConfig.onMeetingTransitionItemActionToExecute
        self.meetingConfig.setOnMeetingTransitionItemActionToExecute([])
        self.backToState(meeting, 'created')
        self.assertEqual('itemfrozen', wftool.getInfoFor(item1, 'review_state'))
        self.assertEqual('itemfrozen', wftool.getInfoFor(item2, 'review_state'))

    def test_CloseMeeting(self):
        """
           When we close a meeting, every items are set to accepted if they are still
           not decided...
        """
        # First, define recurring items in the meeting config
        self.changeUser('pmManager')
        # create a meeting (with 7 items)
        meetingDate = DateTime('2007/12/11 09:00:00').asdatetime()
        meeting = self.create('Meeting', date=meetingDate)
        item1 = self.create('MeetingItem')  # id=o2
        item1.setProposingGroup(self.vendors_uid)
        item1.setAssociatedGroups((self.developers_uid,))
        item2 = self.create('MeetingItem')  # id=o3
        item2.setProposingGroup(self.developers_uid)
        item3 = self.create('MeetingItem')  # id=o4
        item3.setProposingGroup(self.vendors_uid)
        item4 = self.create('MeetingItem')  # id=o5
        item4.setProposingGroup(self.developers_uid)
        item5 = self.create('MeetingItem')  # id=o7
        item5.setProposingGroup(self.vendors_uid)
        item6 = self.create('MeetingItem', title='The sixth item')
        item6.setProposingGroup(self.vendors_uid)
        item7 = self.create('MeetingItem')  # id=o8
        item7.setProposingGroup(self.vendors_uid)
        for item in (item1, item2, item3, item4, item5, item6, item7):
            self.presentItem(item)
        # we freeze the meeting
        self.freezeMeeting(meeting)
        # a MeetingManager can put the item back to presented
        self.backToState(item7, 'presented')
        # we decide the meeting
        # while deciding the meeting, every items that where presented are frozen
        self.decideMeeting(meeting)
        # change all items in all different state (except first who is in good state)
        self.backToState(item7, 'presented')
        self.do(item2, 'delay')
        self.do(item3, 'pre_accept')
        self.do(item4, 'accept_but_modify')
        self.do(item5, 'refuse')
        self.do(item6, 'accept')
        # we close the meeting
        self.do(meeting, 'close')
        # every items must be in the 'decided' state if we close the meeting
        wftool = self.portal.portal_workflow
        # itemfrozen change into accepted
        self.assertEqual('accepted', wftool.getInfoFor(item1, 'review_state'))
        # delayed rest delayed (it's already a 'decide' state)
        self.assertEqual('delayed', wftool.getInfoFor(item2, 'review_state'))
        # pre_accepted change into accepted
        self.assertEqual('accepted', wftool.getInfoFor(item3, 'review_state'))
        # accepted_but_modified rest accepted_but_modified (it's already a 'decide' state)
        self.assertEqual('accepted_but_modified', wftool.getInfoFor(item4, 'review_state'))
        # refused stays refused (it's already a 'decided' state)
        self.assertEqual('refused', wftool.getInfoFor(item5, 'review_state'))
        # accepted stays accepted (it's already a 'decided' state)
        self.assertEqual('accepted', wftool.getInfoFor(item6, 'review_state'))
        # presented change into accepted
        self.assertEqual('accepted', wftool.getInfoFor(item7, 'review_state'))

    def test_CollegeProcessWithNormalAdvices(self):
        '''How does the process behave when some 'normal' advices,
           aka no 'finances' advice is aksed.'''
        # normal advices can be given when item in state 'itemcreated_waiting_advices',
        cfg = self.meetingConfig
        cfg.setUsedAdviceTypes(('asked_again', ) + cfg.getUsedAdviceTypes())
        # while an advice is given, adviser still keep access to item
        cfg.setKeepAccessToItemWhenAdvice('is_given')
        cfg.setItemAdviceStates(('itemcreated_waiting_advices',
                                 'proposed_waiting_advices',))
        cfg.setItemAdviceEditStates = (('itemcreated_waiting_advices',
                                        'proposed_waiting_advices', ))
        # not necessary as keepAccessToItemWhenAdviceIsGiven is True
        cfg.setItemAdviceViewStates = (())

        self.changeUser('pmCreator1')
        item = self.create('MeetingItem', title='The first item')
        # if no advice to ask, pmCreator may only 'propose' the item
        self.assertEqual(self.transitions(item), ['propose', ])
        # the mayWait_advices_from_itemcreated wfCondition returns a 'No' instance
        advice_required_to_ask_advices = translate('advice_required_to_ask_advices',
                                                   domain='PloneMeeting',
                                                   context=self.request)
        self.assertEqual(
            translate(
                item.wfConditions().mayWait_advices(item.query_state(),  "prevalidated_waiting_advices").msg,
                context=self.request),
            advice_required_to_ask_advices)
        # now ask 'vendors' advice
        item.setOptionalAdvisers((self.vendors_uid, ))
        item.at_post_edit_script()
        self.assertEqual(self.transitions(item),
                         ['propose', 'wait_advices_from_itemcreated'])
        # give advice
        self.do(item, 'wait_advices_from_itemcreated')
        # no editable
        self.assertFalse(self.hasPermission(ModifyPortalContent, item))

        # pmReviewer2 is adviser for vendors
        self.changeUser('pmReviewer2')
        createContentInContainer(item,
                                 'meetingadvice',
                                 **{'advice_group': self.vendors_uid,
                                    'advice_type': u'positive',
                                    'advice_comment': RichTextValue(u'My comment vendors')})
        # no more advice to give
        self.assertTrue(not item.hasAdvices(toGive=True))
        # item may be taken back by 'pmCreator1'
        self.assertFalse(self.transitions(item))
        self.changeUser('pmCreator1')
        self.do(item, 'backTo_itemcreated_from_waiting_advices')

        # advices may be asked when item is 'proposed'
        self.do(item, 'propose')
        self.assertFalse(self.transitions(item))
        self.changeUser('pmReviewer1')
        # no advice to ask
        self.assertEqual(self.transitions(item),
                         ['backToItemCreated', 'proposeToRefAdmin'])
        self.assertEqual(
            translate(
                item.wfConditions().mayWait_advices(item.query_state(),  "prevalidated_waiting_advices").msg,
                context=self.request),
            advice_required_to_ask_advices)
        item.setOptionalAdvisers((self.developers_uid, self.vendors_uid, ))
        item.at_post_edit_script()
        self.assertEqual(self.transitions(item),
                         ['backToItemCreated', 'proposeToRefAdmin', 'wait_advices_from_proposed'])
        self.do(item, 'wait_advices_from_proposed')
        self.changeUser('pmAdviser1')
        createContentInContainer(item,
                                 'meetingadvice',
                                 **{'advice_group': self.developers_uid,
                                    'advice_type': u'positive',
                                    'advice_comment': RichTextValue(u'My comment developers')})
        # no more advice to give
        self.assertTrue(not item.hasAdvices(toGive=True))
        # item may be taken back by 'pmReviewer1'
        self.assertFalse(self.transitions(item))
        self.changeUser('pmReviewer1')
        self.do(item, 'backTo_proposed_from_waiting_advices')

    def test_CollegeProcessWithFinancesAdvice(self):
        '''How does the process behave when the 'finances' advice is asked.'''
        cfg = self.meetingConfig
        self.changeUser('siteadmin')
        self._configureFinancesAdvice(cfg)

        self.changeUser('pmCreator1')
        item = self.create('MeetingItem', title='The first item')
        # ask finances advice
        item.setOptionalAdvisers(('{0}__rowid__unique_id_002'.format(finance_group_uid()), ))
        item.at_post_edit_script()
        # not askable for now
        self.assertEqual(self.transitions(item), ['propose', ])

        # only directors may ask finances advice, item must be 'prevalidated'
        self.assertEqual(self.transitions(item), ['propose'])
        self.do(item, 'propose')
        self.assertFalse(self.transitions(item))
        self.changeUser('pmServiceHead1')
        self.assertEqual(self.transitions(item), ['backToItemCreated', 'proposeToRefAdmin'])
        self.do(item, 'proposeToRefAdmin')
        self.assertFalse(self.transitions(item))
        self.changeUser('pmRefAdmin1')
        self.assertEqual(self.transitions(item), ['backToProposed', 'prevalidate'])
        self.do(item, 'prevalidate')
        self.assertFalse(self.transitions(item))
        self.changeUser('pmReviewer1')
        # may only validate if no finances advice or finances advice is given
        self.assertEqual(self.transitions(item),
                         ['backToItemCreatedFromPrevalidated',
                          'backToProposedFromPrevalidated',
                          'backToProposedToRefAdmin',
                          'wait_advices_from_prevalidated'])
        # remove fact that finances advice was asked
        item.setOptionalAdvisers(())
        self.assertEqual(self.transitions(item),
                         ['backToItemCreatedFromPrevalidated',
                          'backToProposedFromPrevalidated',
                          'backToProposedToRefAdmin',
                          'wait_advices_from_prevalidated'])
        item.setOptionalAdvisers(('{0}__rowid__unique_id_002'.format(finance_group_uid()), ))

        # ask finances advice
        self.do(item, 'wait_advices_from_prevalidated')
        # when item is sent to finances, even the reviewer may not change it's state
        self.assertFalse(self.transitions(item))
        # item may be returned to RefAdmin if completeness not evaluated/incomplete
        self.changeUser('pmFinController')
        self.assertEqual(item.getCompleteness(), 'completeness_not_yet_evaluated')
        self.assertEqual(self.transitions(item), ['backTo_proposed_to_refadmin_from_waiting_advices'])
        changeCompleteness = item.restrictedTraverse('@@change-item-completeness')
        self.request.set('new_completeness_value', 'completeness_incomplete')
        self.request.form['form.submitted'] = True
        changeCompleteness()
        self.assertEqual(self.transitions(item), ['backTo_proposed_to_refadmin_from_waiting_advices'])
        # once 'complete' item may not be returned to refAdmin anymore
        self.request.set('new_completeness_value', 'completeness_complete')
        changeCompleteness()
        self.assertEqual(self.transitions(item), [])

        # give advice positive with remarks
        # finances advice WF is tested in test_CollegeFinancesAdviceWF
        self.changeUser('pmFinController')
        advice = createContentInContainer(
            item,
            'meetingadvicefinances',
            **{'advice_group': finance_group_uid(),
               'advice_type': u'negative_finance',
               'advice_comment': RichTextValue(u'My comment finances'),
               'advice_category': u'acquisitions'})
        # MeetingManager may not change item state when sent to finance, but Manager may
        self.do(advice, 'proposeToFinancialEditor')
        self.changeUser('pmManager')
        self.assertFalse(self.transitions(item))
        self.changeUser('siteadmin')
        self.assertEqual(self.transitions(item), ['backTo_prevalidated_from_waiting_advices'])

        self.changeUser('pmFinEditor')
        self.do(advice, 'proposeToFinancialReviewer')
        self.changeUser('pmManager')
        self.assertFalse(self.transitions(item))
        self.changeUser('siteadmin')
        self.assertEqual(self.transitions(item), ['backTo_prevalidated_from_waiting_advices'])

        self.changeUser('pmFinReviewer')
        self.do(advice, 'proposeToFinancialManager')
        self.changeUser('pmManager')
        self.assertFalse(self.transitions(item))
        self.changeUser('siteadmin')
        self.assertEqual(self.transitions(item), ['backTo_prevalidated_from_waiting_advices'])

        self.changeUser('pmFinManager')
        self.do(advice, 'signFinancialAdvice')

        # item was sent back to administrative referent
        self.assertEqual(item.query_state(), 'proposed_to_refadmin')
        # now if it goes to director, director is able to validate the item
        self.changeUser('pmRefAdmin1')
        self.do(item, 'prevalidate')
        self.changeUser('pmReviewer1')
        # now item may be validated but finances advice may not be asked
        # anymore as it was already given
        self.assertEqual(self.transitions(item),
                         ['backToItemCreatedFromPrevalidated',
                          'backToProposedFromPrevalidated',
                          'backToProposedToRefAdmin',
                          'validate'])
        # if finances advice is 'asked_again', it is giveable again
        changeView = advice.restrictedTraverse('@@change-advice-asked-again')
        changeView()
        self.assertEqual(advice.advice_type, 'asked_again')
        self.assertEqual(self.transitions(item),
                         ['backToItemCreatedFromPrevalidated',
                          'backToProposedFromPrevalidated',
                          'backToProposedToRefAdmin',
                          'wait_advices_from_prevalidated'])

    def test_CollegeFinancesAdviceWF(self):
        '''Test the finances advice workflow.'''
        cfg = self.meetingConfig
        self.changeUser('siteadmin')
        self._configureFinancesAdvice(cfg)
        # put users in finances group
        self._setupFinancesGroup()
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem', title='The first item')
        # ask finances advice
        item.setOptionalAdvisers(('{0}__rowid__unique_id_002'.format(finance_group_uid()), ))
        self.proposeItem(item)
        self.changeUser('pmReviewer1')
        self.do(item, 'wait_advices_from_prevalidated')

        # now act as the finances users
        # advice may be added/edit when item is considered 'complete'
        self.changeUser('pmFinController')
        self.assertEqual(self.transitions(item),
                         ['backTo_proposed_to_refadmin_from_waiting_advices'])
        toAdd, toEdit = item.getAdvicesGroupsInfosForUser()
        self.assertFalse(toAdd or toEdit)

        # set item as "incomplete" using itemcompleteness view
        # this way, it checks that current user may actually evaluate completeness
        # and item is updated (at_post_edit_script is called)
        self.assertEqual(item.getCompleteness(), 'completeness_not_yet_evaluated')
        changeCompleteness = item.restrictedTraverse('@@change-item-completeness')
        self.request.set('new_completeness_value', 'completeness_incomplete')
        self.request.form['form.submitted'] = True
        changeCompleteness()
        self.assertEqual(item.getCompleteness(), 'completeness_incomplete')
        # can be sent back even if considered incomplete
        self.assertEqual(self.transitions(item),
                         ['backTo_proposed_to_refadmin_from_waiting_advices'])
        toAdd, toEdit = item.getAdvicesGroupsInfosForUser()
        self.assertFalse(toAdd or toEdit)
        # back to refadmin
        self.do(item, 'backTo_proposed_to_refadmin_from_waiting_advices')

        # now do item complete
        self.changeUser('pmRefAdmin1')
        self.do(item, 'prevalidate')
        self.changeUser('pmReviewer1')
        self.do(item, 'wait_advices_from_prevalidated')
        self.changeUser('pmFinController')
        # delay is not started
        self.assertIsNone(item.adviceIndex[finance_group_uid()]['delay_started_on'])
        self.assertEqual(item.getCompleteness(), 'completeness_evaluation_asked_again')
        self.request.set('new_completeness_value', 'completeness_complete')
        changeCompleteness()
        self.assertEqual(item.getCompleteness(), 'completeness_complete')
        self.assertTrue(item.adviceIndex[finance_group_uid()]['delay_started_on'])
        # advice may be added
        toAdd, toEdit = item.getAdvicesGroupsInfosForUser()
        self.assertEqual(toAdd, [finance_group_uid(),])
        self.assertFalse(toEdit)
        # add advice
        advice = createContentInContainer(
            item,
            'meetingadvicefinances',
            **{'advice_group': finance_group_uid(),
               'advice_type': u'negative_finance',
               'advice_comment': RichTextValue(u'My comment finances'),
               'advice_category': u'acquisitions'})

        # a meetingadvicefinances will be automatically hidden during redaction
        self.assertFalse(cfg.getDefaultAdviceHiddenDuringRedaction())
        self.assertTrue(advice.advice_hide_during_redaction)
        # editable
        self.assertTrue(item.adapted()._adviceIsEditableByCurrentUser(finance_group_uid()))

        # send advice to finances editor
        self.assertEqual(self.transitions(advice), ['proposeToFinancialEditor'])
        self.do(advice, 'proposeToFinancialEditor')
        # send advice to finances reviewer
        self.changeUser('pmFinEditor')
        # editable
        self.assertTrue(item.adapted()._adviceIsEditableByCurrentUser(finance_group_uid()))
        self.assertEqual(self.transitions(advice),
                         ['backToProposedToFinancialController',
                          'proposeToFinancialReviewer'])
        self.do(advice, 'proposeToFinancialReviewer')
        # send advice to finances Manager
        self.changeUser('pmFinReviewer')
        # editable
        self.assertTrue(item.adapted()._adviceIsEditableByCurrentUser(finance_group_uid()))
        self.assertEqual(self.transitions(advice),
                         ['backToProposedToFinancialController',
                          'backToProposedToFinancialEditor',
                          'proposeToFinancialManager'])
        self.do(advice, 'proposeToFinancialManager')
        # sign the advice
        self.changeUser('pmFinManager')
        # editable
        self.assertTrue(item.adapted()._adviceIsEditableByCurrentUser(finance_group_uid()))
        self.assertEqual(self.transitions(advice),
                         ['backToProposedToFinancialController',
                          'backToProposedToFinancialReviewer',
                          'signFinancialAdvice'])

        # sign the advice, as it is 'negative_finance', aka not 'positive_finances'
        # it will be automatically sent back to the refadmin
        self.do(advice, 'signFinancialAdvice')
        self.assertEqual(item.query_state(), 'proposed_to_refadmin')
        # advice was automatically shown
        self.assertFalse(advice.advice_hide_during_redaction)

        # sign the advice as 'positive_finance' it will be automatically 'validated'
        self.changeUser('pmReviewer1')
        self.do(item, 'prevalidate')
        # as advice was already given, user needs to ask advice again
        self.assertFalse('wait_advices_from_prevalidated' in self.transitions(item))
        changeView = advice.restrictedTraverse('@@change-advice-asked-again')
        changeView()
        self.assertEqual(advice.advice_type, 'asked_again')
        self.do(item, 'wait_advices_from_prevalidated')
        self.changeUser('pmFinController')
        # advice was automatically hidden
        self.assertTrue(advice.advice_hide_during_redaction)
        # delay is not started
        self.assertIsNone(item.adviceIndex[finance_group_uid()]['delay_started_on'])
        self.assertEqual(item.getCompleteness(), 'completeness_evaluation_asked_again')
        self.request.set('new_completeness_value', 'completeness_complete')
        changeCompleteness()
        self.assertTrue(item.adviceIndex[finance_group_uid()]['delay_started_on'])
        self.do(advice, 'proposeToFinancialEditor')
        self.changeUser('pmFinEditor')
        self.do(advice, 'proposeToFinancialReviewer')
        self.changeUser('pmFinReviewer')
        # advice may not be sent to financial manager if it is still asked_again
        # change advice_type to 'positive_finance'
        self.assertFalse('proposeToFinancialManager' in self.transitions(advice))
        advice.advice_type = u'positive_finance'
        self.assertTrue('proposeToFinancialManager' in self.transitions(advice))
        self.do(advice, 'proposeToFinancialManager')
        self.changeUser('pmFinManager')
        self.do(advice, 'signFinancialAdvice')
        self.assertEqual(item.query_state(), 'validated')
        # advice was automatically shown
        self.assertFalse(advice.advice_hide_during_redaction)
        # advice is no more editable/deletable by finances
        self.assertFalse(self.hasPermission(ModifyPortalContent, advice))
        self.assertFalse(self.hasPermission(DeleteObjects, advice))

    def test_FinanceAdviceFoundInUpdateDelayAwareAdvices(self):
        """Check that every states of finance advice WF will be managed
           by @@update-delay-aware-advices."""
        '''Test the finances advice workflow.'''
        cfg = self.meetingConfig
        self.changeUser('siteadmin')
        self._configureFinancesAdvice(cfg)
        # put users in finances group
        self._setupFinancesGroup()
        update_advices_view = self.portal.restrictedTraverse('@@update-delay-aware-advices')
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem', title='The first item')
        # ask finances advice
        item.setOptionalAdvisers(('{0}__rowid__unique_id_002'.format(finance_group_uid()), ))
        self.proposeItem(item)
        self.changeUser('pmReviewer1')
        self.do(item, 'wait_advices_from_prevalidated')

        # now act as the finances users
        self.changeUser('pmFinController')
        # set completeness
        item.setCompleteness('completeness_complete')
        item.at_post_edit_script()
        # add advice
        advice = createContentInContainer(
            item,
            'meetingadvicefinances',
            **{'advice_group': finance_group_uid(),
               'advice_type': u'negative_finance',
               'advice_comment': RichTextValue(u'My comment finances'),
               'advice_category': u'acquisitions'})

        query = update_advices_view._computeQuery()
        catalog = api.portal.get_tool('portal_catalog')
        self.assertTrue(item.UID() in [brain.UID for brain in catalog(**query)])

        # send advice to finances editor
        self.do(advice, 'proposeToFinancialEditor')
        self.assertTrue(item.UID() in [brain.UID for brain in catalog(**query)])
        # send advice to finances reviewer
        self.changeUser('pmFinEditor')
        self.do(advice, 'proposeToFinancialReviewer')
        self.assertTrue(item.UID() in [brain.UID for brain in catalog(**query)])
        # send advice to finances Manager
        self.changeUser('pmFinReviewer')
        self.do(advice, 'proposeToFinancialManager')
        self.assertTrue(item.UID() in [brain.UID for brain in catalog(**query)])
        # sign the advice
        self.changeUser('pmFinManager')
        self.do(advice, 'signFinancialAdvice')
        # no more found now that advice is signed, at has been moved to 'advice_given'
        self.assertTrue(advice.query_state() in ADVICE_STATES_ENDED)
        self.assertFalse(item.UID() in [brain.UID for brain in catalog(**query)])

    def test_CollegePostPoneNextMeetingWithGivenAdvices(self):
        '''Check that postpone_next_meeting will work, especially because if finances advice
           is asked, it must be mandatorily given for the item to be validated.'''
        cfg = self.meetingConfig
        self.changeUser('siteadmin')
        self._configureFinancesAdvice(cfg)

        self.changeUser('pmCreator1')
        item = self.create('MeetingItem', title='The first item')
        # ask finances advice
        item.setOptionalAdvisers(('{0}__rowid__unique_id_002'.format(finance_group_uid()), ))
        item.at_post_edit_script()
        self.proposeItem(item)

        # finances advice
        self.changeUser('pmReviewer1')
        self.do(item, 'wait_advices_from_prevalidated')
        self.changeUser('pmFinController')
        item.setCompleteness('completeness_complete')
        item._update_after_edit()
        # give advice positive with remarks
        # finances advice WF is tested in test_CollegeFinancesAdviceWF
        advice = createContentInContainer(
            item,
            'meetingadvicefinances',
            **{'advice_group': finance_group_uid(),
               'advice_type': u'positive_finance',
               'advice_comment': RichTextValue(u'My comment finances'),
               'advice_category': u'acquisitions'})
        self.do(advice, 'proposeToFinancialEditor')
        self.changeUser('pmFinEditor')
        self.do(advice, 'proposeToFinancialReviewer')
        self.changeUser('pmFinReviewer')
        self.do(advice, 'proposeToFinancialManager')
        self.changeUser('pmFinManager')
        self.do(advice, 'signFinancialAdvice')

        # item was automatically validated, present it into a meeting
        self.changeUser('pmManager')
        meeting = self.create('Meeting', date=DateTime('2016/12/11').asdatetime())
        self.presentItem(item)
        self.decideMeeting(meeting)
        self.do(item, 'postpone_next_meeting')
        # item was postponed, cloned item is validated and advices are inherited
        self.assertEqual(item.query_state(), 'postponed_next_meeting')
        cloneItem = item.get_successors()[0]
        for adviceInfo in cloneItem.adviceIndex.values():
            self.assertTrue(adviceInfo['inherited'])

    def test_ItemWithTimedOutAdviceIsAutomaticallySentBackToRefAdmin(self):
        '''When an item is 'prevalidated_waiting_advices', if delay is exceeded
           the 'backTo_proposed_to_refadmin_from_waiting_advices' is automatically
           triggered.
           If advice was already given but still not signed, 'advice_hide_during_redaction'
           is set to True so advice is considered 'not_given' as if it was never added.'''
        cfg = self.meetingConfig
        self.changeUser('siteadmin')
        self._configureFinancesAdvice(cfg)

        # first case, delay exceeded and advice was never given, the item is sent back to refadmin
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem', title='The first item')
        # ask finances advice
        item.setOptionalAdvisers(('{0}__rowid__unique_id_002'.format(finance_group_uid()), ))
        item.at_post_edit_script()
        self.proposeItem(item)
        # finances advice
        self.changeUser('pmReviewer1')
        self.do(item, 'wait_advices_from_prevalidated')
        self.changeUser('pmFinController')
        item.setCompleteness('completeness_complete')
        item.update_local_roles()

        # now does advice timed out
        item.adviceIndex[finance_group_uid()]['delay_started_on'] = datetime.datetime(2014, 1, 1)
        item.update_local_roles()
        # advice is timed out
        self.assertEqual(item.adviceIndex[finance_group_uid()]['delay_infos']['delay_status'],
                         'no_more_giveable')
        # item has been automatically sent back to refadmin
        self.assertEqual(item.query_state(), 'proposed_to_refadmin')
        # advice delay is kept
        self.assertEqual(item.adviceIndex[finance_group_uid()]['delay_started_on'],
                         datetime.datetime(2014, 1, 1))

        # second case, delay exceeded and advice exists but not signed
        # 'advice_hide_during_redaction' is set to True on the advice
        # and item is sent back to refadmin
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem', title='The second item')
        # ask finances advice
        item.setOptionalAdvisers(('{0}__rowid__unique_id_002'.format(finance_group_uid()), ))
        item.at_post_edit_script()
        self.proposeItem(item)
        # finances advice
        self.changeUser('pmReviewer1')
        self.do(item, 'wait_advices_from_prevalidated')
        self.changeUser('pmFinController')
        item.setCompleteness('completeness_complete')
        item._update_after_edit()
        # give advice positive with remarks
        advice = createContentInContainer(
            item,
            'meetingadvicefinances',
            **{'advice_group': finance_group_uid(),
               'advice_type': u'positive_finance',
               'advice_comment': RichTextValue(u'My comment finances'),
               'advice_category': u'acquisitions'})
        self.do(advice, 'proposeToFinancialEditor')
        self.assertTrue(item.adviceIndex[finance_group_uid()]['hidden_during_redaction'])
        # now does advice timed out
        item.adviceIndex[finance_group_uid()]['delay_started_on'] = datetime.datetime(2014, 1, 1)
        item.update_local_roles()
        # advice is timed out
        self.assertEqual(item.adviceIndex[finance_group_uid()]['delay_infos']['delay_status'],
                         'no_more_giveable')
        # item has been automatically sent back to refadmin
        self.assertTrue(item.query_state() == 'proposed_to_refadmin')
        # advice is still 'hidden_during_redaction'
        self.assertTrue(item.adviceIndex[finance_group_uid()]['hidden_during_redaction'])
