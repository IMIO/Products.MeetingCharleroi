# -*- coding: utf-8 -*-
#
# File: events.py
#
# Copyright (c) 2016 by Imio.be
#
# GNU General Public License (GPL)
#

__author__ = """Gauthier BASTIEN <gauthier.bastien@imio.be>"""
__docformat__ = 'plaintext'

from plone import api
from Products.PloneMeeting.utils import sendMailIfRelevant
from Products.MeetingCommunes.config import FINANCE_STATE_TO_GROUPS_MAPPINGS
from Products.MeetingCharleroi.config import FINANCE_GROUP_ID


def onAdviceTransition(advice, event):
    '''Called whenever a transition has been fired on an advice.'''
    # pass if we are pasting items as advices are not kept
    if advice != event.object or advice.REQUEST.get('currentlyPastingItems', False):
        return

    # manage finance workflow, just consider relevant transitions
    # if it is not a finance wf transition, return
    if not advice.advice_group == FINANCE_GROUP_ID:
        return

    item = advice.getParentNode()
    itemState = item.queryState()
    adviserGroupId = '%s_advisers' % advice.advice_group

    # onAdviceTransition is called before onAdviceAdded...
    # so the advice_row_id is still not set wich is very bad because
    # when we updateAdvices, it does not find the advice_row_id and adviceIndex is wrong
    # so we call it here...
    if not advice.advice_row_id:
        advice._updateAdviceRowId()

    wfTool = api.portal.get_tool('portal_workflow')
    oldStateId = event.old_state.id
    newStateId = event.new_state.id

    # initial_state or going back from 'advice_given', we set automatically
    # advice_hide_during_redaction to True
    if not event.transition or \
       newStateId == 'proposed_to_financial_controller' and oldStateId == 'advice_given':
        advice.advice_hide_during_redaction = True

    if newStateId == 'financial_advice_signed':
        # final state of the wf, make sure advice is no more hidden during redaction
        advice.advice_hide_during_redaction = False
        # if item was still in state 'prevalidated_waiting_advices',
        # it is automatically validated if advice is 'positive_finance'
        # otherwise it is sent back to the refadmin
        if itemState == 'prevalidated_waiting_advices':
            if advice.advice_type == 'positive_finance':
                item.REQUEST.set('mayValidate', True)
                wfTool.doActionFor(item,
                                   'backTo_validated_from_waiting_advices',
                                   comment='item_wf_changed_finance_advice_positive')
                item.REQUEST.set('mayValidate', False)
            else:
                item.REQUEST.set('maybackTo_proposed_to_refadmin_from_waiting_advices', True)
                wfTool.doActionFor(item,
                                   'backTo_proposed_to_refadmin_from_waiting_advices',
                                   comment='item_wf_changed_finance_advice_not_positive')
                item.REQUEST.set('maybackTo_proposed_to_refadmin_from_waiting_advices', False)
                sendMailIfRelevant(item, 'sentBackToRefAdminWhileSigningNotPositiveFinancesAdvice',
                                   'MeetingReviewer', isRole=True)
        else:
            # we need to _updateAdvices so change to
            # 'advice_hide_during_redaction' is taken into account
            item.updateLocalRoles()

    # in some corner case, we could be here and we are actually already updating advices,
    # this is the case if we validate an item and it triggers the fact that advice delay is exceeded
    # this should never be the case as advice delay should have been updated during nightly cron...
    # but if we are in a '_updateAdvices', do not _updateAdvices again...
    if not newStateId in FINANCE_STATE_TO_GROUPS_MAPPINGS:
        if not item.REQUEST.get('currentlyUpdatingAdvice', False):
            item.updateLocalRoles()
        return

    # give 'Reader' role to every members of the _advisers and
    # give 'MeetingFinanceEditor' role to the relevant finance sub-group depending on new advice state
    # we use a specific 'MeetingFinanceEditor' role because the 'Editor' role is given to entire
    # _advisers group by default in PloneMeeting and it is used for non finance advices
    advice.manage_delLocalRoles((adviserGroupId, ))
    advice.manage_addLocalRoles(adviserGroupId, ('Reader', ))
    advice.manage_addLocalRoles('%s_%s' % (advice.advice_group, FINANCE_STATE_TO_GROUPS_MAPPINGS[newStateId]),
                                ('MeetingFinanceEditor', ))
    # finally remove 'MeetingFinanceEditor' given in previous state except if it is initial_state
    if oldStateId in FINANCE_STATE_TO_GROUPS_MAPPINGS and event.transition:
        localRoledGroupId = '%s_%s' % (advice.advice_group,
                                       FINANCE_STATE_TO_GROUPS_MAPPINGS[oldStateId])
        advice.manage_delLocalRoles((localRoledGroupId, ))

    # need to updateLocalRoles, and especially _updateAdvices to finish work :
    # timed_out advice is no more giveable
    item.updateLocalRoles()


def onAdvicesUpdated(item, event):
    '''
      When advices have been updated, we need to check that finance advice marked as 'advice_editable' = True
      are really editable, this could not be the case if the advice is signed.
      In a second step, if item is 'backToProposedToInternalReviewer', we need to reinitialize finance advice delay.
    '''
    for groupId, adviceInfo in item.adviceIndex.items():
        # special behaviour for finances advice
        if not groupId == FINANCE_GROUP_ID:
            continue

        # double check if it is really editable...
        # to be editable, the advice has to be in an editable wf state
        if adviceInfo['advice_editable']:
            advice = getattr(item, adviceInfo['advice_id'])
            if not advice.queryState() in FINANCE_STATE_TO_GROUPS_MAPPINGS:
                # advice is no more editable, adapt adviceIndex
                item.adviceIndex[groupId]['advice_editable'] = False

        # the advice delay is really started when item completeness is 'complete' or
        # 'evaluation_not_required', until then, we do not let the delay start
        if not item.getCompleteness() in ('completeness_complete',
                                          'completeness_evaluation_not_required'):
            adviceInfo['delay_started_on'] = None
            adviceInfo['advice_addable'] = False
            adviceInfo['advice_editable'] = False
            adviceInfo['delay_infos'] = item.getDelayInfosForAdvice(groupId)
