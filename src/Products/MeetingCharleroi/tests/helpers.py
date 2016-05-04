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
from Products.PloneMeeting.tests.helpers import PloneMeetingTestingHelpers
from Products.MeetingCharleroi.config import FINANCE_GROUP_ID


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

    def _setupFinancesGroup(self):
        '''Configure finances group.'''
        groupsTool = api.portal.get_tool('portal_groups')
        # add pmFinController, pmFinReviewer and pmFinManager to advisers and to their respective finance group
        groupsTool.addPrincipalToGroup('pmFinController', '%s_advisers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinReviewer', '%s_advisers' % FINANCE_GROUP_ID)
        groupsTool.addPrincipalToGroup('pmFinManager', '%s_advisers' % FINANCE_GROUP_ID)
