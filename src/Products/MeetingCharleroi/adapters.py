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

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore.permissions import ReviewPortalContent
from zope.i18n import translate

from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.model import adaptations
from Products.PloneMeeting.model.adaptations import WF_APPLIED, grantPermission
from Products.PloneMeeting.adapters import ItemPrettyLinkAdapter
from Products.PloneMeeting.interfaces import IMeetingCustom, IMeetingItemCustom, \
    IMeetingGroupCustom, IMeetingConfigCustom, IToolPloneMeetingCustom
from Products.PloneMeeting.utils import checkPermission

from Products.MeetingCommunes.adapters import CustomMeetingItem, \
    MeetingItemCollegeWorkflowActions, MeetingItemCollegeWorkflowConditions
from Products.MeetingCommunes.adapters import CustomMeetingGroup
from Products.MeetingCommunes.adapters import MeetingCollegeWorkflowActions, \
    MeetingCollegeWorkflowConditions, CustomMeeting
from Products.MeetingCommunes.adapters import CustomMeetingConfig
from Products.MeetingCommunes.adapters import CustomToolPloneMeeting
from Products.MeetingCharleroi.interfaces import \
    IMeetingItemCharleroiCollegeWorkflowConditions, IMeetingItemCharleroiCollegeWorkflowActions,\
    IMeetingCharleroiCollegeWorkflowConditions, IMeetingCharleroiCollegeWorkflowActions, \
    IMeetingItemCharleroiCouncilWorkflowConditions, IMeetingItemCharleroiCouncilWorkflowActions,\
    IMeetingCharleroiCouncilWorkflowConditions, IMeetingCharleroiCouncilWorkflowActions

# disable most of wfAdaptations
customWfAdaptations = ('no_publication', 'no_global_observation', 'pre_validation', 'return_to_proposing_group',
                       'charleroi_add_refadmin')
MeetingConfig.wfAdaptations = customWfAdaptations
originalPerformWorkflowAdaptations = adaptations.performWorkflowAdaptations

# states taken into account by the 'no_global_observation' wfAdaptation
from Products.PloneMeeting.model import adaptations
noGlobalObsStates = ('itempublished', 'itemfrozen', 'accepted', 'refused',
                     'delayed', 'accepted_but_modified', 'pre_accepted')
adaptations.noGlobalObsStates = noGlobalObsStates

adaptations.WF_NOT_CREATOR_EDITS_UNLESS_CLOSED = ('delayed', 'refused', 'accepted',
                                                  'pre_accepted', 'accepted_but_modified')

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

    security.declarePrivate('doProposeToRefAdmin')

    def doProposeToRefAdmin(self, stateChange):
        pass


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

    def performCustomWFAdaptations(self, meetingConfig, wfAdaptation, logger, itemWorkflow, meetingWorkflow):
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


class MCItemPrettyLinkAdapter(ItemPrettyLinkAdapter):
    """
      Override to take into account MeetingCharleroi use cases...
    """

    def _leadingIcons(self):
        """
          Manage icons to display before the icons managed by PrettyLink._icons.
        """
        res = []
        if not self.context.meta_type == 'MeetingItem':
            return res

        # Default PM item icons
        icons = super(MCItemPrettyLinkAdapter, self)._leadingIcons()

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
