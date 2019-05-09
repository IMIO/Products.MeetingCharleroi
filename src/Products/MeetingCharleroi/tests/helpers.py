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

from collective.contact.plonegroup.utils import get_all_suffixes
from collective.contact.plonegroup.utils import get_organizations
from collective.contact.plonegroup.utils import select_org_for_function
from copy import deepcopy
from plone import api
from plone.memoize.forever import _memos
from Products.MeetingCharleroi.config import POLICE_GROUP_PREFIX
from Products.MeetingCharleroi.config import PROJECTNAME
from Products.MeetingCharleroi.profiles.zcharleroi import import_data as charleroi_import_data
from Products.MeetingCharleroi.setuphandlers import _addCouncilDemoData
from Products.MeetingCharleroi.setuphandlers import _configureCollegeCustomAdvisers
from Products.MeetingCharleroi.setuphandlers import _demoData
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.PloneMeeting.exportimport.content import ToolInitializer
from Products.PloneMeeting.tests.helpers import PloneMeetingTestingHelpers
from Products.PloneMeeting.utils import org_id_to_uid


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
        # add finances group
        self._createFinancesGroup()
        # put users in finances group
        self._setupFinancesGroup()
        # configure customAdvisers for 'meeting-config-college'
        _configureCollegeCustomAdvisers(self.portal)
        cfg.setTransitionsReinitializingDelays(
            charleroi_import_data.collegeMeeting.transitionsReinitializingDelays)
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

    def _createFinancesGroup(self):
        """
           Create the finances group.
        """
        context = self.portal.portal_setup._getImportContext('Products.MeetingCharleroi:testing')
        initializer = ToolInitializer(context, PROJECTNAME)
        # create echevin2 first as it is a group in charge of finances org
        orgs, active_orgs, savedOrgsData = initializer.addOrgs([charleroi_import_data.ech2_grp])
        for org in orgs:
            org_uid = org.UID()
            self._select_organization(org_uid)

        dirfin_grp = deepcopy(charleroi_import_data.dirfin_grp)
        dirfin_grp.groups_in_charge = [org_id_to_uid(group_in_charge_id)
                                       for group_in_charge_id in dirfin_grp.groups_in_charge]

        orgs, active_orgs, savedOrgsData = initializer.addOrgs([dirfin_grp])
        for org in orgs:
            org_uid = org.UID()
            self._select_organization(org_uid)
            select_org_for_function(org_uid, 'financialcontrollers')
            select_org_for_function(org_uid, 'financialeditors')
            select_org_for_function(org_uid, 'financialmanagers')
            select_org_for_function(org_uid, 'financialreviewers')
        # clean forever cache on utils finance_group_uid
        _memos.clear()

    def _setupFinancesGroup(self):
        '''Configure finances group.'''
        groupsTool = api.portal.get_tool('portal_groups')
        # add finances users to relevant groups
        # _advisers
        groupsTool.addPrincipalToGroup('pmFinController', '{0}_advisers'.format(finance_group_uid()))
        groupsTool.addPrincipalToGroup('pmFinEditor', '{0}_advisers'.format(finance_group_uid()))
        groupsTool.addPrincipalToGroup('pmFinReviewer', '{0}_advisers'.format(finance_group_uid()))
        groupsTool.addPrincipalToGroup('pmFinManager', '{0}_advisers'.format(finance_group_uid()))
        groupsTool.addPrincipalToGroup('dfin', '{0}_advisers'.format(finance_group_uid()))
        # respective _financesXXX groups
        groupsTool.addPrincipalToGroup('pmFinController', '{0}_financialcontrollers'.format(finance_group_uid()))
        groupsTool.addPrincipalToGroup('pmFinEditor', '{0}_financialeditors'.format(finance_group_uid()))
        groupsTool.addPrincipalToGroup('pmFinReviewer', '{0}_financialreviewers'.format(finance_group_uid()))
        groupsTool.addPrincipalToGroup('pmFinManager', '{0}_financialmanagers'.format(finance_group_uid()))
        # dfin is member of every finances groups
        groupsTool.addPrincipalToGroup('dfin', '{0}_financialcontrollers'.format(finance_group_uid()))
        groupsTool.addPrincipalToGroup('dfin', '{0}_financialeditors'.format(finance_group_uid()))
        groupsTool.addPrincipalToGroup('dfin', '{0}_financialreviewers'.format(finance_group_uid()))
        groupsTool.addPrincipalToGroup('dfin', '{0}_financialmanagers'.format(finance_group_uid()))

    def _setupPoliceGroup(self):
        '''Configure police group.
           - create 'bourgmestre' group as in charge of police groups;
           - create police/police_compta groups;
           - add 'pmManager' to the _creators group;
           - add some default categories.'''
        # due to complex setup to manage college and council,
        # sometimes this method is called twice...
        if POLICE_GROUP_PREFIX in get_organizations(the_objects=False):
            return

        self.changeUser('siteadmin')
        context = self.portal.portal_setup._getImportContext('Products.MeetingCharleroi:testing')
        initializer = ToolInitializer(context, PROJECTNAME)
        # create bourgmestre first as it is a group in charge of police orgs
        orgs, active_orgs, savedOrgsData = initializer.addOrgs([charleroi_import_data.bourg_grp])
        bourg_grp = orgs[0]
        for org in orgs:
            org_uid = org.UID()
            self._select_organization(org_uid)

        # groups_in_charge are organziation ids, we need organization uids
        police_grp = deepcopy(charleroi_import_data.police_grp)
        police_grp.groups_in_charge = [org_id_to_uid(group_in_charge_id)
                                       for group_in_charge_id in police_grp.groups_in_charge]
        police_compta_grp = deepcopy(charleroi_import_data.police_compta_grp)
        police_compta_grp.groups_in_charge = [org_id_to_uid(group_in_charge_id)
                                              for group_in_charge_id in police_compta_grp.groups_in_charge]
        org_descriptors = (police_grp, police_compta_grp)
        orgs, active_orgs, savedOrgsData = initializer.addOrgs(org_descriptors, defer_data=False)
        for org in orgs:
            org_uid = org.UID()
            self._select_organization(org_uid)

        police = orgs[0]
        police_compta = orgs[1]
        gic1 = self.create('organization', id='groupincharge1', title="Group in charge 1", acronym='GIC1')
        self._select_organization(gic1.UID())
        gic2 = self.create('organization', id='groupincharge2', title="Group in charge 2", acronym='GIC2')
        self._select_organization(gic2.UID())
        # police is added at the end of existing groups
        self.assertEquals(get_organizations(the_objects=False),
                          [self.developers_uid, self.vendors_uid,
                           bourg_grp.UID(),
                           police.UID(), police_compta.UID(),
                           gic1.UID(), gic2.UID()])
        # set groupsInCharge for police groups
        police.groups_in_charge = ('groupincharge1',)
        police_compta.groups_in_charge = ('groupincharge1',)
        self.vendors.groups_in_charge = ('groupincharge1',)
        self.developers.groups_in_charge = ('groupincharge2',)
        # make 'pmManager' able to manage everything for 'vendors' and 'police'
        groupsTool = self.portal.portal_groups
        for org in (self.vendors, police, police_compta):
            org_uid = org.UID()
            for suffix in get_all_suffixes(org_uid):
                groupsTool.addPrincipalToGroup('pmManager', '{0}_{1}'.format(org_uid, suffix))

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
        existing = [cat.getId() for cat in self.meetingConfig.getCategories(onlySelectable=False)]
        for cat in categories:
            if cat.id not in existing:
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
        self.changeUser('siteadmin')
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
        self._createCategories()

    def setupCollegeConfig(self):
        """ """
        cfg = self.meetingConfig

        self._setupPoliceGroup()
        self._configureFinancesAdvice(cfg)
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
        self._createItemTemplates()
        self._createRecurringItems()
        self.setupCouncilConfig()
        councilMeeting = _addCouncilDemoData(collegeMeeting,
                                             collegeExtraMeeting,
                                             userId='pmManager',
                                             firstTwoGroupIds=('developers', 'vendors'))
        self.setMeetingConfig(current_cfg.getId())
        return councilMeeting
