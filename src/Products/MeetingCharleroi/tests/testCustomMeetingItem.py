# -*- coding: utf-8 -*-
#
# File: testCustomMeetingItem.py
#
# Copyright (c) 2007-2013 by Imio.be
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

from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.MeetingCommunes.tests.testCustomMeetingItem import testCustomMeetingItem as mctcmi
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCharleroi.setuphandlers import _configureCollegeCustomAdvisers
from Products.MeetingCharleroi.setuphandlers import _createFinancesGroup


class testCustomMeetingItem(MeetingCharleroiTestCase, mctcmi):
    """
        Tests the MeetingItem adapted methods
    """
    def test_FinancesAdviserOnlyMayEvaluateCompleteness(self):
        '''Only finances adviser may evaluate completeness when item is 'waiting_advices'.'''
        self.changeUser('admin')
        # configure customAdvisers for 'meeting-config-college'
        _configureCollegeCustomAdvisers(self.portal)
        # add finances group
        _createFinancesGroup(self.portal)
        # put users in finances group
        self._setupFinancesGroup()
        # completeness widget is disabled for items of the config
        cfg = self.meetingConfig
        self.changeUser('siteadmin')
        recurringItem = cfg.getRecurringItems()[0]
        templateItem = cfg.getItemTemplates(as_brains=False)[0]
        self.assertFalse(recurringItem.adapted().mayEvaluateCompleteness())
        self.assertFalse(templateItem.adapted().mayEvaluateCompleteness())
        self.assertFalse(recurringItem.adapted().mayAskCompletenessEvalAgain())
        self.assertFalse(templateItem.adapted().mayAskCompletenessEvalAgain())

        # creator may not evaluate
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        self.assertTrue(item.getCompleteness() == 'completeness_not_yet_evaluated')
        self.assertTrue(self.hasPermission(ModifyPortalContent, item))
        self.assertFalse(item.adapted().mayEvaluateCompleteness())

        # reviewer may not evaluate
        self.proposeItem(item)
        self.changeUser('pmReviewer1')
        self.assertTrue(self.hasPermission(ModifyPortalContent, item))
        self.assertFalse(item.adapted().mayEvaluateCompleteness())

        # not sendable to 'waiting_advices' if finances advice not asked
        self.assertFalse('wait_advices' in self.transitions(item))
        item.setOptionalAdvisers(('dirfin__rowid__2016-05-01.0', ))
        item.at_post_edit_script()
        self.do(item, 'wait_advices_from_prevalidated')
        self.assertFalse(item.adapted().mayEvaluateCompleteness())

        # finances controller is able to evaluate
        self.changeUser('pmFinController')
        self.assertTrue(self.hasPermission(View, item))
        self.assertFalse(item.adapted().mayEvaluateCompleteness())
        itemCompletenessView = item.restrictedTraverse('item-completeness')
        # and even able to change it
        self.assertTrue(itemCompletenessView.listSelectableCompleteness())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeetingItem, prefix='test_'))
    return suite
