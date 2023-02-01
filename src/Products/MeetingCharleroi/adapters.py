# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from AccessControl import ClassSecurityInfo
from collections import OrderedDict
from collective.contact.plonegroup.utils import get_organizations
from DateTime import DateTime
from Globals import InitializeClass
from imio.helpers.cache import cleanRamCacheFor
from imio.history.utils import getLastWFAction
from plone import api
from plone.memoize import ram
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.MeetingCharleroi.config import CC_ARRET_OJ_CAT_ID
from Products.MeetingCharleroi.config import COMMUNICATION_CAT_ID
from Products.MeetingCharleroi.config import COUNCIL_DEFAULT_CATEGORY
from Products.MeetingCharleroi.config import COUNCIL_SPECIAL_CATEGORIES
from Products.MeetingCharleroi.config import DECISION_ITEM_SENT_TO_COUNCIL
from Products.MeetingCharleroi.config import NEVER_LATE_CATEGORIES
from Products.MeetingCharleroi.config import POLICE_GROUP_PREFIX
from Products.MeetingCharleroi.interfaces import IMeetingCharleroiCollegeWorkflowActions
from Products.MeetingCharleroi.interfaces import IMeetingCharleroiCollegeWorkflowConditions
from Products.MeetingCharleroi.interfaces import IMeetingCharleroiCouncilWorkflowActions
from Products.MeetingCharleroi.interfaces import IMeetingCharleroiCouncilWorkflowConditions
from Products.MeetingCharleroi.interfaces import IMeetingItemCharleroiCollegeWorkflowActions
from Products.MeetingCharleroi.interfaces import IMeetingItemCharleroiCollegeWorkflowConditions
from Products.MeetingCharleroi.interfaces import IMeetingItemCharleroiCouncilWorkflowActions
from Products.MeetingCharleroi.interfaces import IMeetingItemCharleroiCouncilWorkflowConditions
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.MeetingCommunes.adapters import CustomMeeting
from Products.MeetingCommunes.adapters import CustomMeetingConfig
from Products.MeetingCommunes.adapters import CustomMeetingItem
from Products.MeetingCommunes.adapters import CustomToolPloneMeeting
from Products.MeetingCommunes.adapters import MeetingCommunesWorkflowActions
from Products.MeetingCommunes.adapters import MeetingCommunesWorkflowConditions
from Products.MeetingCommunes.adapters import MeetingItemCommunesWorkflowActions
from Products.MeetingCommunes.adapters import MeetingItemCommunesWorkflowConditions
from Products.PloneMeeting.adapters import ItemPrettyLinkAdapter
from Products.PloneMeeting.interfaces import IMeetingConfigCustom
from Products.PloneMeeting.interfaces import IMeetingCustom
from Products.PloneMeeting.interfaces import IMeetingItemCustom
from Products.PloneMeeting.interfaces import IToolPloneMeetingCustom
from Products.PloneMeeting.Meeting import Meeting
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.MeetingItem import MeetingItem
# states taken into account by the 'no_global_observation' wfAdaptation
from Products.PloneMeeting.model import adaptations
from Products.PloneMeeting.model.adaptations import grantPermission
from zope.annotation import IAnnotations
from zope.i18n import translate
from zope.interface import implements

import re

customWfAdaptations = (  # ORDER IS IMPORTANT
    'only_creator_may_delete',
    # first define meeting workflow state removal
    'no_publication',
    # then define added item decided states
    'accepted_but_modified',
    'postpone_next_meeting',
    'mark_not_applicable',
    'removed',
    'removed_and_duplicated',
    'refused',
    'delayed',
    'pre_accepted',
    # charleroi specific
    'charleroi_return_to_any_state_when_prevalidated',
    # then other adaptations
    'return_to_proposing_group',
    'decide_item_when_back_to_meeting_from_returned_to_proposing_group',
    'hide_decisions_when_under_writing',
    'waiting_advices',
    'waiting_advices_proposing_group_send_back',
    'meetingmanager_correct_closed_meeting',
)
MeetingConfig.wfAdaptations = customWfAdaptations

noGlobalObsStates = ('itempublished', 'itemfrozen', 'accepted', 'refused',
                     'delayed', 'accepted_but_modified', 'pre_accepted')
adaptations.noGlobalObsStates = noGlobalObsStates

adaptations.WF_NOT_CREATOR_EDITS_UNLESS_CLOSED = ('delayed', 'refused', 'accepted',
                                                  'pre_accepted', 'accepted_but_modified')

adaptations.WAITING_ADVICES_FROM_STATES = {
    '*': (
        {'from_states': ('itemcreated',),
         'back_states': ('itemcreated',),
         'perm_cloned_states': ('itemcreated',),
         'remove_modify_access': True,
         'new_state_id': None},
        {'from_states': ('proposed',),
         'back_states': ('proposed',),
         'perm_cloned_states': ('proposed',),
         'remove_modify_access': True,
         'new_state_id': None},
        {'from_states': ('prevalidated',),
         'back_states': ('proposed_to_refadmin', 'prevalidated', 'validated'),
         'perm_cloned_states': ('prevalidated',),
         'remove_modify_access': True,
         'new_state_id': None},),
}

RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE = {'meetingitemcommunes_workflow':
                                                'meetingitemcommunes_workflow.itemcreated'}
adaptations.RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE = RETURN_TO_PROPOSING_GROUP_STATE_TO_CLONE


class CustomCharleroiMeeting(CustomMeeting):
    '''Adapter that adapts a custom meeting implementing IMeeting to the
       interface IMeetingCustom.'''

    implements(IMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, meeting):
        self.context = meeting

    Meeting.__pm_old_updateItemReferences = Meeting.updateItemReferences

    def updateItemReferences(self, startNumber=0, check_needed=False):
        """ """
        # clean ram.cache for item reference computation
        cleanRamCacheFor('Products.MeetingCharleroi.adapters._itemNumberCalculationQueryUids')
        # call old monkeypatched method
        self.__pm_old_updateItemReferences(startNumber, check_needed)

    Meeting.updateItemReferences = updateItemReferences

    def getDefaultAssemblyPolice(self):
        """ """
        if self.attribute_is_used('assemblyPolice'):
            tool = api.portal.get_tool('portal_plonemeeting')
            return tool.getMeetingConfig(self).getAssemblyPolice()
        return ''

    Meeting.getDefaultAssemblyPolice = getDefaultAssemblyPolice

    def _getPoliceItems(self, itemUids, categories=[], excludedCategories=[], list_types=['normal']):
        """Get all items from the group 'Police'."""
        tool = api.portal.get_tool('portal_plonemeeting')
        policeItems = self.getPrintableItemsByCategory(itemUids,
                                                       forceCategOrderFromConfig=True,
                                                       categories=categories,
                                                       excludedCategories=excludedCategories,
                                                       list_types=list_types,
                                                       groupIds=tool.adapted().zplGroups())
        if policeItems:
            return policeItems
        else:
            return []

    def _getItemsHeadedToAnotherMeetingConfig(self, itemsList, meetingConfigId=''):
        """
        Get all items which are supposed to go to the meeting config
        given by p_meetingConfigId. Just pass an empty string to get items
        which are not supposed to go to other MC. p_byDate sorts
        the items between the different meeting they are sent to.
        """
        filteredGroupedItems = []
        for groupedItems in itemsList:
            # store the group name as first element of the list
            filteredItems = [groupedItems[0]]
            # items not headed to another meeting config
            if meetingConfigId == '':
                filteredItems += [item for item in groupedItems[1:]
                                  if not item.getOtherMeetingConfigsClonableTo()]
            # items headed to another meeting config
            else:
                filteredItems += [item for item in groupedItems[1:]
                                  if meetingConfigId in item.getOtherMeetingConfigsClonableTo()]
            # if there is no item, do not keep the proposing group.
            if len(filteredItems) > 1:
                filteredGroupedItems.append(filteredItems)
        return filteredGroupedItems

    def _sortByGroupInCharge(self, itemsList):
        """
        Sort the item list p_itemsList by group in charge and
        return an ordered dict with group in charge as key and
        an another ordered dict as value containing the item's
        category as key and the list of all items having that
        group in charge and that category as value.
        """
        groupsInChargeItems = {}
        for categorizedItems in itemsList:
            for item in categorizedItems[1:]:
                groupInCharge = item.getGroupsInCharge(theObjects=True, first=True)
                # if we already have the group in charge in the dict.
                if groupInCharge in groupsInChargeItems:
                    # if we already have the category for that group in charge.
                    if categorizedItems[0] in groupsInChargeItems[groupInCharge]:
                        # add the item to the list of items for that category
                        # and that group in charge.
                        groupsInChargeItems[groupInCharge][categorizedItems[0]].append(item)
                    else:
                        # create the list with item in it
                        groupsInChargeItems[groupInCharge][categorizedItems[0]] = [item]
                else:
                    # create the ordereddict for categ and add the list of
                    # items of that categ in it.
                    categDict = OrderedDict()
                    categDict[categorizedItems[0]] = [item]
                    groupsInChargeItems[groupInCharge] = categDict
        return OrderedDict(sorted(groupsInChargeItems.items(),
                                  key=lambda t: t[0] and t[0].get_order()))

        return groupsInChargeItems

    def _sortByGroupInChargeByDate(self, itemsList):
        """
        Sort the item list p_itemsList by group in charge and
        return an ordered dict with group in charge as key and
        an another ordered dict as value containing the item's
        category as key and the list of all items having that
        group in charge and that category as value.
        """
        byDateItems = {}
        tool = api.portal.get_tool('portal_plonemeeting')
        councilMC = getattr(tool, 'meeting-config-council')
        categDict = OrderedDict()

        for categorizedItems in itemsList:
            for item in categorizedItems[1:]:

                # Take the relevant meeting according to the cloned item having a meeting or not.
                if item.getOtherMeetingConfigsClonableTo():
                    other_meeting_config_item = item.getItemClonedToOtherMC(item.getOtherMeetingConfigsClonableTo()[0])
                    if other_meeting_config_item and other_meeting_config_item.hasMeeting():
                        nextMeetingDate = other_meeting_config_item.getMeeting()
                    else:
                        nextMeetingDate = item._otherMCMeetingToBePresentedIn(councilMC)
                else:
                    nextMeetingDate = item._otherMCMeetingToBePresentedIn(councilMC)

                groupInCharge = item.getGroupsInCharge(theObjects=True, first=True)
                # if we already have the next meeting date in the dict.
                if nextMeetingDate in byDateItems:
                    # if we already have the group in charge in the dict.
                    if groupInCharge in byDateItems[nextMeetingDate]:
                        # if we already have the category for that group in charge.
                        if categorizedItems[0] in byDateItems[nextMeetingDate][groupInCharge]:
                            # add the item to the list of items for that category
                            # and that group in charge and that date.
                            byDateItems[nextMeetingDate][groupInCharge][categorizedItems[0]].append(item)
                        else:
                            # create the list with item in it
                            byDateItems[nextMeetingDate][groupInCharge][categorizedItems[0]] = [item]
                    else:
                        # create the key for that group in charge and add the item list in it.
                        categDict = OrderedDict()
                        categDict[categorizedItems[0]] = [item]
                        byDateItems[nextMeetingDate][groupInCharge] = categDict.copy()
                else:
                    # create the keys for categ, groups in charge and date
                    # and add the items list in it.
                    categDict = OrderedDict()
                    categDict[categorizedItems[0]] = [item]
                    groupsInChargeItems = OrderedDict()
                    groupsInChargeItems[groupInCharge] = categDict.copy()
                    byDateItems[nextMeetingDate] = groupsInChargeItems.copy()
        res = OrderedDict()
        # sort by groupInCharge
        for date in byDateItems.items():
            res[date[0]] = OrderedDict(sorted(date[1].items(), key=lambda t: t[0].get_order()))
        # sort by meeting date
        res = OrderedDict(
            sorted(
                res.items(),
                key=lambda t: (t[0] and t[0].getDate().strftime('%Y%m%d') or DateTime('1950/01/01'))))
        return res

    def _getPolicePrescriptiveItems(self, itemUids, list_types=['normal']):
        """
        Get all items from the group "Police" which are not from the
        communication category and not supposed to go to Council.
        """
        policeItems = self._getPoliceItems(
            itemUids,
            excludedCategories=[COMMUNICATION_CAT_ID, CC_ARRET_OJ_CAT_ID],
            list_types=list_types)

        filteredItems = self._getItemsHeadedToAnotherMeetingConfig(policeItems, '')
        return self._sortByGroupInCharge(filteredItems)

    def _getPoliceHeadedToCouncilItems(self, itemUids, list_types=['normal']):
        """
        Get all items from the group "Police" which are not from the
        communication category and supposed to go to council.
        """
        policeItems = self._getPoliceItems(
            itemUids,
            excludedCategories=[COMMUNICATION_CAT_ID, CC_ARRET_OJ_CAT_ID],
            list_types=list_types)

        filteredItems = self._getItemsHeadedToAnotherMeetingConfig(policeItems,
                                                                   'meeting-config-council')
        return self._sortByGroupInChargeByDate(filteredItems)

    def _getPoliceCommunicationItems(self, itemUids, list_types=['normal']):
        """
        Get all items from the group "Police" which are from the
        communication category.
        """
        return self._getPoliceItems(
            itemUids,
            categories=[COMMUNICATION_CAT_ID, CC_ARRET_OJ_CAT_ID],
            list_types=list_types)

    def _getStandardItems(self, itemUids, categories=[], excludedCategories=[], list_types=['normal']):
        """Get all items, except those from the group 'Police'."""
        everyItems = self.getPrintableItemsByCategory(itemUids,
                                                      forceCategOrderFromConfig=True,
                                                      list_types=list_types,
                                                      categories=categories,
                                                      excludedCategories=excludedCategories)
        groupedStandardItems = []
        tool = api.portal.get_tool('portal_plonemeeting')
        zplGroups = tool.adapted().zplGroups()
        for groupedItems in everyItems:
            standardItems = [groupedItems[0]]
            standardItems += [item for item in groupedItems[1:]
                              if item.getProposingGroup() not in zplGroups]

            # if there is no item, do not keep the proposing group.
            if len(standardItems) > 1:
                groupedStandardItems.append(standardItems)
        return groupedStandardItems

    def _getStandardPrescriptiveItems(self, itemUids, list_types=['normal']):
        '''
        Get items which are not from the group Police, not from the
        communication category and not supposed to go to council.
        '''
        standardItems = self._getStandardItems(
            itemUids,
            excludedCategories=[COMMUNICATION_CAT_ID, CC_ARRET_OJ_CAT_ID],
            list_types=list_types)

        filteredItems = self._getItemsHeadedToAnotherMeetingConfig(standardItems, '')
        return self._sortByGroupInCharge(filteredItems)

    def _getStandardHeadedToCouncilItems(self, itemUids, list_types=['normal']):
        '''
        Get items which are not from the group Police, not from the
        communication category and supposed to go to council.
        '''
        standardItems = self._getStandardItems(
            itemUids,
            excludedCategories=[COMMUNICATION_CAT_ID, CC_ARRET_OJ_CAT_ID],
            list_types=list_types)

        filteredItems = self._getItemsHeadedToAnotherMeetingConfig(standardItems,
                                                                   'meeting-config-council')
        return self._sortByGroupInChargeByDate(filteredItems)

    def _getStandardCommunicationItems(self, itemUids, list_types=['normal']):
        """
        Get all items not from the group "Police" which are from the
        COMMUNICATION_CAT_ID category..
        """
        return self._getStandardItems(
            itemUids,
            categories=[COMMUNICATION_CAT_ID],
            list_types=list_types)

    def _getStandardCCArretOJItems(self, itemUids, list_types=['normal']):
        """
        Get all items not from the group "Police" which are from the
        CC_ARRET_OJ_CAT_ID category..
        """
        return self._getStandardItems(
            itemUids,
            categories=[CC_ARRET_OJ_CAT_ID],
            list_types=list_types)

    def getPrintableItemsForAgenda(self, itemUids, standard=True, itemType='prescriptive', list_types=['normal']):
        """
        Return an ordered dict with the items' group in charge as key and another
        ordered dict as value. The second ordered dict has the items' categories as
        keys and the list of items as value.
        Items are filtered between "police items" and "standard items" thanks
        to p_standard. p_itemType is expecting 'prescriptive', 'toCouncil' or
        COMMUNICATION_CAT_ID and return respectively prescriptives, headed to
        council and communication items.
        """
        if standard is True:
            if itemType == 'prescriptive':
                return self._getStandardPrescriptiveItems(itemUids, list_types=list_types)
            elif itemType == 'toCouncil':
                return self._getStandardHeadedToCouncilItems(itemUids,
                                                             list_types=list_types)
            elif itemType == 'communication':
                return self._getStandardCommunicationItems(itemUids, list_types=list_types)
            elif itemType == 'cc-arret-oj':
                return self._getStandardCCArretOJItems(itemUids, list_types=list_types)
            else:
                return 'The itemType given to getPrintableItemsForAgenda ' \
                       'must be prescriptive, toCouncil, communication or cc-arret-oj'
        else:
            if itemType == 'prescriptive':
                return self._getPolicePrescriptiveItems(itemUids, list_types=list_types)
            elif itemType == 'toCouncil':
                return self._getPoliceHeadedToCouncilItems(itemUids,
                                                           list_types=list_types)
            elif itemType == 'communication':
                return self._getPoliceCommunicationItems(itemUids, list_types=list_types)
            else:
                return 'The itemType given to getPrintableItemsForAgenda ' \
                       'must be prescriptive, toCouncil or communication'


