# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 by Imio.be
#
# GNU General Public License (GPL)
#

from Products.MeetingCommunes.tests.helpers import MeetingCommunesTestingHelpers


class MeetingCharleroiTestingHelpers(MeetingCommunesTestingHelpers):
    '''Stub class that provides some helper methods about testing.'''

    WF_ITEM_STATE_NAME_MAPPINGS_1 = {
        'itemcreated': 'itemcreated',
        'proposed_first_level': 'proposed',
        # prevalidation always enabled
        'proposed': 'prevalidated',
        'prevalidated': 'prevalidated',
        'validated': 'validated',
        'presented': 'presented',
        'itemfrozen': 'itemfrozen'}
    WF_ITEM_STATE_NAME_MAPPINGS_2 = WF_ITEM_STATE_NAME_MAPPINGS_1
