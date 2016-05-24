# -*- coding: utf-8 -*-
#
# File: testCustomMeeting.py
#
# Copyright (c) 2007-2013 by Imio.be
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
from Products.MeetingCommunes.tests.testCustomMeeting import testCustomMeeting as mctcm
from Products.PloneMeeting.profiles import GroupDescriptor


class testCustomMeeting(MeetingCharleroiTestCase, mctcm):
    """
        Tests the Meeting adapted methods
    """

    def test_GetPrintableItemsByCategoryWithBothLateItems(self):
        self.changeUser('pmManager')
        self.setMeetingConfig(self.meetingConfig2.getId())
        meeting = self._createMeetingWithItems()
        orderedItems = meeting.getItems(ordered=True)
        item1 = orderedItems[0]
        item2 = orderedItems[1]
        item3 = orderedItems[2]
        self.do(item1, 'backToValidated')
        self.do(item1, 'backToProposed')
        self.do(item2, 'backToValidated')
        self.do(item2, 'backToProposed')
        self.do(item3, 'backToValidated')
        self.do(item3, 'backToProposed')
        self.freezeMeeting(meeting)
        item1.setPreferredMeeting(meeting.UID())
        item2.setPreferredMeeting(meeting.UID())
        item3.setPreferredMeeting(meeting.UID())
        self.presentItem(item1)
        self.presentItem(item2)
        self.presentItem(item3)
        # now we have 2 normal items and 3 late items
        # 2 lates development, 1 normal and 1 late events
        # and 1 normal research
        # build the list of uids
        itemUids = [anItem.UID() for anItem in meeting.getItems(ordered=True)]
        # test on the meeting with listTypes=['late','normal']
        # Every items (normal and late) should be in the same category, in the good order
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[0][0].getId(),
                          'development')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[1][0].getId(),
                          'events')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[2][0].getId(),
                          'research')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[0][0].meta_type,
                          'MeetingCategory')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[1][0].meta_type,
                          'MeetingCategory')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[2][0].meta_type,
                          'MeetingCategory')
        # the event category should have 2 items, research 1 and development 2 ( + 1 category element for each one)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                            listTypes=['late', 'normal'])[0]),
                          3)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                            listTypes=['late', 'normal'])[1]),
                          3)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                            listTypes=['late', 'normal'])[2]),
                          2)
        # other element of the list are MeetingItems...
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[0][1].meta_type,
                          'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[0][2].meta_type,
                          'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[1][1].meta_type,
                          'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[1][2].meta_type,
                          'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                        listTypes=['late', 'normal'])[2][1].meta_type,
                          'MeetingItem')

    def test_GetNumberOfItems(self):
        """
          This method will return a certain number of items depending on passed paramaters.
        """
        self.changeUser('admin')
        # make categories available
        self.setMeetingConfig(self.meetingConfig2.getId())
        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        orderedItems = meeting.getItems(ordered=True)
        # the meeting is created with 5 items
        self.assertEquals(len(orderedItems), 5)
        itemUids = [item.UID() for item in orderedItems]
        # without parameters, every items are returned
        self.assertEquals(meeting.adapted().getNumberOfItems(itemUids), 5)

        # test the 'privacy' parameter
        # by default, 2 items are 'secret' and 3 are 'public'
        itemPrivacies = [item.getPrivacy() for item in orderedItems]
        self.assertEquals(itemPrivacies.count('secret'), 2)
        self.assertEquals(itemPrivacies.count('public'), 3)
        # same using getNumberOfItems
        self.assertEquals(meeting.adapted().getNumberOfItems(itemUids, privacy='secret'), 2)
        self.assertEquals(meeting.adapted().getNumberOfItems(itemUids, privacy='public'), 3)

        # test the 'categories' parameter
        # by default, 2 items are in the 'events' category,
        # 2 are in the 'development' category
        # 1 in the 'research' category
        itemCategories = [item.getCategory() for item in orderedItems]
        self.assertEquals(itemCategories.count('events'), 2)
        self.assertEquals(itemCategories.count('development'), 2)
        self.assertEquals(itemCategories.count('research'), 1)
        # same using getNumberOfItems
        self.assertEquals(meeting.adapted().getNumberOfItems(itemUids, categories=['events', ]), 2)
        self.assertEquals(meeting.adapted().getNumberOfItems(itemUids, categories=['development', ]), 2)
        # we can pass several categories
        self.assertEquals(meeting.adapted().getNumberOfItems(itemUids,
                                                             categories=['dummycategory', 'research', 'development', ]),
                          3)

        # test the 'late' parameter
        # by default, no items are late so make 2 late items
        # remove to items, freeze the meeting then add the items
        item1 = orderedItems[0]
        item2 = orderedItems[1]
        self.do(item1, 'backToValidated')
        self.do(item1, 'backToProposed')
        self.do(item2, 'backToValidated')
        self.do(item2, 'backToProposed')
        self.freezeMeeting(meeting)
        item1.setPreferredMeeting(meeting.UID())
        item2.setPreferredMeeting(meeting.UID())
        self.presentItem(item1)
        self.presentItem(item2)
        # now we have 4 normal items and 2 late items
        self.assertEquals(len(meeting.getItems()), 5)
        self.assertEquals(len(meeting.getItems(listTypes=['late'])), 2)
        # same using getNumberOfItems
        self.assertEquals(meeting.adapted().getNumberOfItems(itemUids, listTypes=['normal']), 3)
        self.assertEquals(meeting.adapted().getNumberOfItems(itemUids, listTypes=['late']), 2)

        # we can combinate parameters
        # we know that we have 2 late items that are using the 'development' category...
        lateItems = meeting.getItems(listTypes=['late'])
        self.assertEquals(len(lateItems), 2)
        self.assertEquals(lateItems[0].getCategory(), 'development')
        self.assertEquals(lateItems[1].getCategory(), 'development')
        self.assertEquals(meeting.adapted().getNumberOfItems(itemUids, categories=['development', ],
                                                             listTypes=['late']), 2)
        # we have so 0 normal item using the 'development' category
        self.assertEquals(meeting.adapted().getNumberOfItems(itemUids, categories=['development', ],
                                                             listTypes=['normal']), 0)

    def test_GetPrintableItemsForAgenda(self):
        '''
        Return the items for agenda.
        '''
        self.changeUser('admin')
        police = GroupDescriptor('zone-de-police', 'Police', 'La police.')
        # make categories available
        self.setMeetingConfig(self.meetingConfig2.getId())
        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        orderedItems = meeting.getItems(ordered=True)
        itemUids = [item.UID() for item in orderedItems]
        item1 = orderedItems[0]
        item1.setToDiscuss(False)
        item2 = orderedItems[1]
        item2.setToDiscuss(False)
        item3 = orderedItems[2]
        item3.setToDiscuss(False)
        item3.setOtherMeetingConfigsClonableTo('meeting-config-council')
        item4 = orderedItems[3]
        item4.setToDiscuss(False)
        item4.setOtherMeetingConfigsClonableTo('meeting-config-council')
        item5 = orderedItems[4]
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=True, itemType='prescriptive')[0]),3)
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=True, itemType='toCouncil')[0]),3)
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=True, itemType='communication')[0]),2)
        # Every item in the meeting is now from the police group
        for item in meeting.getItems():
            item.setProposingGroup('zone-de-police')
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=False, itemType='prescriptive')[0]),3)
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=False, itemType='toCouncil')[0]),3)
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=False, itemType='communication')[0]),2)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeeting, prefix='test_'))
    return suite
