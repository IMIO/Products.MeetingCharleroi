# -*- coding: utf-8 -*-
#
# File: testToolPloneMeeting.py
#
# Copyright (c) 2007-2012 by PloneGov
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

from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.PloneMeeting.tests.testToolPloneMeeting import testToolPloneMeeting as pmtt


class testToolPloneMeeting(MeetingCharleroiTestCase, pmtt):
    '''Tests the ToolPloneMeeting class methods.'''

    def test_pm_GetGroupsForUser(self):
        '''getGroupsForUser check in with Plone subgroups a user is and
           returns corresponding MeetingGroups.'''
        self.changeUser('pmManager')
        # pmManager is in every 'developers' Plone groups except 'prereviewers'
        # and in the 'vendors_advisers' Plone group and in the _meetingmanagers groups
        dev = self.meetingConfig.developers
        globalGroups = ['AuthenticatedUsers',
                        '%s_meetingmanagers' % self.meetingConfig.getId(),
                        '%s_meetingmanagers' % self.meetingConfig2.getId()]
        pmManagerGroups = dev.getPloneGroups(idsOnly=True) + ['vendors_advisers', ] + globalGroups
        self.assertTrue(set(self.member.getGroups()) == set(pmManagerGroups))
        self.assertTrue([mGroup.getId() for mGroup in self.tool.getGroupsForUser()] ==
                        ['developers', 'vendors'])
        # check the 'suffix' parameter, it will check that user is in a Plone group of that suffix
        # here, 'pmManager' is only in the '_creators' or 'developers'
        self.assertTrue([mGroup.getId() for mGroup in self.tool.getGroupsForUser(suffixes=['reviewers'])] ==
                        ['developers'])
        # check the 'omittedSuffixes' parameter, it will not consider Plone group having that suffix
        # here, if we omit the 'advisers' suffix, the 'vendors' MeetingGroup will not be returned
        self.assertTrue([mGroup.getId() for mGroup in self.tool.getGroupsForUser(omittedSuffixes=('advisers', ))] ==
                        ['developers'])
        # we can get MeetingGroup for another user
        pmCreator1 = self.portal.portal_membership.getMemberById('pmCreator1')
        self.assertTrue(pmCreator1.getGroups() == ['AuthenticatedUsers', 'developers_creators'])
        self.assertTrue([mGroup.getId() for mGroup in self.tool.getGroupsForUser(userId='pmCreator1')] ==
                        ['developers', ])

        # the 'active' parameter will return only active MeetingGroups
        # so deactivate MeetingGroup 'vendors' and check
        self.changeUser('admin')
        self.do(self.tool.vendors, 'deactivate')
        self.changeUser('pmManager')
        self.assertTrue([mGroup.getId() for mGroup in self.tool.getGroupsForUser(active=True)] ==
                        ['developers', ])
        self.assertTrue([mGroup.getId() for mGroup in self.tool.getGroupsForUser(active=False)] ==
                        ['developers', 'vendors', ])
        self.changeUser('admin')
        self.do(self.tool.vendors, 'activate')
        self.changeUser('pmManager')
        # if we pass a 'zope=True' parameter, it will actually return
        # Plone groups the user is in, no more MeetingGroups
        self.assertTrue(set([group.getId() for group in self.tool.getGroupsForUser(zope=True)]) ==
                        set([group for group in pmManagerGroups if group not in globalGroups]))

    def test_pm_UserIsAmong(self):
        """This method will check if a user has a group that ends with a list of given suffixes.
           This will return True if at least one suffixed group corresponds."""
        self.changeUser('pmCreator1')
        self.assertEqual(self.member.getGroups(),
                         ['AuthenticatedUsers', 'developers_creators'])
        # suffixes parameter must be a list of suffixes
        self.assertFalse(self.tool.userIsAmong('creators'))
        self.assertTrue(self.tool.userIsAmong(['creators']))
        self.assertTrue(self.tool.userIsAmong(['creators', 'reviewers']))
        self.assertTrue(self.tool.userIsAmong(['creators', 'powerobservers']))
        self.assertTrue(self.tool.userIsAmong(['creators', 'unknown_suffix']))
        self.changeUser('pmReviewer1')
        # XXX change for MeetingCharleroi, specific groups
        self.assertEqual(self.member.getGroups(),
                         ['developers_reviewers', 'developers_observers', 'AuthenticatedUsers',
                          'developers_prereviewers', 'developers_serviceheads'])
        self.assertFalse(self.tool.userIsAmong(['creators']))
        self.assertTrue(self.tool.userIsAmong(['reviewers']))
        self.assertTrue(self.tool.userIsAmong(['observers']))
        self.assertTrue(self.tool.userIsAmong(['reviewers', 'observers']))
        # userIsAmong of specific groups
        self.assertTrue(self.tool.userIsAmong(['creators', 'serviceheads']))
        self.assertTrue(self.tool.userIsAmong(['serviceheads']))
        self.changeUser('powerobserver1')
        self.assertEqual(self.member.getGroups(),
                         ['AuthenticatedUsers', '{0}_powerobservers'.format(self.meetingConfig.getId())])
        self.assertFalse(self.tool.userIsAmong(['creators']))
        self.assertFalse(self.tool.userIsAmong(['reviewers']))
        self.assertFalse(self.tool.userIsAmong(['creators', 'reviewers']))
        self.assertTrue(self.tool.userIsAmong(['powerobservers']))
        self.assertTrue(self.tool.userIsAmong(['creators', 'powerobservers']))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testToolPloneMeeting, prefix='test_pm_'))
    return suite
