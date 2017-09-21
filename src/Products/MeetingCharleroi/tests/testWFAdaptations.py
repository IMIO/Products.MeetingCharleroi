# -*- coding: utf-8 -*-
#
# File: testWFAdaptations.py
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

from Products.MeetingCommunes.tests.testWFAdaptations import testWFAdaptations as mctwfa
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCharleroi.setuphandlers import _configureCollegeCustomAdvisers
from Products.MeetingCharleroi.setuphandlers import _createFinancesGroup


class testWFAdaptations(MeetingCharleroiTestCase, mctwfa):
    '''See doc string in PloneMeeting.tests.testWFAdaptations.'''

    def test_pm_WFA_availableWFAdaptations(self):
        '''Test what are the available wfAdaptations.'''
        # we removed the 'archiving' and 'creator_initiated_decisions' wfAdaptations
        self.assertEquals(sorted(self.meetingConfig.listWorkflowAdaptations().keys()),
                          ['charleroi_add_refadmin',
                           'hide_decisions_when_under_writing',
                           'items_come_validated',
                           'mark_not_applicable',
                           'no_global_observation',
                           'no_publication',
                           'only_creator_may_delete',
                           'postpone_next_meeting',
                           'pre_validation',
                           'removed',
                           'removed_and_duplicated',
                           'return_to_proposing_group',
                           'waiting_advices'])

    def test_pm_Validate_workflowAdaptations_added_items_come_validated(self):
        """ """
        # disable some wfAdaptations interferring with the test
        cfg = self.meetingConfig
        cfg.setWorkflowAdaptations(('no_publication', 'no_global_observation'))
        cfg.at_post_edit_script()
        # turn to proposed
        original_proposed_state_mapping_value = self.WF_ITEM_STATE_NAME_MAPPINGS_1['proposed']
        self.WF_ITEM_STATE_NAME_MAPPINGS_1['proposed'] = 'proposed'
        super(testWFAdaptations, self).test_pm_Validate_workflowAdaptations_added_items_come_validated()
        self.WF_ITEM_STATE_NAME_MAPPINGS_1['proposed'] = original_proposed_state_mapping_value

    def test_pm_WFA_pre_validation(self):
        '''Will not work as we have also a state before...
           Tested in testCustomWorkflows.py'''
        pass

    def test_pm_WFA_charleroi_add_refadmin(self):
        '''Test that permissions are correct when the WFA is enabled.'''
        cfg = self.meetingConfig
        self.changeUser('siteadmin')
        cfg.setWorkflowAdaptations(())
        cfg.at_post_edit_script()
        itemWF = self.wfTool.getWorkflowsFor(cfg.getItemTypeName())[0]
        self.assertFalse('proposed_to_refadmin' in itemWF.states)
        # activate, needs the 'pre_validation' WFA
        cfg.setWorkflowAdaptations(('charleroi_add_refadmin', ))
        cfg.at_post_edit_script()
        itemWF = self.wfTool.getWorkflowsFor(cfg.getItemTypeName())[0]
        self.assertFalse('proposed_to_refadmin' in itemWF.states)
        # together with 'pre_validation', it is ok
        cfg.setWorkflowAdaptations(('pre_validation',
                                    'charleroi_add_refadmin', ))
        cfg.at_post_edit_script()
        itemWF = self.wfTool.getWorkflowsFor(cfg.getItemTypeName())[0]
        self.assertTrue('proposed_to_refadmin' in itemWF.states)

    def _waiting_advices_with_prevalidation_active(self):
        '''Enable WFAdaptation 'charleroi_add_refadmin' before executing test.'''
        cfg = self.meetingConfig
        cfg.setWorkflowAdaptations(('pre_validation', 'charleroi_add_refadmin', 'waiting_advices'))
        cfg.at_post_edit_script()
        # put pmReviewerLevel1 in _refadmins group
        self.portal.portal_groups.addPrincipalToGroup('pmReviewerLevel1', 'developers_prereviewers')
        self.portal.REQUEST.set('mayWaitAdvices', True)
        super(testWFAdaptations, self)._waiting_advices_with_prevalidation_active()

    def _setItemToWaitingAdvices(self, item, transition=None):
        """We need to ask finances advice to be able to do the transition."""
        originalMember = self.member.getId()
        self.changeUser('siteadmin')
        # configure customAdvisers for 'meeting-config-college'
        _configureCollegeCustomAdvisers(self.portal)
        # add finances group
        _createFinancesGroup(self.portal)
        # put users in finances group
        self._setupFinancesGroup()
        self.changeUser(originalMember)
        item.setOptionalAdvisers(item.getOptionalAdvisers() +
                                 ('dirfin__rowid__2016-05-01.0', ))
        item.at_post_edit_script()
        if transition:
            self.do(item, transition)

    def test_pm_WFA_waiting_advices_with_prevalidation(self):
        """Override to add 'pmReviewerLevel1' to the 'prereviewers' group."""
        self.portal.portal_groups.addPrincipalToGroup('pmReviewerLevel1', 'developers_prereviewers')
        super(testWFAdaptations, self).test_pm_WFA_waiting_advices_with_prevalidation()

    def _afterItemCreatedWaitingAdviceWithPrevalidation(self, item):
        """ """
        self._setItemToWaitingAdvices(item)

    def _userAbleToBackFromWaitingAdvices(self, currentState):
        """Return username able to back from waiting advices."""
        if currentState == 'prevalidated_waiting_advices':
            return 'pmManager'
        else:
            return super(testWFAdaptations, self)._userAbleToBackFromWaitingAdvices(currentState)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix='test_pm_'))
    return suite
