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
from Products.MeetingCharleroi.config import POLICE_GROUP_ID
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

    WF_STATE_NAME_MAPPINGS = {'itemcreated': 'itemcreated',
                              'proposed_first_level': 'proposed_to_refadmin',
                              'proposed': 'prevalidated',
                              'proposed_to_refadmin': 'proposed_to_refadmin',
                              'prevalidated': 'prevalidated',
                              'validated': 'validated',
                              'presented': 'presented'}

    # in which state an item must be after an particular meeting transition?
    ITEM_WF_STATE_AFTER_MEETING_TRANSITION = {'publish_decisions': 'accepted',
                                              'close': 'accepted'}

    TRANSITIONS_FOR_ACCEPTING_ITEMS_MEETING_1 = TRANSITIONS_FOR_ACCEPTING_ITEMS_MEETING_2 = ('freeze', 'decide', )

    def _configureFinancesAdvice(self, cfg):
        """ """
        # configure customAdvisers for 'meeting-config-college'
        _configureCollegeCustomAdvisers(self.portal)
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
        # respective _financesXXX groups
        groupsTool.addPrincipalToGroup('pmFinController', '%s_financialcontrollers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinEditor', '%s_financialeditors' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinReviewer', '%s_financialreviewers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinManager', '%s_financialmanagers' % FINANCE_GROUP_ID)

    def _setupPoliceGroup(self):
        '''Configure police group.
           - create 'zone-de-police' group;
           - add 'pmManager' to the _creators group;
           - add some default categories.'''
        # due to complex setup to manage college and council,
        # sometimes this method is called twice...
        if POLICE_GROUP_ID in self.tool.objectIds():
            return

        self.changeUser('siteadmin')
        self.create('MeetingGroup',
                    id=POLICE_GROUP_ID,
                    title="Zone de Police", acronym='ZPL')
        self.create('MeetingGroup',
                    id='groupincharge1',
                    title="Group in charge 1", acronym='GIC1')
        self.create('MeetingGroup',
                    id='groupincharge2',
                    title="Group in charge 2", acronym='GIC2')
        # police is added at the end of existing groups
        self.assertEquals(self.tool.objectIds('MeetingGroup'), ['developers',
                                                                'vendors',
                                                                # disabled
                                                                'endUsers',
                                                                POLICE_GROUP_ID,
                                                                'groupincharge1',
                                                                'groupincharge2'])
        # set groupsInCharge for 'vendors' and 'developers'
        self.tool.get(POLICE_GROUP_ID).setGroupInCharge(
            ({'date_to': '', 'group_id': 'groupincharge1', 'orderindex_': '1'},))
        self.tool.vendors.setGroupInCharge(
            ({'date_to': '', 'group_id': 'groupincharge1', 'orderindex_': '1'},))
        self.tool.developers.setGroupInCharge(
            ({'date_to': '', 'group_id': 'groupincharge2', 'orderindex_': '1'},))
        # make 'pmManager' able to manage everything for 'vendors' and 'police'
        groupsTool = self.portal.portal_groups
        for groupId in ('vendors', POLICE_GROUP_ID):
            for suffix in MEETING_GROUP_SUFFIXES:
                groupsTool.addPrincipalToGroup('pmManager', '{0}_{1}'.format(groupId, suffix))

        # create categories
        for cat in charleroi_import_data.collegeMeeting.categories:
            data = {'id': cat.id,
                    'title': cat.title,
                    'description': cat.description}
            self.create('MeetingCategory', **data)

        self._removeConfigObjectsFor(self.meetingConfig)
        # create itemTemplates
        for template in charleroi_import_data.collegeMeeting.itemTemplates:
            data = {'id': template.id,
                    'title': template.title,
                    'description': template.description,
                    'category': template.category,
                    'proposingGroup': template.proposingGroup == POLICE_GROUP_ID and POLICE_GROUP_ID or 'developers',
                    #'templateUsingGroups': template.templateUsingGroups,
                    'decision': template.decision}
            self.create('MeetingItemTemplate', **data)

    def setupCouncilWorkflows(self):
        """ """
        cfg = getattr(self.tool, 'meeting-config-college')
        cfg.setItemManualSentToOtherMCStates(charleroi_import_data.collegeMeeting.itemManualSentToOtherMCStates)

        cfg2 = getattr(self.tool, 'meeting-config-council')
        # this will especially setup groups in charge, necessary to present items to a Council meeting
        self._setupPoliceGroup()
        cfg2.setWorkflowAdaptations(charleroi_import_data.councilMeeting.workflowAdaptations)
        # items come validated
        cfg2.setTransitionsForPresentingAnItem(('present', ))
        cfg2.setItemReferenceFormat(charleroi_import_data.councilMeeting.itemReferenceFormat)
        # setup inserting methods
        cfg2.setInsertingMethodsOnAddItem(charleroi_import_data.councilMeeting.insertingMethodsOnAddItem)
        cfg2.at_post_edit_script()

    def setupCollegeDemoData(self):
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

        # create items and meetings using demo data
        self.changeUser('pmManager')
        collegeMeeting = _demoData(self.portal, 'pmManager', ('developers', 'vendors'))
        return collegeMeeting

    def setupCouncilDemoData(self):
        """ """
        collegeMeeting = self.setupCollegeDemoData()
        self.setupCouncilWorkflows()
        councilMeeting = _addCouncilDemoData(collegeMeeting, userId='pmManager')
        return councilMeeting
