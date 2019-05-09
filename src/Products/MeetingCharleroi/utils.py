# -*- coding: utf-8 -*-
#
# File: utils.py
#
# Copyright (c) 2019 by Imio.be
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

from plone.memoize import forever
from Products.MeetingCharleroi.config import FINANCE_GROUP_ID
from Products.PloneMeeting.utils import org_id_to_uid


@forever.memoize
def finance_group_uid(raise_on_error=False):
    """ """
    return org_id_to_uid(FINANCE_GROUP_ID, raise_on_error=raise_on_error)
