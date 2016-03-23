# -*- coding: utf-8 -*-
#
# File: testCustomMeeting.py
#
# Copyright (c) 2007-2012 by CommunesPlone.org
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


class testCustomToolPloneMeeting(MeetingCharleroiTestCase):
    """Tests the ToolPloneMeeting adapted methods."""

    def test_GetSpecificAssemblyFor(self):
        """
            This method aimed to ease printings should return formated assembly
        """
        self.changeUser('pmManager')
        m1 = self._createMeetingWithItems()
        m1.setAssembly('Pierre Dupont - Bourgmestre,\n'
                       'Charles Exemple - 1er Echevin,\n'
                       'Echevin Un, Echevin Deux, Echevin Trois - Echevins,\n'
                       'Jacqueline Exemple, Responsable du CPAS')
        attendee = '<p class="mltAssembly">Pierre Dupont - Bourgmestre,<br />' \
                   'Charles Exemple - 1er Echevin,<br />Echevin Un, Echevin Deux, ' \
                   'Echevin Trois - Echevins,<br />Jacqueline Exemple, Responsable du CPAS</p>'
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='')[0],
                          attendee)
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='Absent'),
                          '')
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='Excus'),
                          '')
        m1.setAssembly('Pierre Dupont - Bourgmestre,\n'
                       'Charles Exemple - 1er Echevin,\n'
                       'Echevin Un, Echevin Deux, Echevin Trois - Echevins,\n'
                       'Jacqueline Exemple, Responsable du CPAS \n'
                       'Excusés: \n '
                       'Monsieur x, Mesdames Y et Z')
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='')[0],
                          attendee)
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='Absent'),
                          '')
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='Excus')[0],
                          'Excusés:')
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='Excus')[1],
                          '<p class="mltAssembly">Monsieur x, Mesdames Y et Z</p>')
        m1.setAssembly('Pierre Dupont - Bourgmestre,\n'
                       'Charles Exemple - 1er Echevin,\n'
                       'Echevin Un, Echevin Deux, Echevin Trois - Echevins,\n'
                       'Jacqueline Exemple, Responsable du CPAS \n'
                       'Absent: \n '
                       'Monsieur tartenpion \n'
                       'Excusés: \n '
                       'Monsieur x, Mesdames Y et Z')
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='')[0],
                          attendee)
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='Absent')[0],
                          'Absent:')
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='Absent')[1],
                          '<p class="mltAssembly">Monsieur tartenpion</p>')
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='Excus')[0],
                          'Excusés:')
        self.assertEquals(self.tool.adapted().getSpecificAssemblyFor(m1.getAssembly(),
                                                                     startTxt='Excus')[1],
                          '<p class="mltAssembly">Monsieur x, Mesdames Y et Z</p>')
