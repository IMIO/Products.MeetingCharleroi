# -*- coding: utf-8 -*-
#
# File: testMeetingConfig.py
#
# Copyright (c) 2015 by Imio.be
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
from Products.MeetingCommunes.tests.testSearches import testSearches as mcts

from zope.component import getAdapter
from collective.compoundcriterion.interfaces import ICompoundCriterionFilter
from Products.PloneMeeting.config import MEETINGREVIEWERS


class testSearches(MeetingCharleroiTestCase, mcts):
    """Test searches."""

    def test_pm_SearchItemsToValidateOfEveryReviewerLevelsAndLowerLevels(self):
        '''Test the searchItemsToValidateOfEveryReviewerLevelsAndLowerLevels method.
           This will return items to validate of his highest hierarchic level and every levels
           under, even if user is not in the corresponding Plone reviewer groups.'''
        cfg = self.meetingConfig
        itemTypeName = cfg.getItemTypeName()
        # create 2 items
        self.changeUser('pmCreator1')
        item1 = self.create('MeetingItem')
        item2 = self.create('MeetingItem')
        self.do(item1, self.TRANSITIONS_FOR_PROPOSING_ITEM_1[0])
        self.do(item2, self.TRANSITIONS_FOR_PROPOSING_ITEM_1[0])
        adapter = getAdapter(cfg,
                             ICompoundCriterionFilter,
                             name='items-to-validate-of-every-reviewer-levels-and-lower-levels')
        self.assertEquals(adapter.query,
                          {'review_state': {'query': ['unknown_review_state']}})
        # now do the query
        # this adapter is not used by default, but is intended to be used with
        # the "searchitemstovalidate" collection so use it with it
        collection = cfg.searches.searches_items.searchitemstovalidate
        patchedQuery = list(collection.query)
        patchedQuery[0]['v'] = 'items-to-validate-of-every-reviewer-levels-and-lower-levels'
        collection.query = patchedQuery
        self.failIf(collection.getQuery())
        # as first level user, he will see items
        self.changeUser('pmReviewerLevel1')
        # find state to use for current reviewer
        reviewer_state = MEETINGREVIEWERS[cfg._highestReviewerLevel(self.member.getGroups())]
        self.assertEquals(adapter.query,
                          {'portal_type': {'query': itemTypeName},
                           'reviewProcessInfo': {'query': ['developers__reviewprocess__%s' % reviewer_state]}})

        self.failUnless(len(collection.getQuery()) == 2)
        # as second level user, he will not see items because items are from lower reviewer levels
        self.changeUser('pmReviewerLevel2')
        self.failUnless(len(collection.getQuery()) == 0)

        # now propose item1, both items are viewable to 'pmReviewerLevel2', but 'pmReviewerLevel1'
        # will only see item of 'his' highest hierarchic level
        self.proposeItem(item1)
        self.failUnless(len(collection.getQuery()) == 1)
        self.changeUser('pmReviewerLevel1')
        self.failUnless(len(collection.getQuery()) == 1)
        self.failUnless(collection.getQuery()[0].UID == item2.UID())

    def test_pm_SearchItemsToValidateOfHighestHierarchicLevel(self):
        '''Test the searchItemsToValidateOfHighestHierarchicLevel method.
           This should return a list of items a user ***really*** has to validate.
           Items to validate are items for which user is a reviewer and only regarding
           his higher hierarchic level.
           So a reviewer level 1 and level 2 will only see items in level 2, a reviewer in level
           1 (only) will only see items in level 1.'''
        self.changeUser('admin')
        cfg = self.meetingConfig
        itemTypeName = cfg.getItemTypeName()

        # first test the generated query
        adapter = getAdapter(cfg,
                             ICompoundCriterionFilter,
                             name='items-to-validate-of-highest-hierarchic-level')
        # if user si not a reviewer, we want the search to return
        # nothing so the query uses an unknown review_state
        self.assertEquals(adapter.query,
                          {'review_state': {'query': ['unknown_review_state']}})
        # for a reviewer, query is correct
        self.changeUser('pmManager')
        self.assertEquals(adapter.query,
                          {'getProposingGroup': {'query': ['developers']},
                           'portal_type': {'query': itemTypeName},
                           'review_state': {'query': self.WF_STATE_NAME_MAPPINGS['proposed']}})

        # now do the query
        # this adapter is used by the "searchitemstovalidate"
        collection = cfg.searches.searches_items.searchitemstovalidate
        # create an item
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        # jump to first level of validation
        self.do(item, self.TRANSITIONS_FOR_PROPOSING_ITEM_1[0])
        self.failIf(collection.getQuery())
        self.changeUser('pmReviewerLevel1')
        self.failUnless(collection.getQuery())
        # now as 'pmReviewerLevel2', the item should not be returned
        # as he only see items of his highest hierarchic level
        self.changeUser('pmReviewerLevel2')
        self.failIf(collection.getQuery())
        # pass the item to second last level of hierarchy, where 'pmReviewerLevel2' is reviewer for
        self.changeUser('pmReviewerLevel1')
        # jump to last level of validation
        self.proposeItem(item)
        self.failIf(collection.getQuery())
        self.changeUser('pmReviewerLevel2')
        self.failUnless(collection.getQuery())

        # now give a view on the item by 'pmReviewer2' and check if, as a reviewer,
        # the search does returns him the item, it should not as he is just a reviewer
        # but not able to really validate the new item
        cfg.setUseCopies(True)
        review_states = MEETINGREVIEWERS[MEETINGREVIEWERS.keys()[0]]
        if 'prereviewers' in MEETINGREVIEWERS:
            review_states = ('prevalidated',)
        cfg.setItemCopyGroupsStates(review_states)
        item.setCopyGroups(('vendors_reviewers',))
        item.at_post_edit_script()
        self.changeUser('pmReviewer2')
        # the user can see the item
        self.failUnless(self.hasPermission('View', item))
        # but the search will not return it
        self.failIf(collection.getQuery())
        # if the item is validated, it will not appear for pmReviewer1 anymore
        self.changeUser('pmReviewer1')
        self.failUnless(collection.getQuery())
        self.validateItem(item)
        self.failIf(collection.getQuery())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSearches, prefix='test_'))
    return suite
