# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 by Imio.be
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

from Products.PloneMeeting.tests.PloneMeetingTestCase import PloneMeetingTestCase

from Products.MeetingCharleroi.testing import MCH_TESTING_PROFILE_FUNCTIONAL
from Products.MeetingCharleroi.tests.helpers import MeetingCharleroiTestingHelpers


class MeetingCharleroiTestCase(PloneMeetingTestCase, MeetingCharleroiTestingHelpers):
    """Base class for defining MeetingCharleroi test cases."""

    layer = MCH_TESTING_PROFILE_FUNCTIONAL

    def setUp(self):
        PloneMeetingTestCase.setUp(self)
        self.meetingConfig = getattr(self.tool, 'meeting-config-college')
        self.meetingConfig2 = getattr(self.tool, 'meeting-config-council')
