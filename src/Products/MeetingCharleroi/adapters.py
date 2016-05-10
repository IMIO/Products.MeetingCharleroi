# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Copyright (c) 2007 by PloneGov
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
# ------------------------------------------------------------------------------

from appy.gen import No
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from zope.interface import implements
from zope.i18n import translate

from plone import api

from Products.CMFCore.permissions import ReviewPortalContent
from Products.PloneMeeting.adapters import ItemPrettyLinkAdapter
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.interfaces import IMeetingConfigCustom
from Products.PloneMeeting.interfaces import IMeetingCustom
from Products.PloneMeeting.interfaces import IMeetingGroupCustom
from Products.PloneMeeting.interfaces import IMeetingItemCustom
from Products.PloneMeeting.interfaces import IToolPloneMeetingCustom
from Products.PloneMeeting.model import adaptations
from Products.PloneMeeting.model.adaptations import grantPermission
from Products.PloneMeeting.model.adaptations import WF_APPLIED
from Products.PloneMeeting.utils import checkPermission
from Products.PloneMeeting.utils import getLastEvent
from Products.MeetingCommunes.adapters import CustomMeeting
from Products.MeetingCommunes.adapters import CustomMeetingConfig
from Products.MeetingCommunes.adapters import CustomMeetingGroup
from Products.MeetingCommunes.adapters import CustomMeetingItem
from Products.MeetingCommunes.adapters import CustomToolPloneMeeting
from Products.MeetingCommunes.adapters import MeetingItemCollegeWorkflowActions
from Products.MeetingCommunes.adapters import MeetingItemCollegeWorkflowConditions
from Products.MeetingCommunes.adapters import MeetingCollegeWorkflowActions
from Products.MeetingCommunes.adapters import MeetingCollegeWorkflowConditions
from Products.MeetingCharleroi.interfaces import IMeetingCharleroiCollegeWorkflowActions
from Products.MeetingCharleroi.interfaces import IMeetingCharleroiCollegeWorkflowConditions
from Products.MeetingCharleroi.interfaces import IMeetingItemCharleroiCollegeWorkflowActions
from Products.MeetingCharleroi.interfaces import IMeetingItemCharleroiCollegeWorkflowConditions
from Products.MeetingCharleroi.interfaces import IMeetingCharleroiCouncilWorkflowActions
from Products.MeetingCharleroi.interfaces import IMeetingCharleroiCouncilWorkflowConditions
from Products.MeetingCharleroi.interfaces import IMeetingItemCharleroiCouncilWorkflowActions
from Products.MeetingCharleroi.interfaces import IMeetingItemCharleroiCouncilWorkflowConditions
from Products.MeetingCharleroi.config import FINANCE_ADVICE_LEGAL_TEXT_PRE
from Products.MeetingCharleroi.config import FINANCE_ADVICE_LEGAL_TEXT
from Products.MeetingCharleroi.config import FINANCE_ADVICE_LEGAL_TEXT_NOT_GIVEN
from Products.MeetingCharleroi.config import FINANCE_GIVEABLE_ADVICE_STATES
from Products.MeetingCharleroi.config import FINANCE_GROUP_ID

# disable most of wfAdaptations
customWfAdaptations = ('no_publication', 'no_global_observation',
                       'pre_validation', 'return_to_proposing_group',
                       'charleroi_add_refadmin', 'waiting_advices')
MeetingConfig.wfAdaptations = customWfAdaptations
originalPerformWorkflowAdaptations = adaptations.performWorkflowAdaptations

# states taken into account by the 'no_global_observation' wfAdaptation
from Products.PloneMeeting.model import adaptations
noGlobalObsStates = ('itempublished', 'itemfrozen', 'accepted', 'refused',
                     'delayed', 'accepted_but_modified', 'pre_accepted')
adaptations.noGlobalObsStates = noGlobalObsStates

adaptations.WF_NOT_CREATOR_EDITS_UNLESS_CLOSED = ('delayed', 'refused', 'accepted',
                                                  'pre_accepted', 'accepted_but_modified')

