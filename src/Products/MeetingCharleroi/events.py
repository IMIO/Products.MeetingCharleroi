# -*- coding: utf-8 -*-
#
# File: events.py
#
# Copyright (c) 2016 by Imio.be
#
# GNU General Public License (GPL)
#

from datetime import datetime
from imio.actionspanel import ActionsPanelMessageFactory as _AP
from plone import api
from Products.PloneMeeting.utils import sendMailIfRelevant
from Products.MeetingCharleroi.config import COUNCIL_DEFAULT_CATEGORY
from Products.MeetingCharleroi.config import COUNCIL_DEFAULT_CLASSIFIER
from Products.MeetingCharleroi.utils import finance_group_uid


def onAdviceAfterTransition(advice, event):
    '''Called whenever a transition has been fired on an advice.'''

    if advice != event.object:
        return

    # pass if we are pasting items as advices are not kept
    if advice.REQUEST.get('currentlyPastingItems', False):
        return

    # manage finance workflow, just consider relevant transitions
    # if it is not a finance wf transition, return
    if advice.advice_group != finance_group_uid():
        return

    item = advice.getParentNode()
    itemState = item.query_state()

    oldStateId = event.old_state.id
    newStateId = event.new_state.id

    # initial_state or going back from 'advice_given', we set automatically
    # advice_hide_during_redaction to True
    if not event.transition or \
       newStateId == 'proposed_to_financial_controller' and oldStateId == 'advice_given':
        advice.advice_hide_during_redaction = True

    if newStateId == 'financial_advice_signed':
        plone_utils = api.portal.get_tool('plone_utils')
        # final state of the wf, make sure advice is no more hidden during redaction
        advice.advice_hide_during_redaction = False
        # if item was still in state 'prevalidated_waiting_advices',
        # it is automatically validated if advice is 'positive_finance'
        # otherwise it is sent back to the refadmin
        if itemState == 'prevalidated_waiting_advices':
            wfTool = api.portal.get_tool('portal_workflow')
            if advice.advice_type == 'positive_finance':
                item.REQUEST.set('mayValidate', True)
                wfTool.doActionFor(item,
                                   'backTo_validated_from_waiting_advices',
                                   comment='item_wf_changed_finance_advice_positive')
                item.REQUEST.set('mayValidate', False)
                msg = _AP('backTo_validated_from_waiting_advices_done_descr')
            else:
                item.REQUEST.set('maybackTo_proposed_to_refadmin_from_waiting_advices', True)
                wfTool.doActionFor(item,
                                   'backTo_proposed_to_refadmin_from_waiting_advices',
                                   comment='item_wf_changed_finance_advice_not_positive')
                item.REQUEST.set('maybackTo_proposed_to_refadmin_from_waiting_advices', False)
                sendMailIfRelevant(item, 'sentBackToRefAdminWhileSigningNotPositiveFinancesAdvice',
                                   'MeetingReviewer', isRole=True)
                msg = _AP('backTo_proposed_to_refadmin_from_waiting_advices_done_descr')
            plone_utils.addPortalMessage(msg)

    # in some corner case, we could be here and we are actually already updating advices,
    # this is the case if we validate an item and it triggers the fact that advice delay is exceeded
    # this should never be the case as advice delay should have been updated during nightly cron...
    # but if we are in a '_updateAdvices', do not _updateAdvices again...
    # also bypass if we are creating the advice as onAdviceAdded is called after onAdviceTransition
    if event.transition and not item.REQUEST.get('currentlyUpdatingAdvice', False):
        item.update_local_roles()
    return


def onAdvicesUpdated(item, event):
    '''
      If item is 'backToProposedToInternalReviewer', we need to reinitialize finances advice delay.
    '''
    for groupId, adviceInfo in item.adviceIndex.items():
        # special behaviour for finances advice
        if groupId != finance_group_uid():
            continue

        # when a finance advice is just timed out, we will send the item back to the refadmin
        if adviceInfo['delay_infos']['delay_status'] == 'timed_out' and \
           'delay_infos' in event.old_adviceIndex[groupId] and not \
           event.old_adviceIndex[groupId]['delay_infos']['delay_status'] == 'timed_out':
            if item.query_state() == 'prevalidated_waiting_advices':
                wfTool = api.portal.get_tool('portal_workflow')
                item.adviceIndex[groupId]['delay_stopped_on'] = datetime.now()
                item.REQUEST.set('maybackTo_proposed_to_refadmin_from_waiting_advices', True)
                wfTool.doActionFor(item,
                                   'backTo_proposed_to_refadmin_from_waiting_advices',
                                   comment='item_wf_changed_finance_advice_timed_out')
                item.REQUEST.set('maybackTo_proposed_to_refadmin_from_waiting_advices', False)


def onItemDuplicatedToOtherMC(originalItem, event):
    '''When an item is sent to the Council, we need to initialize
       category depending on privacy :
       - 'public' items will use category COUNCIL_DEFAULT_CATEGORY and will be presented to next meeting;
       - 'secret' items will stay in it's initial state.'''
    newItem = event.newItem

    # set a default classifier as it is mandatory to insert the item in the meeting
    if not newItem.getClassifier():
        newItem.setClassifier(COUNCIL_DEFAULT_CLASSIFIER)

    newItem.setPollType(originalItem.getPollType())

    # check if current state is 'validated' to avoid breaking tests
    if originalItem.portal_type == 'MeetingItemCollege' and \
       newItem.portal_type == 'MeetingItemCouncil' and \
       newItem.getPrivacy() == 'public' and \
       newItem.query_state() == 'validated':
        tool = api.portal.get_tool('portal_plonemeeting')
        destMeetingConfig = tool.getMeetingConfig(newItem)
        # if no mapping was defined for category, use the default
        # one, it is mandatory to insert the item in the meeting
        if not newItem.getCategory():
            newItem.setCategory(COUNCIL_DEFAULT_CATEGORY)
        meeting = originalItem._otherMCMeetingToBePresentedIn(destMeetingConfig)
        if meeting:
            # make sure we present in the right Council meeting
            # if we are on the meeting College view
            # this will be taken into account by getCurrentMeetingObject
            originalPublishedObject = newItem.REQUEST.get('PUBLISHED')
            newItem.REQUEST['PUBLISHED'] = meeting
            newItem.setPreferredMeeting(meeting.UID())
            wfTool = api.portal.get_tool('portal_workflow')
            wfTool.doActionFor(newItem, 'present')
            # set back originally PUBLISHED object
            newItem.REQUEST.set('PUBLISHED', originalPublishedObject)
