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

from DateTime import DateTime
from Products.PloneMeeting.profiles import GroupDescriptor
from Products.MeetingCommunes.tests.testCustomMeeting import testCustomMeeting as mctcm
from Products.MeetingCharleroi.config import POLICE_GROUP_ID
from Products.MeetingCharleroi.setuphandlers import _demoData
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase


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
        # make categories available
        self.setMeetingConfig(self.meetingConfig2.getId())
        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        orderedItems = meeting.getItems(ordered=True)
        itemUids = [item.UID() for item in orderedItems]
        item3 = orderedItems[2]
        item3.setOtherMeetingConfigsClonableTo('meeting-config-council')
        item4 = orderedItems[3]
        item4.setOtherMeetingConfigsClonableTo('meeting-config-council')
        item5 = orderedItems[4]
        item5.setToDiscuss(False)
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=True, itemType='prescriptive')[0]),3)
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=True, itemType='toCouncil')[0]),3)
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=True, itemType='communication')[0]),2)
        # Every item in the meeting is now from the police group
        for item in meeting.getItems():
            item.setProposingGroup('zone-de-police')
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=False, itemType='prescriptive')[0]),3)
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=False, itemType='toCouncil')[0]),3)
        self.assertEqual(len(meeting.adapted().getPrintableItemsForAgenda(itemUids, standard=False, itemType='communication')[0]),2)

    def test_pm_InsertItemOnPoliceThenOtherGroups(self):
        '''Test inserting an item using the "on_police_then_other_groups" sorting method.'''
        self._setupPoliceGroup()
        self.meetingConfig.setInsertingMethodsOnAddItem(
            ({'insertingMethod': 'on_police_then_other_groups',
              'reverse': '0'}, ))

        self.changeUser('pmManager')
        # create items with various groups
        itemDev1 = self.create('MeetingItem')
        itemDev2 = self.create('MeetingItem')
        itemDev3 = self.create('MeetingItem')
        itemVen1 = self.create('MeetingItem', proposingGroup='vendors')
        itemVen2 = self.create('MeetingItem', proposingGroup='vendors')
        itemPol1 = self.create('MeetingItem', proposingGroup=POLICE_GROUP_ID)
        itemPol2 = self.create('MeetingItem', proposingGroup=POLICE_GROUP_ID)
        meeting = self.create('Meeting', date=DateTime())
        for item in [itemDev1, itemDev2, itemDev3,
                     itemVen1, itemVen2,
                     itemPol1, itemPol2, ]:
            self.presentItem(item)

        orderedItems = meeting.getItems(ordered=True)
        self.assertEquals([item.getId() for item in orderedItems],
                          ['o6', 'o7', 'o1', 'o2', 'o3', 'o4', 'o5'])
        self.assertEquals([item.getProposingGroup() for item in orderedItems],
                          ['zone-de-police', 'zone-de-police',
                           'developers', 'developers', 'developers',
                           'vendors', 'vendors'])

    def test_pm_FullInsertingProcess(self):
        '''Test inserting an item using the relevant inserting methods.'''
        self._setupPoliceGroup()
        cfg = self.meetingConfig
        cfg2 = self.meetingConfig2
        cfg2Id = cfg2.getId()
        cfg.setInsertingMethodsOnAddItem(
            (
                {'insertingMethod': 'on_police_then_other_groups', 'reverse': '0'},
                {'insertingMethod': 'on_to_discuss', 'reverse': '0'},
                {'insertingMethod': 'on_other_mc_to_clone_to', 'reverse': '1'},
                {'insertingMethod': 'on_categories', 'reverse': '0'},
                {'insertingMethod': 'on_proposing_groups', 'reverse': '0'},
                )
            )
        cfg.setUseGroupsAsCategories(False)
        # let creators select the 'toDiscuss' value
        cfg.setToDiscussSetOnItemInsert(False)
        cfg.setMeetingConfigsToCloneTo(({'meeting_config': '%s' % cfg2Id,
                                         'trigger_workflow_transitions_until': '__nothing__'},))
        self.changeUser('pmManager')

        # create items and meetings using demo data
        _demoData(self.portal, 'pmManager', ('developers', 'vendors'))
        meeting = cfg.getMeetingsAcceptingItems()[-3].getObject()
        orderedItems = meeting.getItems(ordered=True)
        self.assertEquals(
            [(item.getProposingGroup(),
              item.getToDiscuss(),
              item.getOtherMeetingConfigsClonableTo(),
              item.getCategory()) for item in orderedItems],
            [('zone-de-police', True, (), 'remboursement'),
             ('zone-de-police', True, ('meeting-config-council',), 'affaires-juridiques'),
             ('zone-de-police', True, ('meeting-config-council',), 'remboursement'),
             ('zone-de-police', False, (), 'remboursement'),
             ('zone-de-police', False, ('meeting-config-council',), 'affaires-juridiques'),
             ('developers', True, (), 'remboursement'),
             ('vendors', True, (), 'remboursement'),
             ('developers', True, ('meeting-config-council',), 'affaires-juridiques'),
             ('vendors', True, ('meeting-config-council',), 'affaires-juridiques'),
             ('developers', True, ('meeting-config-council',), 'remboursement'),
             ('vendors', True, ('meeting-config-council',), 'remboursement'),
             ('developers', False, (), 'remboursement'),
             ('vendors', False, (), 'remboursement'),
             ('developers', False, ('meeting-config-council',), 'affaires-juridiques'),
             ('vendors', False, ('meeting-config-council',), 'affaires-juridiques')]
            )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeeting, prefix='test_'))
    return suite
