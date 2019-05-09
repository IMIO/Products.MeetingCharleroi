# -*- coding: utf-8 -*-
#
# File: indexes.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from plone.indexer import indexer
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.PluginIndexes.common.UnIndex import _marker
from Products.PloneMeeting.interfaces import IMeetingItem


@indexer(IMeetingItem)
def financesAdviceCategory(item):
    """
      Indexes the 'advice_category' field defined on the contained 'meetingadvicefinances'.
    """
    # finance group could not be present at portal creation (necessary in tests)
    advice = item.getAdviceObj(finance_group_uid())
    if advice and advice.advice_category:
        return advice.advice_category
    return _marker
