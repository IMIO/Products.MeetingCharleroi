# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 by Imio.be
#
# GNU General Public License (GPL)
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
from Products.MeetingCharleroi.setuphandlers import _demoData
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.MeetingCommunes.tests.helpers import MeetingCommunesTestingHelpers
from Products.PloneMeeting.exportimport.content import ToolInitializer
from Products.PloneMeeting.utils import org_id_to_uid


class MeetingCharleroiTestingHelpers(MeetingCommunesTestingHelpers):
    '''Stub class that provides some helper methods about testing.'''

    TRANSITIONS_FOR_PROPOSING_ITEM_FIRST_LEVEL_1 = TRANSITIONS_FOR_PROPOSING_ITEM_FIRST_LEVEL_2 = ('propose',
                                                                                                   'proposeToRefAdmin')
    TRANSITIONS_FOR_PUBLISHING_MEETING_1 = TRANSITIONS_FOR_PUBLISHING_MEETING_2 = ('freeze', 'publish', )
    TRANSITIONS_FOR_FREEZING_MEETING_1 = TRANSITIONS_FOR_FREEZING_MEETING_2 = ('freeze', )
    TRANSITIONS_FOR_DECIDING_MEETING_1 = TRANSITIONS_FOR_DECIDING_MEETING_2 = ('freeze', 'publish', 'decide')
    TRANSITIONS_FOR_CLOSING_MEETING_1 = TRANSITIONS_FOR_CLOSING_MEETING_2 = ('freeze',
                                                                             'publish',
                                                                             'decide',
                                                                             'close', )

    TRANSITIONS_FOR_PROPOSING_ITEM_1 = ('propose',
                                         'proposeToRefAdmin',
                                         'prevalidate',
                                        )

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
