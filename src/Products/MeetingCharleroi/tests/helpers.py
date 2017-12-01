# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 by Imio.be
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

from plone import api
from Products.PloneMeeting.config import MEETING_GROUP_SUFFIXES
from Products.PloneMeeting.tests.helpers import PloneMeetingTestingHelpers
from Products.MeetingCharleroi.config import FINANCE_GROUP_ID
from Products.MeetingCharleroi.config import POLICE_GROUP_PREFIX
from Products.MeetingCharleroi.profiles.zcharleroi import import_data as charleroi_import_data
from Products.MeetingCharleroi.setuphandlers import _configureCollegeCustomAdvisers
from Products.MeetingCharleroi.setuphandlers import _createFinancesGroup
from Products.MeetingCharleroi.setuphandlers import _demoData
from Products.MeetingCharleroi.setuphandlers import _addCouncilDemoData


class MeetingCharleroiTestingHelpers(PloneMeetingTestingHelpers):
    '''Stub class that provides some helper methods about testing.'''

    TRANSITIONS_FOR_PROPOSING_ITEM_FIRST_LEVEL_1 = TRANSITIONS_FOR_PROPOSING_ITEM_FIRST_LEVEL_2 = ('propose',
                                                                                                   'proposeToRefAdmin')
    TRANSITIONS_FOR_PUBLISHING_MEETING_1 = TRANSITIONS_FOR_PUBLISHING_MEETING_2 = ('freeze', 'publish', )
    TRANSITIONS_FOR_FREEZING_MEETING_1 = TRANSITIONS_FOR_FREEZING_MEETING_2 = ('freeze', )
    TRANSITIONS_FOR_DECIDING_MEETING_1 = ('freeze', 'decide', )
    TRANSITIONS_FOR_DECIDING_MEETING_2 = ('freeze', 'publish', 'decide', )
    TRANSITIONS_FOR_CLOSING_MEETING_1 = TRANSITIONS_FOR_CLOSING_MEETING_2 = ('freeze',
                                                                             'publish',
                                                                             'decide',
                                                                             'close', )

    TRANSITIONS_FOR_PROPOSING_ITEM_1 = ('propose',
                                        'proposeToRefAdmin',
                                        'prevalidate', )

    TRANSITIONS_FOR_VALIDATING_ITEM_1 = ('propose',
                                         'proposeToRefAdmin',
                                         'prevalidate',
                                         'validate', )

    TRANSITIONS_FOR_PRESENTING_ITEM_1 = ('propose',
                                         'proposeToRefAdmin',
                                         'prevalidate',
                                         'validate',
                                         'present', )

    TRANSITIONS_FOR_ACCEPTING_ITEMS_1 = ('freeze', 'decide', )
    TRANSITIONS_FOR_ACCEPTING_ITEMS_2 = ('freeze', 'publish', 'decide', )
    BACK_TO_WF_PATH_1 = BACK_TO_WF_PATH_2 = {
        # Meeting
        'created': ('backToDecisionsPublished',
                    'backToDecided',
                    'backToPublished',
                    'backToFrozen',
                    'backToCreated',),
        # MeetingItem
        'itemcreated': ('backToItemPublished',
                        'backToItemFrozen',
                        'backToPresented',
                        'backToValidated',
                        'backToPrevalidated',
                        'backToProposedToRefAdmin',
                        'backToProposed',
                        'backToItemCreated', ),
        'proposed': ('backToItemPublished',
                     'backToItemFrozen',
                     'backToPresented',
                     'backToValidated',
                     'backToPrevalidated',
                     'backToProposedToRefAdmin',
                     'backToProposed', ),
        'prevalidated': ('backToItemPublished',
                         'backToItemFrozen',
                         'backToPresented',
                         'backToValidated',
                         'backToPrevalidated',),
        'validated': ('backToItemPublished',
                      'backToItemFrozen',
                      'backToPresented',
                      'backToValidated',),
        'presented': ('backToItemPublished',
                      'backToItemFrozen',
                      'backToPresented', )}

    WF_ITEM_STATE_NAME_MAPPINGS_1 = {
        'itemcreated': 'itemcreated',
        'proposed_first_level': 'proposed_to_refadmin',
        'proposed': 'prevalidated',
        'proposed_to_refadmin': 'proposed_to_refadmin',
        'prevalidated': 'prevalidated',
        'validated': 'validated',
        'presented': 'presented',
        'itemfrozen': 'itemfrozen'}
    WF_ITEM_STATE_NAME_MAPPINGS_2 = WF_ITEM_STATE_NAME_MAPPINGS_1

    # in which state an item must be after an particular meeting transition?
    ITEM_WF_STATE_AFTER_MEETING_TRANSITION = {'publish_decisions': 'accepted',
                                              'close': 'accepted'}

    TRANSITIONS_FOR_ACCEPTING_ITEMS_MEETING_1 = TRANSITIONS_FOR_ACCEPTING_ITEMS_MEETING_2 = ('freeze', 'decide', )

    def _configureFinancesAdvice(self, cfg):
        """ """
        # configure customAdvisers for 'meeting-config-college'
        _configureCollegeCustomAdvisers(self.portal)
        cfg.setTransitionsReinitializingDelays(
            charleroi_import_data.collegeMeeting.transitionsReinitializingDelays)
        # add finances group
        _createFinancesGroup(self.portal)
        # put users in finances group
        self._setupFinancesGroup()
        # configure usedAdviceTypes
        cfg.setUsedAdviceTypes(('asked_again',
                                'positive',
                                'positive_with_remarks',
                                'negative',
                                'nil',
                                'positive_finance',
                                'positive_with_remarks_finance',
                                'negative_finance',
                                'not_given_finance'))
        # finances advice can be given when item in state 'prevalidated_waiting_advices'
        cfg.setKeepAccessToItemWhenAdviceIsGiven(True)

    def _setupFinancesGroup(self):
        '''Configure finances group.'''
        groupsTool = api.portal.get_tool('portal_groups')
        # add finances users to relevant groups
        # _advisers
        groupsTool.addPrincipalToGroup('pmFinController', '%s_advisers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinEditor', '%s_advisers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinReviewer', '%s_advisers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinManager', '%s_advisers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('dfin', '%s_advisers' % FINANCE_GROUP_ID)
        # respective _financesXXX groups
        groupsTool.addPrincipalToGroup('pmFinController', '%s_financialcontrollers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinEditor', '%s_financialeditors' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinReviewer', '%s_financialreviewers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinManager', '%s_financialmanagers' % FINANCE_GROUP_ID)
        # dfin is member of every finances groups
        groupsTool.addPrincipalToGroup('dfin', '%s_financialcontrollers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('dfin', '%s_financialeditors' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('dfin', '%s_financialreviewers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('dfin', '%s_financialmanagers' % FINANCE_GROUP_ID)

    def _setupPoliceGroup(self):
        '''Configure police group.
           - create 'zone-de-police' group;
           - add 'pmManager' to the _creators group;
           - add some default categories.'''
        # due to complex setup to manage college and council,
        # sometimes this method is called twice...
        if POLICE_GROUP_PREFIX in self.tool.objectIds():
            return

        self.changeUser('siteadmin')
        self.create('MeetingGroup',
                    id=POLICE_GROUP_PREFIX,
                    title="Zone de Police", acronym='ZPL')
        self.create('MeetingGroup',
                    id=POLICE_GROUP_PREFIX + '-compta',
                    title="Zone de Police comptable spécial", acronym='ZPLCS')
        self.create('MeetingGroup',
                    id='groupincharge1',
                    title="Group in charge 1", acronym='GIC1')
        self.create('MeetingGroup',
                    id='groupincharge2',
                    title="Group in charge 2", acronym='GIC2')
        # police is added at the end of existing groups
        self.assertEquals(self.tool.objectIds('MeetingGroup'),
                          ['developers',
                           'vendors',
                           # disabled
                           'endUsers',
                           POLICE_GROUP_PREFIX,
                           POLICE_GROUP_PREFIX + '-compta',
                           'groupincharge1',
                           'groupincharge2'])
        # set groupsInCharge for 'vendors' and 'developers'
        self.tool.get(POLICE_GROUP_PREFIX).setGroupsInCharge(('groupincharge1',))
        self.tool.get(POLICE_GROUP_PREFIX + '-compta').setGroupsInCharge(('groupincharge1',))
        self.tool.vendors.setGroupsInCharge(('groupincharge1',))
        self.tool.developers.setGroupsInCharge(('groupincharge2',))
        # make 'pmManager' able to manage everything for 'vendors' and 'police'
        groupsTool = self.portal.portal_groups
        for groupId in ('vendors', POLICE_GROUP_PREFIX, POLICE_GROUP_PREFIX + '-compta'):
            for suffix in MEETING_GROUP_SUFFIXES:
                groupsTool.addPrincipalToGroup('pmManager', '{0}_{1}'.format(groupId, suffix))

        self._removeConfigObjectsFor(self.meetingConfig,
                                     folders=['recurringitems', 'itemtemplates', 'categories'])
        self._createCategories()
        self._createItemTemplates()

    def _createCategories(self):
        """ """
        if self.meetingConfig.getId() == 'meeting-config-college':
            categories = charleroi_import_data.collegeMeeting.categories
        else:
            categories = charleroi_import_data.councilMeeting.categories
        # create categories
        for cat in categories:
            data = {'id': cat.id,
                    'title': cat.title,
                    'description': cat.description}
            self.create('MeetingCategory', **data)

    def _createItemTemplates(self):
        """ """
        if self.meetingConfig.getId() == 'meeting-config-college':
            templates = charleroi_import_data.collegeMeeting.itemTemplates
        else:
            templates = charleroi_import_data.councilMeeting.itemTemplates
        for template in templates:
            data = {'id': template.id,
                    'title': template.title,
                    'description': template.description,
                    'category': template.category,
                    'proposingGroup': template.proposingGroup.startswith(POLICE_GROUP_PREFIX) and
                    template.proposingGroup or 'developers',
                    # 'templateUsingGroups': template.templateUsingGroups,
                    'decision': template.decision}
            self.create('MeetingItemTemplate', **data)

    def _createRecurringItems(self):
        """ """
        if self.meetingConfig.getId() == 'meeting-config-college':
            items = charleroi_import_data.collegeMeeting.recurringItems
        else:
            items = charleroi_import_data.councilMeeting.recurringItems
        for item in items:
            group_in_charge_value = 'developers__groupincharge__{0}'.format(
                self.tool.developers.getGroupsInCharge()[0])
            data = {'id': item.id,
                    'title': item.title,
                    'description': item.description,
                    'category': item.category,
                    'proposingGroup': 'developers',
                    'proposingGroupWithGroupInCharge': group_in_charge_value,
                    'decision': item.decision,
                    'meetingTransitionInsertingMe': item.meetingTransitionInsertingMe}
            self.create('MeetingItemRecurring', **data)

    def setupCouncilConfig(self):
        """ """
        cfg = getattr(self.tool, 'meeting-config-college')
        cfg.setItemManualSentToOtherMCStates(charleroi_import_data.collegeMeeting.itemManualSentToOtherMCStates)

        cfg2 = getattr(self.tool, 'meeting-config-council')
        # this will especially setup groups in charge, necessary to present items to a Council meeting
        self._setupPoliceGroup()
        cfg2.setListTypes(charleroi_import_data.councilMeeting.listTypes)
        cfg2.setSelectablePrivacies(charleroi_import_data.councilMeeting.selectablePrivacies)
        cfg2.setWorkflowAdaptations(charleroi_import_data.councilMeeting.workflowAdaptations)
        # items come validated
        cfg2.setTransitionsForPresentingAnItem(('present', ))
        cfg2.setItemReferenceFormat(charleroi_import_data.councilMeeting.itemReferenceFormat)
        cfg2.setUsedItemAttributes(charleroi_import_data.councilMeeting.usedItemAttributes)
        # setup inserting methods
        cfg2.setInsertingMethodsOnAddItem(charleroi_import_data.councilMeeting.insertingMethodsOnAddItem)
        cfg2.at_post_edit_script()

    def setupCollegeConfig(self):
        """ """
        cfg = self.meetingConfig

        self._setupPoliceGroup()
        self._configureFinancesAdvice(cfg)
        cfg.setCustomAdvisers(charleroi_import_data.collegeMeeting.customAdvisers)
        cfg.setInsertingMethodsOnAddItem(charleroi_import_data.collegeMeeting.insertingMethodsOnAddItem)
        cfg.setUseGroupsAsCategories(charleroi_import_data.collegeMeeting.useGroupsAsCategories)
        cfg.setItemReferenceFormat(charleroi_import_data.collegeMeeting.itemReferenceFormat)
        # let creators select the 'toDiscuss' value
        cfg.setToDiscussSetOnItemInsert(False)
        cfg.setMeetingConfigsToCloneTo(charleroi_import_data.collegeMeeting.meetingConfigsToCloneTo)

    def setupCollegeDemoData(self):
        """ """
        self.setupCollegeConfig()
        # create items and meetings using demo data
        self.changeUser('pmManager')
        collegeMeeting, collegeExtraMeeting = _demoData(
            self.portal,
            userId='pmManager',
            firstTwoGroupIds=('developers', 'vendors'))
        return collegeMeeting, collegeExtraMeeting

    def setupCouncilDemoData(self):
        """ """
        collegeMeeting, collegeExtraMeeting = self.setupCollegeDemoData()
        self.changeUser('siteadmin')
        self._removeConfigObjectsFor(self.meetingConfig2,
                                     folders=['recurringitems', 'itemtemplates', 'categories'])
        current_cfg = self.meetingConfig
        self.setMeetingConfig(self.meetingConfig2.getId())
        self._createCategories()
        self._createItemTemplates()
        self._createRecurringItems()
        self.setupCouncilConfig()
        councilMeeting = _addCouncilDemoData(collegeMeeting,
                                             collegeExtraMeeting,
                                             userId='pmManager',
                                             firstTwoGroupIds=('developers', 'vendors'))
        self.setMeetingConfig(current_cfg.getId())
        return councilMeeting