class CustomCharleroiMeetingItem(CustomMeetingItem):
    '''Adapter that adapts a custom meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom.'''
    implements(IMeetingItemCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    MeetingItem.__pm_old_getDecision = MeetingItem.getDecision

    def getDecision(self, **kwargs):
        '''Overridde 'decision' field accessor.
           Display specific message when College item is sent to Council.'''
        decision = self.__pm_old_getDecision(**kwargs)
        if self.portal_type == 'MeetingItemCollege':
            annotation_key = self._getSentToOtherMCAnnotationKey('meeting-config-council')
            ann = IAnnotations(self)
            if ann.get(annotation_key, None):
                decision = DECISION_ITEM_SENT_TO_COUNCIL
        return decision

    MeetingItem.getDecision = getDecision

    MeetingItem.__pm_old_getRawDecision = MeetingItem.getRawDecision

    def getRawDecision(self, **kwargs):
        '''Overridde 'decision' field accessor.
           Display specific message when College item is sent to Council.'''
        decision = self.__pm_old_getRawDecision(**kwargs)
        if self.portal_type == 'MeetingItemCollege':
            annotation_key = self._getSentToOtherMCAnnotationKey('meeting-config-council')
            ann = IAnnotations(self)
            if ann.get(annotation_key, None):
                decision = DECISION_ITEM_SENT_TO_COUNCIL
        return decision

    MeetingItem.getRawDecision = getRawDecision

    security.declarePrivate('setDecision')

    def setDecision(self, value, **kwargs):
        '''Overrides the field 'decision' mutator to avoid to lose original
           decision when DECISION_ITEM_SENT_TO_COUNCIL is in use.'''
        if value.strip() == DECISION_ITEM_SENT_TO_COUNCIL:
            return
        self.getField('decision').set(self, value, **kwargs)

    MeetingItem.setDecision = setDecision

    MeetingItem.__pm_old_validate_category = MeetingItem.validate_category

    def validate_category(self, value):
        '''For MeetingItemCollege, category 'indeterminee' can NOT be used if item will NOT be sent to Council.
           But it MUST be selected when the item IS to be sent to meeting-config-council '''
        res = self.__pm_old_validate_category(value)
        if res:
            return res

        if self.portal_type == 'MeetingItemCollege':
            configToCloneTo = self.REQUEST.get('otherMeetingConfigsClonableTo',
                                               self.getOtherMeetingConfigsClonableTo())
            if 'meeting-config-council' in configToCloneTo and value != COUNCIL_DEFAULT_CATEGORY:
                msg = translate('category_must_be_indeterminee',
                                domain='PloneMeeting',
                                context=self.REQUEST)
                return msg

            elif 'meeting-config-council' not in configToCloneTo and value == COUNCIL_DEFAULT_CATEGORY:
                msg = translate('category_indeterminee_not_allowed',
                                domain='PloneMeeting',
                                context=self.REQUEST)
                return msg

    MeetingItem.validate_category = validate_category

    def getCustomAdviceMessageFor(self, advice):
        '''If we are on a finance advice that is still not giveable because
           the item is not 'complete', we display a clear message.'''
        item = self.getSelf()
        if advice['id'] == finance_group_uid() and \
                advice['delay'] and \
                not advice['delay_started_on']:
            # import FINANCE_WAITING_ADVICES_STATES as it is monkeypatched
            from Products.MeetingCommunes.config import FINANCE_WAITING_ADVICES_STATES
            # item in state giveable but item not complete
            if item.query_state() in FINANCE_WAITING_ADVICES_STATES:
                return {'displayDefaultComplementaryMessage': False,
                        'displayAdviceReviewState': False,
                        'customAdviceMessage':
                            translate('finance_advice_not_giveable_because_item_not_complete',
                                      domain="PloneMeeting",
                                      context=item.REQUEST,
                                      default="Advice is still not giveable because item is not considered complete.")}
            elif getLastWFAction(item, 'proposeToFinance') and \
                    item.query_state() in ('itemcreated',
                                           'itemcreated_waiting_advices',
                                           'proposed_to_internal_reviewer',
                                           'proposed_to_internal_reviewer_waiting_advices',
                                           'proposed_to_director',):
                # advice was already given but item was returned back to the service
                return {'displayDefaultComplementaryMessage': False,
                        'displayAdviceReviewState': False,
                        'customAdviceMessage': translate(
                            'finance_advice_suspended_because_item_sent_back_to_proposing_group',
                            domain="PloneMeeting",
                            context=item.REQUEST,
                            default="Advice is suspended because it was sent back to proposing group.")}
        return {'displayDefaultComplementaryMessage': True,
                'displayAdviceReviewState': False,
                'customAdviceMessage': None}

    def _adviceDelayMayBeStarted(self, org_uid):
        """Really started when item completeness is 'complete' or 'evaluation_not_required'."""
        if org_uid == finance_group_uid():
            return self._is_complete()
        return super(CustomCharleroiMeetingItem, self)._adviceDelayMayBeStarted(org_uid)

    def _adviceIsAddableByCurrentUser(self, org_uid):
        """Only when item completeness is 'complete' or 'evaluation_not_required'."""
        if org_uid == finance_group_uid():
            return self._is_complete()
        return super(CustomCharleroiMeetingItem, self)._adviceIsAddableByCurrentUser(org_uid)

    def _adviceIsAddable(self, org_uid):
        ''' '''
        return self._adviceIsAddableByCurrentUser(org_uid)

    def _advicePortalTypeForAdviser(self, groupId):
        """Return the meetingadvice portal_type that will be added for given p_groupId.
           By default we always use meetingadvice but this makes it possible to have several
           portal_types for meetingadvice."""
        if groupId == finance_group_uid():
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
        if finance_group_uid() not in item.adviceIndex or \
                not '%s_financialcontrollers' % finance_group_uid() in member.getGroups():
            return False

        # item must be still in a state where the advice can be given
        # and advice must still not have been given
        if not item.query_state() == 'prevalidated_waiting_advices':
            return False
        return True

    def _findCustomOrderFor(self, insertMethod):
        '''Manage our custom inserting methods 'on_communication'
           and 'on_police_then_other_groups'.'''
        item = self.getSelf()
        if insertMethod == 'on_police_then_other_groups':
            if item.getProposingGroup(True).getId().startswith(POLICE_GROUP_PREFIX):
                return 0
            else:
                return 1
        elif insertMethod == 'on_communication':
            if item.getCategory() == COMMUNICATION_CAT_ID:
                return 0
            elif item.getCategory() == CC_ARRET_OJ_CAT_ID:
                return 1
            else:
                return 2
        raise NotImplementedError

    def mayChangeDelayTo(self, days):
        """May current user change finance advice delay to given p_days?
           Given p_days could be :
           - 5 : in this case, only the proposingGroup (while having edit permission) may change to this delay;
           - 20 : in this case, only finance advisers may change to this delay;
           - 10 : come back from 5 or 20 : if from 20, only finance advisers may come back,
                  if from 5, only proposingGroup (while having edit permission).
           In every case, 5 and 20 days are only available thru the popup widget, not from the item edit form,
           we check that 'managing_available_delays' is in the REQUEST."""
        # in case nothing was already selected
        # the only available value is 10
        if finance_group_uid() not in self.context.adviceIndex:
            if days == 10:
                return True
            else:
                return False

        res = False
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        is20DaysDelay = self.context.adviceIndex[finance_group_uid()]['delay'] == '20'
        # bypass for Managers
        isManager = tool.isManager(cfg)
        if days == 10 and _checkPermission(ModifyPortalContent, self.context) and not is20DaysDelay:
            res = True
        # change delay widget
        elif self.context.REQUEST.get('managing_available_delays', None):
            if isManager:
                res = True
            # to 20 or back from 20
            elif days == 20 or (days == 10 and is20DaysDelay):
                itemState = self.context.query_state()
                if itemState == 'prevalidated_waiting_advices' and \
                        tool.adapted().isFinancialUser():
                    res = True
            # to 5, only available thru change delay widget
            elif days == 5 and not is20DaysDelay:
                if _checkPermission(ModifyPortalContent, self.context):
                    res = True

        return res

    def getItemRefForActe(self, oj=False):
        '''Compute the College item reference.'''
        item = self.getSelf()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        isPoliceItem = bool(item.getProposingGroup(theObject=True).getId().startswith(POLICE_GROUP_PREFIX))
        isCommuItem = bool(item.getCategory() == COMMUNICATION_CAT_ID)
        toSendToCouncil = bool('meeting-config-council' in item.getOtherMeetingConfigsClonableTo())
        isPrivacySecret = bool(item.getPrivacy() == 'secret')

        additionalQuery = {}
        policeItems = {'getProposingGroup': {'query': tool.adapted().zplGroups()}}
        notPoliceItems = {'getProposingGroup': {'not': tool.adapted().zplGroups()}}
        toSendToCouncilItems = {'sentToInfos': {'query': ['meeting-config-council__clonable_to',
                                                          'meeting-config-council__clonable_to_emergency',
                                                          'meeting-config-council__cloned_to',
                                                          'meeting-config-council__cloned_to_emergency']}}
        notToSendToCouncilItems = {'sentToInfos': {'query': 'not_to_be_cloned_to'}}
        notCommunicationItems = {'getCategory': {'not': COMMUNICATION_CAT_ID}}
        secretItems = {'privacy': {'query': 'secret'}}

        ref = '-'
        if not isCommuItem:
            meeting = item.getMeeting()
            year = meeting.date.strftime('%Y')
            meetingNumber = cfg.getLastMeetingNumber() + 1
            if meeting.meeting_number != -1:
                meetingNumber = meeting.meeting_number
            ref = str(year) + '/' + str(meetingNumber)
            additionalQuery.update(notCommunicationItems)
            if isPrivacySecret:
                ref = ref + '/HC'
                additionalQuery.update(secretItems)
            if isPoliceItem:
                additionalQuery.update(policeItems)
                if not toSendToCouncil:
                    additionalQuery.update(notToSendToCouncilItems)
                    ref = ref + '/ZP'
                else:
                    ref = ref + '/ZP/C'
                    additionalQuery.update(toSendToCouncilItems)
            if not isPoliceItem:
                additionalQuery.update(notPoliceItems)
                if not toSendToCouncil:
                    ref = ref
                    additionalQuery.update(notToSendToCouncilItems)
                else:
                    ref = ref + '/C'
                    additionalQuery.update(toSendToCouncilItems)
            itemNumber = self._itemNumberCalculation(item, meeting, additionalQuery)
            ref = ref + '/' + str(itemNumber)

        # if for oj, manage the A and B items.
        if oj:
            if item.getToDiscuss():
                ref = ref + '/B'
            else:
                ref = ref + '/A'

        return ref

    def getItemRefForActeCouncil(self, oj=False):
        '''Compute the Council item reference.'''
        item = self.getSelf()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        isSpecialItem = bool(item.getCategory() in COUNCIL_SPECIAL_CATEGORIES)
        isLateItem = bool(item.getListType() != 'normal')

        additionalQuery = {}
        specialItems = {'getCategory': {'query': COUNCIL_SPECIAL_CATEGORIES}}
        normalItems = {
            'listType': {'query': 'normal'},
            'getCategory': {'not': COUNCIL_SPECIAL_CATEGORIES}}
        lateItems = {'listType': {'not': 'normal'}}

        meeting = item.getMeeting()
        year = meeting.date.strftime('%Y')
        meetingNumber = cfg.getLastMeetingNumber() + 1
        if meeting.meeting_number != -1:
            meetingNumber = meeting.meeting_number
        ref = str(year) + '/' + str(meetingNumber)
        if isSpecialItem:
            ref = ref + '/S'
            additionalQuery.update(specialItems)
        elif isLateItem:
            ref = ref + '/U'
            additionalQuery.update(lateItems)
        else:
            # normal items
            additionalQuery.update(normalItems)

        itemNumber = self._itemNumberCalculation(item, meeting, additionalQuery)
        ref = ref + '/' + str(itemNumber)
        return ref

    # def _itemNumberCalculationQueryUids_cachekey(method, self, meeting, additionalQuery):
    #     '''cachekey method for self._itemNumberCalculationQueryUids.'''
    #     return (self.context.REQUEST._debug, meeting, additionalQuery)
    #
    # @ram.cache(_itemNumberCalculationQueryUids_cachekey)
    def _itemNumberCalculationQueryUids(self, meeting, additionalQuery):
        """ """
        # do the query unrestricted so we have same result for users
        # that do not have access to every items of the meeting
        brains = meeting.get_items(ordered=True,
                                   the_objects=False,
                                   additional_catalog_query=additionalQuery,
                                   unrestricted=True)
        return [brain.UID for brain in brains]

    def _itemNumberCalculation(self, item, meeting, additionalQuery={}):
        '''Compute the item number used in the reference.'''
        uids = self._itemNumberCalculationQueryUids(meeting, additionalQuery)
        number = 0
        found = False
        for uid in uids:
            number += 1
            if uid == item.UID():
                found = True
                break
        if not found:
            return ''
        else:
            return number

    def showFinanceAdviceDocuments(self):
        docgen = self.context.restrictedTraverse('document-generation')
        helper = docgen.get_generation_context_helper()
        return helper.showFinancesAdvice()

    def _getCommunicationListType(self):
        '''If listType 'communication' is used in the meetingConfig, and the category of
           this meetingItem is also 'communication'.
           Then the listType 'communication' should always be applied. '''
        item = self.getSelf()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(item)
        pattern = r'^%s.?$' % COMMUNICATION_CAT_ID
        prog = re.compile(pattern)

        list_types = [listType['identifier'] for listType in cfg.getListTypes()]
        if 'communication' in list_types and prog.match(item.getCategory()):
            return 'communication'
        return None

    def getListTypeLateValue(self, meeting):
        '''If listType 'communication' is used in the meetingConfig, and the category of
           this meetingItem is also 'communication'.
           Then the listType 'communication' should always be applied. '''
        communication = self._getCommunicationListType()
        if communication:
            return communication

        '''Returns 'late' by default except if item is inserted into a Council meeting
           and is coming from a College item presented to an extraordinary meeting.'''
        if self.context.portal_type == 'MeetingItemCouncil':
            predecessor = self.context.get_predecessor()
            if predecessor and \
                    predecessor.portal_type == 'MeetingItemCollege' and \
                    (predecessor.hasMeeting() and predecessor.getMeeting().extraordinary_session):
                return 'lateextracollege'

        return self.context.getListTypeLateValue(meeting)

    def getListTypeNormalValue(self, meeting):
        '''If listType 'communication' is used in the meetingConfig, and the category of
           this meetingItem is also 'communication'.
           Then the listType 'communication' should always be applied. '''
        communication = self._getCommunicationListType()
        if communication:
            return communication
        return self.context.getListTypeNormalValue(meeting)

    def getAdviceRelatedIndexes(self):
        '''Update index 'financesAdviceCategory' in addition to default 'indexAdvisers'.'''
        return ['indexAdvisers', 'financesAdviceCategory']


class CustomCharleroiMeetingConfig(CustomMeetingConfig):
    '''Adapter that adapts a custom meetingConfig implementing IMeetingConfig to the
       interface IMeetingConfigCustom.'''

    implements(IMeetingConfigCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    def extraItemEvents(self):
        '''See doc in interfaces.py.'''
        return ['sentBackToRefAdminWhileSigningNotPositiveFinancesAdvice']

    def extraInsertingMethods(self):
        '''See doc in interfaces.py.'''
        return OrderedDict((
            ('on_communication', []),
            ('on_police_then_other_groups', []),
        ))


class MeetingCharleroiCollegeWorkflowActions(MeetingCommunesWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCharleroiCollegeWorkflowActions'''

    implements(IMeetingCharleroiCollegeWorkflowActions)
    security = ClassSecurityInfo()


class MeetingCharleroiCollegeWorkflowConditions(MeetingCommunesWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCharleroiCollegeWorkflowConditions'''

    implements(IMeetingCharleroiCollegeWorkflowConditions)
    security = ClassSecurityInfo()


class MeetingItemCharleroiCollegeWorkflowActions(MeetingItemCommunesWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCharleroiCollegeWorkflowActions'''

    implements(IMeetingItemCharleroiCollegeWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doProposeToRefAdmin')

    def doProposeToRefAdmin(self, stateChange):
        pass

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
            if event['action'] == 'wait_advices_from_prevalidated':
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


class MeetingItemCharleroiCollegeWorkflowConditions(MeetingItemCommunesWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCharleroiCollegeWorkflowConditions'''

    implements(IMeetingItemCharleroiCollegeWorkflowConditions)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item
        self.tool = api.portal.get_tool('portal_plonemeeting')
        self.cfg = self.tool.getMeetingConfig(self.context)
        self.review_state = self.context.query_state()

    security.declarePublic('mayProposeToRefAdmin')

    def mayProposeToRefAdmin(self):
        res = False
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayWait_advices_from_proposed_to_refadmin')

    def mayWait_advices_from_proposed_to_refadmin(self):
        """ """
        return self.mayWait_advices(self._getWaitingAdvicesStateFrom('proposed_to_refadmin'))

    security.declarePublic('mayValidate')

    def mayValidate(self):
        res = MeetingItemCommunesWorkflowConditions.mayValidate(self)
        if res and not self.context.REQUEST.get('duplicating_and_validating_item', False):
            # if finances advice is asked, item may only be validated
            # if the advice has actually be given
            if finance_group_uid() in self.context.adviceIndex and \
                    not self.context.adviceIndex[finance_group_uid()]['type'].endswith('_finance'):
                res = False
        return res

    security.declarePublic('mayCorrect')

    def mayCorrect(self, destinationState=None):
        '''See docstring in interfaces.py'''
        res = MeetingItemCommunesWorkflowConditions(self.context).mayCorrect(destinationState)
        tool = api.portal.get_tool('portal_plonemeeting')
        # if item is sent to finances, only finances advisers and MeetingManagers may send it back
        if self.context.query_state() == 'prevalidated_waiting_advices':
            res = False
            if destinationState == 'validated':
                # in this case, we need the 'mayValidate' to True in the REQUEST
                if self.context.REQUEST.get('mayValidate', False):
                    res = True
            elif destinationState == 'proposed_to_refadmin':
                # item may be sent back to refadmin when completeness is not 'complete' or
                # when the advice delay is exceeded, it is automatically sent back to refadmin
                # in this case, we need the 'maybackTo_proposed_to_refadmin_from_waiting_advices'
                # to True in the REQUEST
                if self.context.REQUEST.get('maybackTo_proposed_to_refadmin_from_waiting_advices', False):
                    res = True
                elif tool.adapted().isFinancialUser() and \
                        self.context.getCompleteness() in ('completeness_incomplete',
                                                           'completeness_not_yet_evaluated',
                                                           'completeness_evaluation_asked_again'):
                    res = True
            # only administrators may send back to director from finances
            elif destinationState == 'prevalidated' and tool.isManager(realManagers=True):
                res = True

        return res

    security.declarePublic('isLateFor')

    def isLateFor(self, meeting):
        '''Some categories are never considered 'late'.'''
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(meeting)
        if self.context.getCategory() in NEVER_LATE_CATEGORIES.get(cfg.getId(), []):
            return False

        # return original behavior
        return MeetingItemCommunesWorkflowConditions.isLateFor(self, meeting)


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
        if _checkPermission(ReviewPortalContent, self.context):
            res = True
        return res


class CustomCharleroiToolPloneMeeting(CustomToolPloneMeeting):
    '''Adapter that adapts a tool implementing ToolPloneMeeting to the
       interface IToolPloneMeetingCustom'''

    implements(IToolPloneMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    def zplGroups(self, the_objects=False):
        """Return organizations having id starting with POLICE_GROUP_PREFIX."""
        orgs = [org for org in get_organizations(the_objects=True)
                if org.getId().startswith(POLICE_GROUP_PREFIX)]
        if not the_objects:
            orgs = [org.UID() for org in orgs]
        return orgs

    def enableNonFinancesStyles(self, context):
        """Condition for enabling the meetingcharleroi_non_finances.css
           made especially to hide/show the 'Finances category' faceted widget."""
        member = api.user.get_current()
        if '{0}_advisers'.format(finance_group_uid()) in member.getGroups() or "Manager" in member.getRoles():
            return False
        return True

    def performCustomWFAdaptations(self,
                                   meetingConfig,
                                   wfAdaptation,
                                   logger,
                                   itemWorkflow,
                                   meetingWorkflow):
        '''This function applies workflow changes as specified by the
           p_meetingConfig.'''
        if wfAdaptation == 'charleroi_return_to_any_state_when_prevalidated':
            # Allow reviewers and managers to send items back to any previous state in one click
            if 'prevalidated' in itemWorkflow.states:
                transitions = itemWorkflow.transitions

                if 'proposed_to_refadmin' in itemWorkflow.states:
                    if 'backToProposedFromPrevalidated' not in transitions:
                        transitions.addTransition('backToProposedFromPrevalidated')

                    transition = itemWorkflow.transitions['backToProposedFromPrevalidated']
                    transition.setProperties(
                        title='backToProposedFromPrevalidated',
                        new_state_id='proposed', trigger_type=1, script_name='',
                        actbox_name='backToProposed', actbox_url='',
                        actbox_icon='%(portal_url)s/backToProposed.png', actbox_category='workflow',
                        props={'guard_expr': 'python:here.wfConditions().mayCorrect("prevalidated")'})

                if 'backToItemCreatedFromPrevalidated' not in transitions:
                    transitions.addTransition('backToItemCreatedFromPrevalidated')

                transition = itemWorkflow.transitions['backToItemCreatedFromPrevalidated']
                transition.setProperties(
                    title='backToItemCreatedFromPrevalidated',
                    new_state_id='itemcreated', trigger_type=1, script_name='',
                    actbox_name='backToItemCreated', actbox_url='',
                    actbox_icon='%(portal_url)s/backToItemCreated.png', actbox_category='workflow',
                    props={'guard_expr': 'python:here.wfConditions().mayCorrect("prevalidated")'})

                # Update connections between states and transitions
                itemWorkflow.states['prevalidated'].setProperties(
                    title='prevalidated', description='',
                    transitions=['backToProposedFromPrevalidated',
                                 'backToItemCreatedFromPrevalidated',
                                 'backToProposedToRefAdmin',
                                 'validate'])
                return True
        return False


# ------------------------------------------------------------------------------
InitializeClass(CustomCharleroiMeeting)
InitializeClass(CustomCharleroiMeetingItem)
InitializeClass(CustomCharleroiMeetingConfig)
InitializeClass(MeetingCharleroiCollegeWorkflowActions)
InitializeClass(MeetingCharleroiCollegeWorkflowConditions)
InitializeClass(MeetingItemCharleroiCollegeWorkflowActions)
InitializeClass(MeetingItemCharleroiCollegeWorkflowConditions)
InitializeClass(MeetingItemCharleroiCouncilWorkflowActions)
InitializeClass(MeetingItemCharleroiCouncilWorkflowConditions)
InitializeClass(MeetingCharleroiCouncilWorkflowActions)
InitializeClass(MeetingCharleroiCouncilWorkflowConditions)
InitializeClass(CustomCharleroiToolPloneMeeting)
