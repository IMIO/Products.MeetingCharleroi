# -*- coding: utf-8 -*-
#
# File: indexes.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from plone.indexer import indexer
from Products.PluginIndexes.common.UnIndex import _marker
from Products.PloneMeeting.interfaces import IMeetingItem
from Products.MeetingCharleroi.config import FINANCE_GROUP_ID


@indexer(IMeetingItem)
def financesAdviceCategory(item):
    """
      Indexes the 'advice_category' field defined on the contained 'meetingadvicefinances'.
    """
    advice = item.getAdviceObj(FINANCE_GROUP_ID)
    if advice and advice.advice_category:
        return advice.advice_category
    return _marker
