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

from Products.PloneMeeting.tests.testWFAdaptations import testWFAdaptations as pmtwfa
from Products.MeetingCommunes.tests.MeetingCommunesTestCase import MeetingCommunesTestCase


class testWFAdaptations(MeetingCommunesTestCase, pmtwfa):
    '''See doc string in PloneMeeting.tests.testWFAdaptations.'''

    def test_pm_WFA_availableWFAdaptations(self):
        '''Test what are the available wfAdaptations.'''
        # we removed the 'archiving' and 'creator_initiated_decisions' wfAdaptations
        self.assertEquals(set(self.meetingConfig.listWorkflowAdaptations()),
                          set(('creator_edits_unless_closed',
                               'everyone_reads_all',
                               'hide_decisions_when_under_writing',
                               'items_come_validated',
                               'no_global_observation',
                               'no_proposal',
                               'no_publication',
                               'only_creator_may_delete',
                               'pre_validation',
                               'pre_validation_keep_reviewer_permissions',
                               'return_to_proposing_group',
                               )))

    def test_pm_validate_workflowAdaptations_added_no_publication(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        # we have a 'published' state in self.meetingConfig2
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_validate_workflowAdaptations_added_no_publication()

    def test_pm_WFA_no_publication(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        # we have a 'published' state in self.meetingConfig2
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_WFA_no_publication()

    def test_pm_WFA_no_proposal(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        super(testWFAdaptations, self).test_pm_WFA_no_proposal()
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_WFA_no_proposal()

    def test_pm_WFA_pre_validation(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        super(testWFAdaptations, self).test_pm_WFA_pre_validation()
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_WFA_pre_validation()

    def test_pm_WFA_pre_validation_keep_reviewer_permissions(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        super(testWFAdaptations, self).test_pm_WFA_pre_validation_keep_reviewer_permissions()
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_WFA_pre_validation_keep_reviewer_permissions()

    def test_pm_WFA_creator_initiated_decisions(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py
           In MC WFs this wfAdaptation is not used (deactivated in adapters.py) because it is
           always 'enabled', the creator can edit the decision field by default.'''
        # we just call the subtest while wfAdaptation should be active
        super(testWFAdaptations, self)._creator_initiated_decisions_active()

    def test_pm_WFA_items_come_validated(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        super(testWFAdaptations, self).test_pm_WFA_items_come_validated()
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_WFA_items_come_validated()

    def test_pm_WFA_archiving(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        # we do not have an 'archived' state in the meeting/item WFs...
        # just call the subtest while wfAdaptation sould be inactive
        # it is deactived in adapters.py
        super(testWFAdaptations, self)._archiving_inactive()

    def test_pm_WFA_only_creator_may_delete(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        super(testWFAdaptations, self).test_pm_WFA_only_creator_may_delete()
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_WFA_only_creator_may_delete()

    def test_pm_WFA_no_global_observation(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        # we have a 'published' state in self.meetingConfig2
        # once item is 'itempublished'
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_WFA_no_global_observation()

    def test_pm_WFA_everyone_reads_all(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_WFA_everyone_reads_all()

    def test_pm_WFA_creator_edits_unless_closed(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        super(testWFAdaptations, self).test_pm_WFA_creator_edits_unless_closed()
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_WFA_creator_edits_unless_closed()

    def test_pm_WFA_return_to_proposing_group(self):
        '''See doc in PloneMeeting/tests/testWFAdaptations.py'''
        self.meetingConfig = self.meetingConfig2
        super(testWFAdaptations, self).test_pm_WFA_return_to_proposing_group()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix='test_pm_'))
    return suite
