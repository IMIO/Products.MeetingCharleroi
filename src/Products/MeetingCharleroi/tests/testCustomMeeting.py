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
from Products.MeetingCommunes.tests.testCustomMeeting import testCustomMeeting as mctcm
from Products.MeetingCharleroi.config import COMMUNICATION_CAT_ID
from Products.MeetingCharleroi.config import POLICE_GROUP_ID
from Products.MeetingCharleroi.setuphandlers import _demoData
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase

from plone import api

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
        return
        pm = api.portal.get_tool('portal_plonemeeting')
        self.changeUser('admin')
        # make categories available
        self.meetingConfig.setUseGroupsAsCategories(False)
        self._setupPoliceGroup()
        # find groups in charge within meeting groups.
        for group in pm.getMeetingGroups():
            groupId = group.getId()
            if groupId == 'groupincharge1':
                gic1 = group
            elif groupId == 'groupincharge2':
                gic2 = group
        # get the categories needed to complete the tests.
        develCat = self.meetingConfig.categories.get('development')
        eventsCat = self.meetingConfig.categories.get('events')
        researchCat = self.meetingConfig.categories.get('research')
        commuCat = self.meetingConfig.categories.get('communication')

        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        # switch to council
        self.setMeetingConfig(self.meetingConfig2.getId())

        meetingCouncil = self._createMeetingWithItems(withItems=False, meetingDate=DateTime()+1)
        meetingCouncil2 = self._createMeetingWithItems(withItems=False, meetingDate=DateTime()+30)
        meetingCouncilUID = meetingCouncil.UID()
        meetingCouncilUID2 = meetingCouncil2.UID()

        self.setMeetingConfig(self.meetingConfig.getId())

        # item late
        itemLate = self.create('MeetingItem')
        itemLate.setProposingGroup('vendors')
        itemLate.setAssociatedGroups(('developers',))
        itemLate.setCategory('research')
        itemLate.setListType('late')
        self.presentItem(itemLate)

        # item depose
        itemDepo = self.create('MeetingItem')
        itemDepo.setProposingGroup('vendors')
        itemDepo.setAssociatedGroups(('developers',))
        itemDepo.setCategory('research')
        self.presentItem(itemDepo)
        itemDepo.setListType('depose')

        # item council "emergency" to next meeting
        itemNextCouncil = self.create('MeetingItem')
        itemNextCouncil.setProposingGroup('vendors')
        itemNextCouncil.setAssociatedGroups(('developers',))
        itemNextCouncil.setCategory('research')
        itemNextCouncil.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNextCouncil.setPreferredMeeting(meetingCouncilUID)
        self.presentItem(itemNextCouncil)

        # item council "emergency" to next meeting late
        itemNCLate = self.create('MeetingItem')
        itemNCLate.setProposingGroup('vendors')
        itemNCLate.setAssociatedGroups(('developers',))
        itemNCLate.setCategory('research')
        itemNCLate.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNCLate.setPreferredMeeting(meetingCouncilUID)
        itemNCLate.setListType('late')
        self.presentItem(itemNCLate)

        # item council "emergency" to next meeting depose
        itemNCDepose = self.create('MeetingItem')
        itemNCDepose.setProposingGroup('vendors')
        itemNCDepose.setAssociatedGroups(('developers',))
        itemNCDepose.setCategory('research')
        itemNCDepose.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNCDepose.setPreferredMeeting(meetingCouncilUID)
        itemNCDepose.setListType('depose')
        self.presentItem(itemNCDepose)

        # item council to next month meeting
        itemNextMonthCouncil = self.create('MeetingItem')
        itemNextMonthCouncil.setProposingGroup('vendors')
        itemNextMonthCouncil.setAssociatedGroups(('developers',))
        itemNextMonthCouncil.setCategory('research')
        itemNextMonthCouncil.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNextMonthCouncil.setPreferredMeeting(meetingCouncilUID2)
        self.presentItem(itemNextMonthCouncil)

        # item council to next month meeting late
        itemNMCLate = self.create('MeetingItem')
        itemNMCLate.setProposingGroup('vendors')
        itemNMCLate.setAssociatedGroups(('developers',))
        itemNMCLate.setCategory('research')
        itemNMCLate.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNMCLate.setPreferredMeeting(meetingCouncilUID2)
        itemNMCLate.setListType('late')
        self.presentItem(itemNMCLate)

        # item council to next month meeting depose
        itemNMCDepose = self.create('MeetingItem')
        itemNMCDepose.setProposingGroup('vendors')
        itemNMCDepose.setAssociatedGroups(('developers',))
        itemNMCDepose.setCategory('research')
        itemNMCDepose.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNMCDepose.setPreferredMeeting(meetingCouncilUID2)
        itemNMCDepose.setListType('depose')
        self.presentItem(itemNMCDepose)

        orderedItems = meeting.getItems(listTypes=['normal', 'late', 'depose'], ordered=True)
        item1 = orderedItems[0]
        item2 = orderedItems[1]
        item3 = orderedItems[2]
        item3.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        item4 = orderedItems[3]
        item4.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        item5 = orderedItems[4]
        item5.setCategory('communication')

        itemUids = [item.UID() for item in orderedItems]

        # Prescriptive items (normal, late and depose)
        standardPrescriItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                            standard=True,
                                                                            itemType='prescriptive')
        standardLateItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                         standard=True,
                                                                         listTypes='late',
                                                                         itemType='prescriptive')
        standardDeposeItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                           standard=True,
                                                                           listTypes='depose',
                                                                           itemType='prescriptive')
        # To council items (normal, late and depose)
        standardCouncilItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                            standard=True,
                                                                            itemType='toCouncil')
        standardCouncilLateItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                                standard=True,
                                                                                itemType='toCouncil',
                                                                                listTypes='late')
        standardCouncilDeposeItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                                  standard=True,
                                                                                  itemType='toCouncil',
                                                                                  listTypes='depose')


        # Communication items
        standardCommuItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                          standard=True,
                                                                          itemType='communication')
        self.assertEqual(len(standardPrescriItems[gic2][develCat]), 1)
        self.assertEqual(standardPrescriItems[gic2][develCat][0], item1)

        self.assertEqual(len(standardPrescriItems[gic2][eventsCat]), 1)
        self.assertEqual(standardPrescriItems[gic2][eventsCat][0], item2)

        self.assertEqual(len(standardCouncilItems[meetingCouncil][gic1][develCat]), 1)
        self.assertEqual(standardCouncilItems[meetingCouncil][gic1][develCat][0], item4)
        self.assertEqual(len(standardCouncilItems[meetingCouncil][gic1][researchCat]), 1)
        self.assertEqual(standardCouncilItems[meetingCouncil][gic1][researchCat][0], item3)

        self.assertEqual(standardCommuItems[0][0], commuCat)
        self.assertEqual(standardCommuItems[0][1], item5)

        self.assertEqual(len(standardLateItems[gic1][researchCat]), 1)
        self.assertEqual(standardLateItems[gic1][researchCat][0], itemLate)

        self.assertEqual(len(standardDeposeItems[gic1][researchCat]), 1)
        self.assertEqual(standardDeposeItems[gic1][researchCat][0], itemDepo)

        #self.assertEqual(len(standardEmergencyItems[gic1][researchCat]), 1)
        #self.assertEqual(standardEmergencyItems[gic1][researchCat][0], itemEmer)

        #self.assertEqual(len(standardComplItems[gic1][researchCat]), 1)
        #self.assertEqual(standardComplItems[gic1][researchCat][0], itemCompl)

        # Every item in the meeting is now from the police group
        for item in meeting.getItems(listTypes=['normal', 'late', 'depose']):
            item.setProposingGroup('zone-de-police')

        # Police prescriptive items (normal, late and depose)
        policePrescriItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                          standard=False,
                                                                          itemType='prescriptive')
        policeLateItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                       standard=False,
                                                                       listTypes=['late'],
                                                                       itemType='prescriptive')
        policeDeposeItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                         standard=False,
                                                                         listTypes=['depose'],
                                                                         itemType='prescriptive')
        # Police to council items (normal, emergency and
        # complementary(emergency+late))
        policeCouncilItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                          standard=False,
                                                                          itemType='toCouncil')
        policeEmergencyItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                            standard=False,
                                                                            itemType='toCouncil')
        policeComplItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                        standard=False,
                                                                        itemType='toCouncil',
                                                                        listTypes=['late'])
        # Police communication items
        policeCommuItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                        standard=False,
                                                                        itemType='communication')
        self.assertEqual(len(policePrescriItems[gic1][develCat]), 1)
        self.assertEqual(policePrescriItems[gic1][develCat][0], item1)

        self.assertEqual(len(policePrescriItems[gic1][eventsCat]), 1)
        self.assertEqual(policePrescriItems[gic1][eventsCat][0], item2)

        self.assertEqual(len(policeCouncilItems[gic1][develCat]), 1)
        self.assertEqual(policeCouncilItems[gic1][develCat][0], item4)

        self.assertEqual(len(policeCouncilItems[gic1][researchCat]), 1)
        self.assertEqual(policeCouncilItems[gic1][researchCat][0], item3)

        self.assertEqual(policeCommuItems[0][0], commuCat)
        self.assertEqual(policeCommuItems[0][1], item5)

        self.assertEqual(len(policeLateItems[gic1][researchCat]), 1)
        self.assertEqual(policeLateItems[gic1][researchCat][0], itemLate)

        self.assertEqual(len(policeDeposeItems[gic1][researchCat]), 1)
        self.assertEqual(policeDeposeItems[gic1][researchCat][0], itemDepo)

        self.assertEqual(len(policeEmergencyItems[gic1][researchCat]), 1)
        self.assertEqual(policeEmergencyItems[gic1][researchCat][0], itemEmer)

        self.assertEqual(len(policeComplItems[gic1][researchCat]), 1)
        self.assertEqual(policeComplItems[gic1][researchCat][0], itemCompl)

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

    def test_pm_InsertItemOnCommunication(self):
        '''Test inserting an item using the "on_communication" sorting method.'''
        self._setupPoliceGroup()
        cfg = self.meetingConfig
        cfg.setInsertingMethodsOnAddItem(
            ({'insertingMethod': 'on_communication',
              'reverse': '0'}, ))
        cfg.setUseGroupsAsCategories(False)

        self.changeUser('pmManager')
        # create items with various categories
        itemDev1 = self.create('MeetingItem', category='deployment')
        itemDev2 = self.create('MeetingItem', category='deployment')
        itemDev3 = self.create('MeetingItem', category=COMMUNICATION_CAT_ID)
        itemVen1 = self.create('MeetingItem', proposingGroup='vendors', category='development')
        itemVen2 = self.create('MeetingItem', proposingGroup='vendors', category='deployment')
        itemVen3 = self.create('MeetingItem', proposingGroup='vendors', category=COMMUNICATION_CAT_ID)
        meeting = self.create('Meeting', date=DateTime())
        for item in [itemDev1, itemDev2, itemDev3,
                     itemVen1, itemVen2, itemVen3]:
            self.presentItem(item)

        orderedItems = meeting.getItems(ordered=True)
        self.assertEquals([item.getCategory() for item in orderedItems],
                          [COMMUNICATION_CAT_ID, COMMUNICATION_CAT_ID,
                           'deployment', 'deployment', 'development', 'deployment'])

    def test_pm_FullInsertingProcess(self):
        '''Test inserting an item using the relevant inserting methods.'''
        self._setupPoliceGroup()
        cfg = self.meetingConfig
        cfg2 = self.meetingConfig2
        cfg2Id = cfg2.getId()

        cfg.setInsertingMethodsOnAddItem(
            ({'insertingMethod': 'on_police_then_other_groups', 'reverse': '0'},
             {'insertingMethod': 'on_communication', 'reverse': '1'},
             {'insertingMethod': 'on_other_mc_to_clone_to', 'reverse': '1'},
             {'insertingMethod': 'on_list_type', 'reverse': '0'},
             {'insertingMethod': 'on_groups_in_charge', 'reverse': '0'},
             {'insertingMethod': 'on_categories', 'reverse': '0'}))

        cfg.setUseGroupsAsCategories(False)
        # let creators select the 'toDiscuss' value
        cfg.setToDiscussSetOnItemInsert(False)
        cfg.setMeetingConfigsToCloneTo(({'meeting_config': '%s' % cfg2Id,
                                         'trigger_workflow_transitions_until': '__nothing__'},))

        # create items and meetings using demo data
        self.changeUser('pmManager')
        _demoData(self.portal, 'pmManager', ('developers', 'vendors'))
        meeting = cfg.getMeetingsAcceptingItems()[-3].getObject()
        orderedItems = meeting.getItems(ordered=True)
        self.assertEquals(
            [(item.getListType(),
              item.getProposingGroup(),
              item.getProposingGroup(theObject=True).getGroupInChargeAt(meeting.getDate()).getId(),
              item.getOtherMeetingConfigsClonableTo(),
              item.getOtherMeetingConfigsClonableToEmergency(),
              item.getCategory()) for item in orderedItems],
            [('normal', 'zone-de-police', 'groupincharge1', (), (), 'remboursement'),
             ('normal', 'zone-de-police', 'groupincharge1', (), (), 'remboursement'),
             ('late', 'zone-de-police', 'groupincharge1', (), (), 'remboursement'),
             ('late', 'zone-de-police', 'groupincharge1', (), (), 'remboursement'),
             ('depose', 'zone-de-police', 'groupincharge1', (), (), 'remboursement'),
             ('normal', 'zone-de-police', 'groupincharge1', ('meeting-config-council',), (), 'affaires-juridiques'),
             ('normal', 'zone-de-police', 'groupincharge1', ('meeting-config-council',), (), 'affaires-juridiques'),
             ('normal', 'zone-de-police', 'groupincharge1', ('meeting-config-council',), ('meeting-config-council',), 'affaires-juridiques'),
             ('normal', 'zone-de-police', 'groupincharge1', ('meeting-config-council',), (), 'remboursement'),
             ('late', 'zone-de-police', 'groupincharge1', ('meeting-config-council',), (), 'affaires-juridiques'),
             ('late', 'zone-de-police', 'groupincharge1', ('meeting-config-council',), (), 'affaires-juridiques'),
             ('late', 'zone-de-police', 'groupincharge1', ('meeting-config-council',), ('meeting-config-council',), 'affaires-juridiques'),
             ('late', 'zone-de-police', 'groupincharge1', ('meeting-config-council',), (), 'remboursement'),
             ('normal', 'zone-de-police', 'groupincharge1', (), (), 'communication'),
             ('normal', 'zone-de-police', 'groupincharge1', (), (), 'communication'),
             ('normal', 'zone-de-police', 'groupincharge1', (), (), 'communication'),
             ('normal', 'vendors', 'groupincharge1', (), (), 'remboursement'),
             ('normal', 'vendors', 'groupincharge1', (), (), 'remboursement'),
             ('normal', 'developers', 'groupincharge2', (), (), 'remboursement'),
             ('normal', 'developers', 'groupincharge2', (), (), 'remboursement'),
             ('late', 'vendors', 'groupincharge1', (), (), 'remboursement'),
             ('late', 'vendors', 'groupincharge1', (), (), 'remboursement'),
             ('depose', 'vendors', 'groupincharge1', (), (), 'remboursement'),
             ('normal', 'vendors', 'groupincharge1', ('meeting-config-council',), (), 'affaires-juridiques'),
             ('normal', 'vendors', 'groupincharge1', ('meeting-config-council',), (), 'affaires-juridiques'),
             ('normal', 'vendors', 'groupincharge1', ('meeting-config-council',), (), 'remboursement'),
             ('normal', 'developers', 'groupincharge2', ('meeting-config-council',), (), 'affaires-juridiques'),
             ('normal', 'developers', 'groupincharge2', ('meeting-config-council',), (), 'affaires-juridiques'),
             ('normal', 'developers', 'groupincharge2', ('meeting-config-council',), (), 'remboursement'),
             ('normal', 'developers', 'groupincharge2', ('meeting-config-council',), ('meeting-config-council',), 'remboursement'),
             ('late', 'developers', 'groupincharge2', ('meeting-config-council',), (), 'affaires-juridiques'),
             ('late', 'developers', 'groupincharge2', ('meeting-config-council',), (), 'remboursement'),
             ('late', 'developers', 'groupincharge2', ('meeting-config-council',), ('meeting-config-council',), 'remboursement'),
             ('normal', 'developers', 'groupincharge2', (), (), 'communication'),
             ('normal', 'developers', 'groupincharge2', (), (), 'communication'),
             ('normal', 'developers', 'groupincharge2', (), (), 'communication')])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeeting, prefix='test_'))
    return suite
