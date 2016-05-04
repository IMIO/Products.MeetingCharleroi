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
        self.assertEquals(set(self.meetingConfig.listWorkflowAdaptations()),
                          set(('no_global_observation',
                               'no_publication',
                               'pre_validation',
                               'return_to_proposing_group',
                               'waiting_advices',
                               'charleroi_add_refadmin',
                               )))

    def test_subproduct_call_WFA_no_publication(self):
        '''No sense...'''
        pass

    def test_subproduct_call_WFA_items_come_validated(self):
        '''No sense...'''
        pass

    def test_subproduct_call_WFA_only_creator_may_delete(self):
        '''No sense...'''
        pass

    def test_subproduct_call_WFA_everyone_reads_all(self):
        '''No sense...'''
        pass

    def test_subproduct_call_WFA_creator_edits_unless_closed(self):
        '''No sense...'''
        pass

    def test_subproduct_call_WFA_add_published_state(self):
        '''No sense...tested in customWorkflow with ref-admin-wfa'''
        pass

    def test_pm_WFA_pre_validation(self):
        '''No sense...'''
        pass

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
        item.setOptionalAdvisers(('dirfin__rowid__2016-05-01.0', ))
        item.at_post_edit_script()
        if transition:
            self.do(item, transition)

    def _afterItemCreatedWaitingAdviceWithPrevalidation(self, item):
        """ """
        self._setItemToWaitingAdvices(item)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix='test_pm_'))
    return suite