adaptations.WAITING_ADVICES_FROM_STATES = (
    {'from_states': ('itemcreated', ),
     'back_states': ('itemcreated', ),
     'perm_cloned_states': ('itemcreated',),
     'remove_modify_access': True},
    {'from_states': ('prevalidated', ),
     'back_states': ('proposed_to_refadmin', 'prevalidated', ),
     'perm_cloned_states': ('prevalidated',),
     'remove_modify_access': True},)

RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE = {'meetingitemcommunes_workflow': 'meetingitemcommunes_workflow.itemcreated'}
adaptations.RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE = RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE


class CustomCharleroiMeeting(CustomMeeting):
    '''Adapter that adapts a custom meeting implementing IMeeting to the
       interface IMeetingCustom.'''

    implements(IMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, meeting):
        self.context = meeting


class CustomCharleroiMeetingItem(CustomMeetingItem):
    '''Adapter that adapts a custom meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom.'''
    implements(IMeetingItemCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    def getLegalTextForFDAdvice(self, isMeeting=False):
        '''
        Helper method. Return legal text for each advice type.
        '''
        if not 'dirfin' in self.context.getAdviceDataFor(self.context):
            return ''

        advice = self.context.getAdviceDataFor(self.context, 'dirfin')()
        hidden = advice['hidden_during_redaction']
        statusWhenStopped = advice['delay_infos']['delay_status_when_stopped']
        adviceType = advice['type']
        comment = advice['comment']
        adviceGivenOnLocalized = advice['advice_given_on_localized']
        delayStartedOnLocalized = advice['delay_infos']['delay_started_on_localized']
        delayStatus = advice['delay_infos']['delay_status']
        outOfFinancialdptLocalized = advice['out_of_financial_dpt_localized']
        limitDateLocalized = advice['delay_infos']['limit_date_localized']

        if not isMeeting:
            res = FINANCE_ADVICE_LEGAL_TEXT_PRE.format(delayStartedOnLocalized)

        if not hidden and \
           adviceGivenOnLocalized and \
           (adviceType in (u'positive_finance', u'positive_with_remarks_finance', u'negative_finance')):
            if adviceType in (u'positive_finance', u'positive_with_remarks_finance'):
                adviceTypeFr = 'favorable'
            else:
                adviceTypeFr = 'défavorable'
            #if it's a meetingItem, return the legal bullshit.
            if not isMeeting:
                res = res + FINANCE_ADVICE_LEGAL_TEXT.format(
                    adviceTypeFr,
                    outOfFinancialdptLocalized
                )
            #if it's a meeting, returns only the type and date of the advice.
            else:
                res = "<p>Avis {0} du Directeur Financier du {1}</p>".format(
                    adviceTypeFr, outOfFinancialdptLocalized)

            if comment and adviceType == u'negative_finance':
                res = res + "<p>{0}</p>".format(comment)
        elif statusWhenStopped == 'stopped_timed_out' or delayStatus == 'timed_out':
            if not isMeeting:
                res = res + FINANCE_ADVICE_LEGAL_TEXT_NOT_GIVEN
            else:
                res = "<p>Avis du Directeur financier expiré le {0}</p>".format(limitDateLocalized)
        else:
            res = ''
        return res

    def getCustomAdviceMessageFor(self, advice):
        '''If we are on a finance advice that is still not giveable because
           the item is not 'complete', we display a clear message.'''
        item = self.getSelf()
        if advice['id'] == FINANCE_GROUP_ID and \
           advice['delay'] and \
           not advice['delay_started_on']:
            # item in state giveable but item not complete
            if item.queryState() in FINANCE_GIVEABLE_ADVICE_STATES:
                return {'displayDefaultComplementaryMessage': False,
                        'customAdviceMessage':
                        translate('finance_advice_not_giveable_because_item_not_complete',
                                  domain="PloneMeeting",
                                  context=item.REQUEST,
                                  default="Advice is still not giveable because item is not considered complete.")}
            elif getLastEvent(item, 'proposeToFinance') and \
                item.queryState() in ('itemcreated',
                                      'itemcreated_waiting_advices',
                                      'proposed_to_internal_reviewer',
                                      'proposed_to_internal_reviewer_waiting_advices',
                                      'proposed_to_director',):
                # advice was already given but item was returned back to the service
                return {'displayDefaultComplementaryMessage': False,
                        'customAdviceMessage': translate(
                            'finance_advice_suspended_because_item_sent_back_to_proposing_group',
                            domain="PloneMeeting",
                            context=item.REQUEST,
                            default="Advice is suspended because it was sent back to proposing group.")}
        return {'displayDefaultComplementaryMessage': True,
                'customAdviceMessage': None}

    def _adviceIsEditableByCurrentUser(self, groupId):
        '''Depending on advice WF state, it is only editable by relevant level.
           This is used by MeetingItem.getAdvicesGroupsInfosForUser.'''
        item = self.getSelf()
        if groupId == FINANCE_GROUP_ID:
            member = api.user.get_current()
            adviceObj = getattr(item, item.adviceIndex[groupId]['advice_id'])
            if not member.has_role('MeetingFinanceEditor', adviceObj):
                return False
        return True

    def _advicePortalTypeForAdviser(self, groupId):
        """Return the meetingadvice portal_type that will be added for given p_groupId.
           By default we always use meetingadvice but this makes it possible to have several
           portal_types for meetingadvice."""
        if groupId == FINANCE_GROUP_ID:
            return "meetingadvicefinances"
        else:
            return "meetingadvice"

    def _adviceTypesForAdviser(self, meeting_advice_portal_type):
        """Return the advice types (positive, negative, ...) for given p_meeting_advice_portal_type.
           By default we always use every MeetingConfig.usedAdviceTypes but this is useful
           when using several portal_types for meetingadvice and some may use particular advice types."""
        item = self.getSelf()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(item)
        if meeting_advice_portal_type == 'meetingadvice':
            return [t for t in cfg.getUsedAdviceTypes() if not t.endswith('_finance')]
        else:
            return [t for t in cfg.getUsedAdviceTypes() if t.endswith('_finance')]

    security.declarePublic('mayEvaluateCompleteness')

    def mayEvaluateCompleteness(self):
        '''Condition for editing 'completeness' field,
           being able to define if item is 'complete' or 'incomplete'.
           Completeness can be evaluated by the finance controller.'''
        # user must be a finance controller
        item = self.getSelf()
        if item.isDefinedInTool():
            return
        member = api.user.get_current()
        # bypass for Managers
        if member.has_role('Manager'):
            return True

        # a finance controller may evaluate if advice is actually asked
        # and may not change completeness if advice is currently given or has been given
        if not FINANCE_GROUP_ID in item.adviceIndex or \
           not '%s_financialcontrollers' % FINANCE_GROUP_ID in member.getGroups():
            return False

        # item must be still in a state where the advice can be given
        # and advice must still not have been given
        if not item.queryState() == 'prevalidated_waiting_advices':
            return False
        return True


class CustomCharleroiMeetingGroup(CustomMeetingGroup):
    '''Adapter that adapts a meeting group implementing IMeetingGroup to the
       interface IMeetingGroupCustom.'''

    implements(IMeetingGroupCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item


class CustomCharleroiMeetingConfig(CustomMeetingConfig):
    '''Adapter that adapts a custom meetingConfig implementing IMeetingConfig to the
       interface IMeetingConfigCustom.'''

    implements(IMeetingConfigCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item


class MeetingCharleroiCollegeWorkflowActions(MeetingCollegeWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCharleroiCollegeWorkflowActions'''

    implements(IMeetingCharleroiCollegeWorkflowActions)
    security = ClassSecurityInfo()


class MeetingCharleroiCollegeWorkflowConditions(MeetingCollegeWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCharleroiCollegeWorkflowConditions'''

    implements(IMeetingCharleroiCollegeWorkflowConditions)
    security = ClassSecurityInfo()


class MeetingItemCharleroiCollegeWorkflowActions(MeetingItemCollegeWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCharleroiCollegeWorkflowActions'''

    implements(IMeetingItemCharleroiCollegeWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doProposeToRefAdmin')

    def doProposeToRefAdmin(self, stateChange):
        pass

    def doProposeToFinance(self, stateChange):
        '''When an item is proposed to finance again, make sure the item
           completeness si no more in ('completeness_complete', 'completeness_evaluation_not_required')
           so advice is not addable/editable when item come back again to the finance.'''
        # if we found an event 'proposeToFinance' in workflow_history, it means that item is
        # proposed again to the finances and we need to ask completeness evaluation again
        # current transition 'proposeToFinance' is already in workflow_history...
        wfTool = api.portal.get_tool('portal_workflow')
        # take history but leave last event apart
        history = self.context.workflow_history[wfTool.getWorkflowsFor(self.context)[0].getId()][:-1]
        # if we find 'proposeToFinance' in previous actions, then item is proposed to finance again
        for event in history:
            if event['action'] == 'proposeToFinance':
                changeCompleteness = self.context.restrictedTraverse('@@change-item-completeness')
                comment = translate('completeness_asked_again_by_app',
                                    domain='PloneMeeting',
                                    context=self.context.REQUEST)
                # change completeness even if current user is not able to set it to
                # 'completeness_evaluation_asked_again', here it is the application that set
                # it automatically
                changeCompleteness._changeCompleteness('completeness_evaluation_asked_again',
                                                       bypassSecurityCheck=True,
                                                       comment=comment)
                break

    def _doWaitAdvices(self):
        '''When an item is proposed to finances again, make sure the item
           completeness si no more in ('completeness_complete', 'completeness_evaluation_not_required')
           so advice is not addable/editable when item come back again to the finance.'''
        # if we found an event 'wait_advices_from_proposed_to_refadmin' or 'wait_advices_from_prevalidated'
        # in workflow_history, it means that item is proposed again to the finances and we need to
        # ask completeness evaluation again current transition 'proposeToFinance' is already in workflow_history...
        wfTool = api.portal.get_tool('portal_workflow')
        # take history but leave last event apart
        history = self.context.workflow_history[wfTool.getWorkflowsFor(self.context)[0].getId()][:-1]
        # if we find 'proposeToFinance' in previous actions, then item is proposed to finance again
        for event in history:
            if event['action'] in ('wait_advices_from_proposed_to_refadmin',
                                   'wait_advices_from_prevalidated'):
                changeCompleteness = self.context.restrictedTraverse('@@change-item-completeness')
                comment = translate('completeness_asked_again_by_app',
                                    domain='PloneMeeting',
                                    context=self.context.REQUEST)
                # change completeness even if current user is not able to set it to
                # 'completeness_evaluation_asked_again', here it is the application that set
                # it automatically
                changeCompleteness._changeCompleteness('completeness_evaluation_asked_again',
                                                       bypassSecurityCheck=True,
                                                       comment=comment)
                break

    security.declarePrivate('doWait_advices_from_proposed_to_refadmin')

    def doWait_advices_from_proposed_to_refadmin(self, stateChange):
        """ """
        self._doWaitAdvices()

    security.declarePrivate('doWait_advices_from_prevalidated')

    def doWait_advices_from_prevalidated(self, stateChange):
        """ """
        self._doWaitAdvices()


class MeetingItemCharleroiCollegeWorkflowConditions(MeetingItemCollegeWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCharleroiCollegeWorkflowConditions'''

    implements(IMeetingItemCharleroiCollegeWorkflowConditions)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item  # Implements IMeetingItem

    security.declarePublic('mayProposeToRefAdmin')

    def mayProposeToRefAdmin(self):
        res = False
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    def _mayWaitAdvices(self):
        """May only be set to 'waiting_advices' if finances advice is asked."""
        if not FINANCE_GROUP_ID in self.context.adviceIndex:
            return No(translate('no_finances_advice_asked',
                                domain="PloneMeeting",
                                context=self.context.REQUEST,
                                default="The finances advice has not been selected on this item."))

        res = False
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayWait_advices_from_proposed_to_refadmin')

    def mayWait_advices_from_proposed_to_refadmin(self):
        """ """
        return self._mayWaitAdvices()

    security.declarePublic('mayWait_advices_from_prevalidated')

    def mayWait_advices_from_prevalidated(self):
        """ """
        return self._mayWaitAdvices()

    security.declarePublic('mayCorrect')

    def mayCorrect(self):
        '''If the item is not linked to a meeting, the user just need the
           'Review portal content' permission, if it is linked to a meeting, an item
           may still be corrected until the meeting is 'closed'.'''
        res = MeetingItemCollegeWorkflowConditions(self.context).mayCorrect()
        if not res:
            # if item is 'waiting_advices', finances adviser may send the item back
            if self.context.queryState() == 'waiting_advices':
                member = api.user.get_current()
                if '{0}_advisers'.format(FINANCE_GROUP_ID) in member.getGroups():
                    res = True
        return res


class MeetingCharleroiCouncilWorkflowActions(MeetingCharleroiCollegeWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCharleroiCouncilWorkflowActions'''

    implements(IMeetingCharleroiCouncilWorkflowActions)
    security = ClassSecurityInfo()


class MeetingCharleroiCouncilWorkflowConditions(MeetingCharleroiCollegeWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCharleroiCouncilWorkflowConditions'''

    implements(IMeetingCharleroiCouncilWorkflowConditions)
    security = ClassSecurityInfo()


class MeetingItemCharleroiCouncilWorkflowActions(MeetingItemCharleroiCollegeWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCharleroiCouncilWorkflowActions'''

    implements(IMeetingItemCharleroiCouncilWorkflowActions)
    security = ClassSecurityInfo()


class MeetingItemCharleroiCouncilWorkflowConditions(MeetingItemCharleroiCollegeWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCharleroiCouncilWorkflowConditions'''

    implements(IMeetingItemCharleroiCouncilWorkflowConditions)
    security = ClassSecurityInfo()

    security.declarePublic('mayProposeToRefAdmin')

    def mayProposeToRefAdmin(self):
        """
          Check that the user has the 'Review portal content'
        """
        res = False
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        return res


class CustomCharleroiToolPloneMeeting(CustomToolPloneMeeting):
    '''Adapter that adapts a tool implementing ToolPloneMeeting to the
       interface IToolPloneMeetingCustom'''

    implements(IToolPloneMeetingCustom)
    security = ClassSecurityInfo()

    def performCustomWFAdaptations(self,
                                   meetingConfig,
                                   wfAdaptation,
                                   logger,
                                   itemWorkflow,
                                   meetingWorkflow):
        '''This function applies workflow changes as specified by the
           p_meetingConfig.'''
        if wfAdaptation == 'no_publication':
            # we override the PloneMeeting's 'no_publication' wfAdaptation
            # First, update the meeting workflow
            wf = meetingWorkflow
            # Delete transitions 'publish' and 'backToPublished'
            for tr in ('publish', 'backToPublished'):
                if tr in wf.transitions:
                    wf.transitions.deleteTransitions([tr])
            # Update connections between states and transitions
            wf.states['frozen'].setProperties(
                title='frozen', description='',
                transitions=['backToCreated', 'decide'])
            wf.states['decided'].setProperties(
                title='decided', description='', transitions=['backToFrozen', 'close'])
            # Delete state 'published'
            if 'published' in wf.states:
                wf.states.deleteStates(['published'])
            # Then, update the item workflow.
            wf = itemWorkflow
            # Delete transitions 'itempublish' and 'backToItemPublished'
            for tr in ('itempublish', 'backToItemPublished'):
                if tr in wf.transitions:
                    wf.transitions.deleteTransitions([tr])
            # Update connections between states and transitions
            wf.states['itemfrozen'].setProperties(
                title='itemfrozen', description='',
                transitions=['accept', 'accept_but_modify', 'refuse', 'delay', 'pre_accept', 'backToPresented'])
            for decidedState in ['accepted', 'refused', 'delayed', 'accepted_but_modified']:
                wf.states[decidedState].setProperties(
                    title=decidedState, description='',
                    transitions=['backToItemFrozen', ])
            wf.states['pre_accepted'].setProperties(
                title='pre_accepted', description='',
                transitions=['accept', 'accept_but_modify', 'backToItemFrozen'])
            # Delete state 'published'
            if 'itempublished' in wf.states:
                wf.states.deleteStates(['itempublished'])
            logger.info(WF_APPLIED % ("no_publication", meetingConfig.getId()))
            return True
        if wfAdaptation == 'charleroi_add_refadmin':
            # add the 'proposed_to_refadmin' state after proposed state and before prevalidated state
            itemStates = itemWorkflow.states
            if 'proposed_to_refadmin' not in itemStates and 'prevalidated' in itemStates:
                #create proposed_to_refadmin state
                wf = itemWorkflow
                if 'proposed_to_refadmin' not in wf.states:
                    wf.states.addState('proposed_to_refadmin')
                for tr in ('proposeToRefAdmin', 'backToProposedToRefAdmin'):
                    if tr not in wf.transitions:
                        wf.transitions.addTransition(tr)
                transition = wf.transitions['proposeToRefAdmin']
                transition.setProperties(
                    title='proposeToRefAdmin',
                    new_state_id='proposed_to_refadmin', trigger_type=1, script_name='',
                    actbox_name='proposeToRefAdmin', actbox_url='',
                    actbox_icon='%(portal_url)s/proposeToRefAdmin.png', actbox_category='workflow',
                    props={'guard_expr': 'python:here.wfConditions().mayProposeToRefAdmin()'})
                transition = wf.transitions['backToProposedToRefAdmin']
                transition.setProperties(
                    title='backToProposedToRefAdmin',
                    new_state_id='proposed_to_refadmin', trigger_type=1, script_name='',
                    actbox_name='backToProposedToRefAdmin', actbox_url='',
                    actbox_icon='%(portal_url)s/backToProposedToRefAdmin.png', actbox_category='workflow',
                    props={'guard_expr': 'python:here.wfConditions().mayCorrect()'})
                # Update connections between states and transitions
                wf.states['proposed'].setProperties(
                    title='proposed', description='',
                    transitions=['backToItemCreated', 'proposeToRefAdmin'])
                wf.states['proposed_to_refadmin'].setProperties(
                    title='proposed_to_refadmin', description='',
                    transitions=['backToProposed', 'prevalidate'])
                wf.states['prevalidated'].setProperties(
                    title='prevalidated', description='',
                    transitions=['backToProposedToRefAdmin', 'validate'])
                # Initialize permission->roles mapping for new state "proposed_to_refadmin",
                # which is the same as state "proposed" in the previous setting.
                proposed = wf.states['proposed']
                proposed_to_refadmin = wf.states['proposed_to_refadmin']
                for permission, roles in proposed.permission_roles.iteritems():
                    proposed_to_refadmin.setPermission(permission, 0, roles)
                # Update permission->roles mappings for states 'proposed' and
                # 'proposed_to_refadmin': 'proposed' is 'mainly managed' by
                # 'MeetingServiceHead', while 'proposed_to_refadmin' is "mainly managed" by
                # 'MeetingPreReviewer'.
                for permission in proposed.permission_roles.iterkeys():
                    roles = list(proposed.permission_roles[permission])
                    if 'MeetingPreReviewer' not in roles:
                        continue
                    roles.remove('MeetingPreReviewer')
                    roles.append('MeetingServiceHead')
                    proposed.setPermission(permission, 0, roles)
                for permission in proposed_to_refadmin.permission_roles.iterkeys():
                    roles = list(proposed_to_refadmin.permission_roles[permission])
                    if 'MeetingRefAdmin' not in roles:
                        continue
                    roles.remove('MeetingServiceHead')
                    roles.append('MeetingPreReviewer')
                    proposed_to_refadmin.setPermission(permission, 0, roles)
                # The previous update on state 'proposed_to_refadmin' was a bit too restrictive:
                # it prevents the MeetingServiceHead from consulting the item once it has been
                # proposed_to_refadmin. So here we grant him back this right.
                for viewPerm in ('View', 'Access contents information'):
                    grantPermission(proposed_to_refadmin, viewPerm, 'MeetingServiceHead')
                # Update permission->role mappings for every other state, taking into
                # account new role 'MeetingServiceHead'. The idea is: later in the
                # workflow, MeetingServiceHead and MeetingPreReviewer are granted exactly
                # the same rights.
                for stateName in wf.states.keys():
                    if stateName in ('itemcreated', 'proposed', 'proposed_to_refadmin'):
                        continue
                    state = wf.states[stateName]
                    for permission in state.permission_roles.iterkeys():
                        roles = state.permission_roles[permission]
                        if ('MeetingPreReviewer' in roles) and \
                           ('MeetingServiceHead' not in roles):
                            grantPermission(state, permission, 'MeetingServiceHead')
                # Transition "backToProposedToServiceHead" must be protected by a popup, like
                # any other "correct"-like transition.
                toConfirm = meetingConfig.getTransitionsToConfirm()
                if 'MeetingItem.backToProposedToRefAdmin' not in toConfirm:
                    toConfirm = list(toConfirm)
                    toConfirm.append('MeetingItem.backToProposedToRefAdmin')
                    meetingConfig.setTransitionsToConfirm(toConfirm)
            logger.info(WF_APPLIED % ("charleroi_add_refadmin", meetingConfig.getId()))
            return True
        return False

# ------------------------------------------------------------------------------
InitializeClass(CustomCharleroiMeeting)
InitializeClass(CustomCharleroiMeetingItem)
InitializeClass(CustomCharleroiMeetingConfig)
InitializeClass(CustomCharleroiMeetingGroup)
InitializeClass(MeetingCharleroiCollegeWorkflowActions)
InitializeClass(MeetingCharleroiCollegeWorkflowConditions)
InitializeClass(MeetingItemCharleroiCollegeWorkflowActions)
InitializeClass(MeetingItemCharleroiCollegeWorkflowConditions)
InitializeClass(MeetingItemCharleroiCouncilWorkflowActions)
InitializeClass(MeetingItemCharleroiCouncilWorkflowConditions)
InitializeClass(MeetingCharleroiCouncilWorkflowActions)
InitializeClass(MeetingCharleroiCouncilWorkflowConditions)
InitializeClass(CustomCharleroiToolPloneMeeting)
# ------------------------------------------------------------------------------


class MCHItemPrettyLinkAdapter(ItemPrettyLinkAdapter):
    """
      Override to take into account MeetingCharleroi use cases...
    """

    def _leadingIcons(self):
        """
          Manage icons to display before the icons managed by PrettyLink._icons.
        """
        # Default PM item icons
        icons = super(MCHItemPrettyLinkAdapter, self)._leadingIcons()

        if self.context.isDefinedInTool():
            return icons

        itemState = self.context.queryState()
        # Add our icons for some review states
        if itemState == 'accepted_and_returned':
            icons.append(('accepted_and_returned.png',
                          translate('icon_help_accepted_and_returned',
                                    domain="PloneMeeting",
                                    context=self.request)))
        elif itemState == 'proposed_to_refadmin':
            icons.append(('proposeToRefAdmin.png',
                          translate('icon_help_proposed_to_refadmin',
                                    domain="PloneMeeting",
                                    context=self.request)))
        return icons
