# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 by Imio.be
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

from Products.MeetingCharleroi.testing import MCH_TESTING_PROFILE_FUNCTIONAL
from Products.MeetingCharleroi.tests.helpers import MeetingCharleroiTestingHelpers
from Products.MeetingCommunes.tests.MeetingCommunesTestCase import MeetingCommunesTestCase


class MeetingCharleroiTestCase(MeetingCommunesTestCase, MeetingCharleroiTestingHelpers):
    """Base class for defining MeetingCharleroi test cases."""
    subproductIgnoredTestFiles = ['test_robot.py', 'testPerformances.py', 'testContacts.py', 'testVotes.py']

    layer = MCH_TESTING_PROFILE_FUNCTIONAL
