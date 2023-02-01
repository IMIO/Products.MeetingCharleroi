# -*- coding: utf-8 -*-
import datetime

from DateTime import DateTime
from imio.history.utils import getLastWFAction
from plone import api
from Products.MeetingCharleroi.config import COMMUNICATION_CAT_ID
from Products.MeetingCharleroi.config import COUNCIL_DEFAULT_CATEGORY
from Products.MeetingCharleroi.config import COUNCIL_DEFAULT_CLASSIFIER
from Products.MeetingCharleroi.config import COUNCIL_SPECIAL_CATEGORIES
from Products.MeetingCharleroi.config import POLICE_GROUP_PREFIX
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCommunes.tests.testCustomMeeting import testCustomMeetingType as mctcm
from Products.PloneMeeting.utils import org_id_to_uid


class testCustomMeeting(MeetingCharleroiTestCase, mctcm):
    """
        Tests the Meeting adapted methods
    """

    def test_GetNumberOfItems(self):
        """
          This method will return a certain number of items depending on passed paramaters.
        """
        self.changeUser('admin')
        # make categories available
        self.setMeetingConfig(self.meetingConfig2.getId())
        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        orderedItems = meeting.get_items(ordered=True)
        # the meeting is created with 5 items
        self.assertEqual(len(orderedItems), 5)
        itemUids = [item.UID() for item in orderedItems]
        # without parameters, every items are returned
        self.assertEqual(meeting.adapted().getNumberOfItems(itemUids), 5)

        # test the 'privacy' parameter
        # by default, 2 items are 'secret' and 3 are 'public'
        itemPrivacies = [item.getPrivacy() for item in orderedItems]
        self.assertEqual(itemPrivacies.count('secret'), 2)
        self.assertEqual(itemPrivacies.count('public'), 3)
        # same using getNumberOfItems
        self.assertEqual(meeting.adapted().getNumberOfItems(itemUids, privacy='secret'), 2)
        self.assertEqual(meeting.adapted().getNumberOfItems(itemUids, privacy='public'), 3)

        # test the 'categories' parameter
        # by default, 2 items are in the 'events' category,
        # 2 are in the 'development' category
        # 1 in the 'research' category
        itemCategories = [item.getCategory() for item in orderedItems]
        self.assertEqual(itemCategories.count('events'), 2)
        self.assertEqual(itemCategories.count('development'), 2)
        self.assertEqual(itemCategories.count('research'), 1)
        # same using getNumberOfItems
        self.assertEqual(meeting.adapted().getNumberOfItems(itemUids, categories=['events', ]), 2)
        self.assertEqual(meeting.adapted().getNumberOfItems(itemUids, categories=['development', ]), 2)
        # we can pass several categories
        self.assertEqual(
            meeting.adapted().getNumberOfItems(itemUids, categories=['dummycategory', 'research', 'development', ]),
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
        self.assertEqual(len(meeting.get_items()), 5)
        self.assertEqual(len(meeting.get_items(list_types=['late'])), 2)
        # same using getNumberOfItems
        self.assertEqual(meeting.adapted().getNumberOfItems(itemUids, list_types=['normal']), 3)
        self.assertEqual(meeting.adapted().getNumberOfItems(itemUids, list_types=['late']), 2)

        # we can combinate parameters
        # we know that we have 2 late items that are using the 'development' category...
        lateItems = meeting.get_items(list_types=['late'])
        self.assertEqual(len(lateItems), 2)
        self.assertEqual(lateItems[0].getCategory(), 'development')
        self.assertEqual(lateItems[1].getCategory(), 'development')
        self.assertEqual(
            meeting.adapted().getNumberOfItems(itemUids, categories=['development', ], list_types=['late']),
            2)
        # we have so 0 normal item using the 'development' category
        self.assertEqual(
            meeting.adapted().getNumberOfItems(itemUids, categories=['development', ], list_types=['normal']),
            0)

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

        meetingCouncil = self._createMeetingWithItems(withItems=False, meetingDate=(DateTime() + 1).asdatetime())
        meetingCouncil2 = self._createMeetingWithItems(withItems=False, meetingDate=(DateTime() + 30).asdatetime())
        meetingCouncilUID = meetingCouncil.UID()
        meetingCouncilUID2 = meetingCouncil2.UID()

        self.setMeetingConfig(self.meetingConfig.getId())

        # item late
        itemLate = self.create('MeetingItem')
        itemLate.setProposingGroup(self.vendors_uid)
        itemLate.setAssociatedGroups((self.developers_uid,))
        itemLate.setCategory('research')
        itemLate.setListType('late')
        self.presentItem(itemLate)

        # item depose
        itemDepo = self.create('MeetingItem')
        itemDepo.setProposingGroup(self.vendors_uid)
        itemDepo.setAssociatedGroups((self.developers_uid,))
        itemDepo.setCategory('research')
        self.presentItem(itemDepo)
        itemDepo.setListType('depose')

        # item council "emergency" to next meeting
        itemNextCouncil = self.create('MeetingItem')
        itemNextCouncil.setProposingGroup(self.vendors_uid)
        itemNextCouncil.setAssociatedGroups((self.developers_uid,))
        itemNextCouncil.setCategory('research')
        itemNextCouncil.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNextCouncil.setPreferredMeeting(meetingCouncilUID)
        self.presentItem(itemNextCouncil)

        # item council "emergency" to next meeting late
        itemNCLate = self.create('MeetingItem')
        itemNCLate.setProposingGroup(self.vendors_uid)
        itemNCLate.setAssociatedGroups((self.developers_uid,))
        itemNCLate.setCategory('research')
        itemNCLate.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNCLate.setPreferredMeeting(meetingCouncilUID)
        itemNCLate.setListType('late')
        self.presentItem(itemNCLate)

        # item council "emergency" to next meeting depose
        itemNCDepose = self.create('MeetingItem')
        itemNCDepose.setProposingGroup(self.vendors_uid)
        itemNCDepose.setAssociatedGroups((self.developers_uid,))
        itemNCDepose.setCategory('research')
        itemNCDepose.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNCDepose.setPreferredMeeting(meetingCouncilUID)
        itemNCDepose.setListType('depose')
        self.presentItem(itemNCDepose)

        # item council to next month meeting
        itemNextMonthCouncil = self.create('MeetingItem')
        itemNextMonthCouncil.setProposingGroup(self.vendors_uid)
        itemNextMonthCouncil.setAssociatedGroups((self.developers_uid,))
        itemNextMonthCouncil.setCategory('research')
        itemNextMonthCouncil.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNextMonthCouncil.setPreferredMeeting(meetingCouncilUID2)
        self.presentItem(itemNextMonthCouncil)

        # item council to next month meeting late
        itemNMCLate = self.create('MeetingItem')
        itemNMCLate.setProposingGroup(self.vendors_uid)
        itemNMCLate.setAssociatedGroups((self.developers_uid,))
        itemNMCLate.setCategory('research')
        itemNMCLate.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNMCLate.setPreferredMeeting(meetingCouncilUID2)
        itemNMCLate.setListType('late')
        self.presentItem(itemNMCLate)

        # item council to next month meeting depose
        itemNMCDepose = self.create('MeetingItem')
        itemNMCDepose.setProposingGroup(self.vendors_uid)
        itemNMCDepose.setAssociatedGroups((self.developers_uid,))
        itemNMCDepose.setCategory('research')
        itemNMCDepose.setOtherMeetingConfigsClonableTo(u'meeting-config-council')
        itemNMCDepose.setPreferredMeeting(meetingCouncilUID2)
        itemNMCDepose.setListType('depose')
        self.presentItem(itemNMCDepose)

        orderedItems = meeting.get_items(list_types=['normal', 'late', 'depose'], ordered=True)
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
                                                                         list_types='late',
                                                                         itemType='prescriptive')
        standardDeposeItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                           standard=True,
                                                                           list_types='depose',
                                                                           itemType='prescriptive')
        # To council items (normal, late and depose)
        standardCouncilItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                            standard=True,
                                                                            itemType='toCouncil')
        standardCouncilLateItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                                standard=True,
                                                                                itemType='toCouncil',
                                                                                list_types='late')
        standardCouncilDeposeItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                                  standard=True,
                                                                                  itemType='toCouncil',
                                                                                  list_types='depose')

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

        # self.assertEqual(len(standardEmergencyItems[gic1][researchCat]), 1)
        # self.assertEqual(standardEmergencyItems[gic1][researchCat][0], itemEmer)

        # self.assertEqual(len(standardComplItems[gic1][researchCat]), 1)
        # self.assertEqual(standardComplItems[gic1][researchCat][0], itemCompl)

        # Every item in the meeting is now from the police group
        for item in meeting.get_items(list_types=['normal', 'late', 'depose']):
            item.setProposingGroup(org_id_to_uid(POLICE_GROUP_PREFIX))

        # Police prescriptive items (normal, late and depose)
        policePrescriItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                          standard=False,
                                                                          itemType='prescriptive')
        policeLateItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                       standard=False,
                                                                       list_types=['late'],
                                                                       itemType='prescriptive')
        policeDeposeItems = meeting.adapted().getPrintableItemsForAgenda(itemUids,
                                                                         standard=False,
                                                                         list_types=['depose'],
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
                                                                        list_types=['late'])
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
        itemVen1 = self.create('MeetingItem', proposingGroup=self.vendors_uid)
        itemVen2 = self.create('MeetingItem', proposingGroup=self.vendors_uid)
        itemPol1 = self.create('MeetingItem', proposingGroup=org_id_to_uid(POLICE_GROUP_PREFIX))
        itemPol2 = self.create('MeetingItem', proposingGroup=org_id_to_uid(POLICE_GROUP_PREFIX))
        meeting = self.create('Meeting', date=DateTime().asdatetime())
        for item in [itemDev1, itemDev2, itemDev3,
                     itemVen1, itemVen2,
                     itemPol1, itemPol2, ]:
            self.presentItem(item)

        police_uid = org_id_to_uid(POLICE_GROUP_PREFIX)
        orderedItems = meeting.get_items(ordered=True)
        self.assertEqual([item.getId() for item in orderedItems],
                         ['o6', 'o7', 'o1', 'o2', 'o3', 'o4', 'o5'])
        self.assertEqual([item.getProposingGroup() for item in orderedItems],
                         [police_uid, police_uid,
                          self.developers_uid, self.developers_uid, self.developers_uid,
                          self.vendors_uid, self.vendors_uid])

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
        itemDev1 = self.create('MeetingItem', category='affaires-juridiques')
        itemDev2 = self.create('MeetingItem', category='affaires-juridiques')
        itemDev3 = self.create('MeetingItem', category=COMMUNICATION_CAT_ID)
        itemVen1 = self.create('MeetingItem', proposingGroup=self.vendors_uid, category='remboursement')
        itemVen2 = self.create('MeetingItem', proposingGroup=self.vendors_uid, category='affaires-juridiques')
        itemVen3 = self.create('MeetingItem', proposingGroup=self.vendors_uid, category=COMMUNICATION_CAT_ID)
        meeting = self.create('Meeting', date=DateTime().asdatetime())
        for item in [itemDev1, itemDev2, itemDev3,
                     itemVen1, itemVen2, itemVen3]:
            self.presentItem(item)

        orderedItems = meeting.get_items(ordered=True)
        self.assertEqual([item.getCategory() for item in orderedItems],
                         [COMMUNICATION_CAT_ID, COMMUNICATION_CAT_ID,
                          'affaires-juridiques', 'affaires-juridiques',
                          'remboursement', 'affaires-juridiques'])

    def test_pm_FullInsertingProcess(self):
        '''Test inserting an item using the relevant inserting methods.'''
        collegeMeeting, collegeExtraMeeting = self.setupCollegeDemoData()
        orderedItems = collegeMeeting.get_items(ordered=True)
        cfg2_id = self.meetingConfig2.getId()
        self.assertEqual([
            (item.getListType(), item.getProposingGroup(True).id, item.getGroupsInCharge(True, first=True).id,
             item.getOtherMeetingConfigsClonableTo(), item.getOtherMeetingConfigsClonableToPrivacy(),
             item.getOtherMeetingConfigsClonableToEmergency(), item.getCategory()) for item in orderedItems],
            [
                ('normal', 'zone-de-police', 'groupincharge1', (), (), (), 'remboursement'),
                ('normal', 'zone-de-police', 'groupincharge1', (), (), (), 'remboursement'),
                ('late', 'zone-de-police-compta', 'groupincharge1', (), (), (), 'remboursement'),
                ('late', 'zone-de-police', 'groupincharge1', (), (), (), 'remboursement'),
                ('depose', 'zone-de-police', 'groupincharge1', (), (), (), 'remboursement'),
                ('normal', 'zone-de-police', 'groupincharge1', (cfg2_id,), (), (), 'indeterminee'),
                ('normal', 'zone-de-police-compta', 'groupincharge1', (cfg2_id,), (cfg2_id,), (), 'indeterminee'),
                ('normal', 'zone-de-police-compta', 'groupincharge1', (cfg2_id,), (cfg2_id,), (), 'indeterminee'),
                ('normal', 'zone-de-police', 'groupincharge1', (cfg2_id,), (), (cfg2_id,), 'indeterminee'),
                ('late', 'zone-de-police', 'groupincharge1', (cfg2_id,), (), (), 'indeterminee'),
                ('late', 'zone-de-police-compta', 'groupincharge1', (cfg2_id,), (cfg2_id,), (), 'indeterminee'),
                ('late', 'zone-de-police', 'groupincharge1', (cfg2_id,), (), (), 'indeterminee'),
                ('late', 'zone-de-police', 'groupincharge1', (cfg2_id,), (), (cfg2_id,), 'indeterminee'),
                ('normal', 'zone-de-police', 'groupincharge1', (), (), (), 'communication'),
                ('normal', 'zone-de-police-compta', 'groupincharge1', (), (), (), 'communication'),
                ('normal', 'zone-de-police', 'groupincharge1', (), (), (), 'communication'),
                ('normal', 'vendors', 'groupincharge1', (), (), (), 'remboursement'),
                ('normal', 'vendors', 'groupincharge1', (), (), (), 'remboursement'),
                ('normal', 'developers', 'groupincharge2', (), (), (), 'remboursement'),
                ('normal', 'developers', 'groupincharge2', (), (), (), 'remboursement'),
                ('late', 'vendors', 'groupincharge1', (), (), (), 'remboursement'),
                ('late', 'vendors', 'groupincharge1', (), (), (), 'remboursement'),
                ('depose', 'vendors', 'groupincharge1', (), (), (), 'remboursement'),
                ('normal', 'vendors', 'groupincharge1', (cfg2_id,), (), (), 'indeterminee'),
                ('normal', 'vendors', 'groupincharge1', (cfg2_id,), (), (), 'indeterminee'),
                ('normal', 'vendors', 'groupincharge1', (cfg2_id,), (cfg2_id,), (), 'indeterminee'),
                ('normal', 'developers', 'groupincharge2', (cfg2_id,), (cfg2_id,), (), 'indeterminee'),
                ('normal', 'developers', 'groupincharge2', (cfg2_id,), (), (), 'indeterminee'),
                ('normal', 'developers', 'groupincharge2', (cfg2_id,), (cfg2_id,), (), 'indeterminee'),
                ('normal', 'developers', 'groupincharge2', (cfg2_id,), (), (cfg2_id,), 'indeterminee'),
                ('late', 'developers', 'groupincharge2', (cfg2_id,), (), (), 'indeterminee'),
                ('late', 'developers', 'groupincharge2', (cfg2_id,), (cfg2_id,), (), 'indeterminee'),
                ('late', 'developers', 'groupincharge2', (cfg2_id,), (cfg2_id,), (cfg2_id,), 'indeterminee'),
                ('normal', 'developers', 'groupincharge2', (), (), (), 'conseil-communal-arret-de-lordre-du-jour'),
                ('normal', 'developers', 'groupincharge2', (), (), (), 'communication'),
                ('normal', 'developers', 'groupincharge2', (), (), (), 'communication'),
                ('normal', 'developers', 'groupincharge2', (), (), (), 'communication')]
        )

    def test_CollegeCommunicationItemIsInsertedAsNormalItem(self):
        """ """
        collegeMeeting, collegeExtraMeeting = self.setupCollegeDemoData()
        self.portal.REQUEST['PUBLISHED'] = collegeMeeting
        self.freezeMeeting(collegeMeeting)
        self.assertEqual(collegeMeeting.query_state(), 'frozen')
        commItem = self.create('MeetingItem')
        commItem.setCategory('communication')
        commItem.setPreferredMeeting(collegeMeeting.UID())
        gic2_uid = org_id_to_uid('groupincharge2')
        commItem.setProposingGroupWithGroupInCharge(
            '{0}__groupincharge__{1}'.format(self.developers_uid, gic2_uid))
        self.presentItem(commItem)
        self.assertEqual(commItem.getMeeting(), collegeMeeting)
        self.assertEqual(commItem.getListType(), 'normal')

    def test_CouncilItemsUsingSpecialCategoriesAreInsertedAsNormalItem(self):
        """ """
        # use the Council demo that adds items using special category in a frozen meeting
        meeting = self.setupCouncilDemoData()
        self.changeUser('pmManager')
        self.assertEqual(meeting.query_state(), 'frozen')
        special_items = meeting.get_items(
            ordered=True, additional_catalog_query={'getCategory': COUNCIL_SPECIAL_CATEGORIES})
        # items were presented after meeting freeze
        for item in special_items:
            self.assertTrue(item.modified() > getLastWFAction(meeting, 'freeze')['time'])
        self.assertEqual(
            [(item.getListType(), item.getCategory(), item.getPrivacy()) for item in special_items],
            [('normal', 'proposition-de-motion', 'public'),
             ('normal', 'proposition-de-motion', 'public'),
             ('normal', 'proposes-par-un-conseiller', 'public'),
             ('normal', 'proposes-par-un-conseiller', 'public'),
             ('normal', 'interventions', 'public'),
             ('normal', 'questions-actualite', 'public'),
             ('normal', 'questions-actualite', 'public'),
             ('normal', 'questions-actualite', 'public')])

    def test_CouncilPublicItemsAreInsertedUsingIndetemineeCategoryWhereSecretItemsAreLeftValidated(self):
        """Items with confidentiality 'public' coming from College are inserted in a Council meeting
           a will use the 'indeterminee' category.  Items with confidentiality 'secret' coming from the College
           will stay 'validated' and are not automatically inserted into a meeting."""
        self.setMeetingConfig('meeting-config-council')
        self.setupCouncilConfig()
        self.changeUser('pmManager')
        # Council
        self.setMeetingConfig('meeting-config-council')
        council_meeting = self.create('Meeting', date=(datetime.datetime.today() + datetime.timedelta(1)))
        # College
        self.setMeetingConfig('meeting-config-college')
        publicItem = self.create('MeetingItem')
        publicItem.setOtherMeetingConfigsClonableTo((u'meeting-config-council', ))
        publicItem.setOtherMeetingConfigsClonableToPrivacy(())
        gic2_uid = org_id_to_uid('groupincharge2')
        publicItem.setProposingGroupWithGroupInCharge(
            '{0}__groupincharge__{1}'.format(self.developers_uid, gic2_uid))
        secretItem = self.create('MeetingItem')
        secretItem.setOtherMeetingConfigsClonableTo((u'meeting-config-council', ))
        secretItem.setOtherMeetingConfigsClonableToPrivacy((u'meeting-config-council', ))
        secretItem.setProposingGroupWithGroupInCharge(
            '{0}__groupincharge__{1}'.format(self.developers_uid, gic2_uid))
        college_meeting = self.create('Meeting', date=DateTime('2017/02/12').asdatetime())
        self.presentItem(publicItem)
        self.presentItem(secretItem)
        self.closeMeeting(college_meeting)
        council_publicItem = publicItem.getItemClonedToOtherMC('meeting-config-council')
        # groupsInCharge were kept
        self.assertEqual(
            (council_publicItem.getProposingGroup(), council_publicItem.getGroupsInCharge(first=True)),
            (publicItem.getProposingGroup(), publicItem.getGroupsInCharge(first=True)))
        council_secretItem = secretItem.getItemClonedToOtherMC('meeting-config-council')
        # groupsInCharge were kept
        self.assertEqual(
            (council_secretItem.getProposingGroup(), council_secretItem.getGroupsInCharge(first=True)),
            (secretItem.getProposingGroup(), secretItem.getGroupsInCharge(first=True)))
        # publicItem was presented into the council_meeting, no matter the 'PUBLISHED' object is the college_meeting
        self.assertEqual(self.request['PUBLISHED'], college_meeting)
        self.assertEqual(council_publicItem.getMeeting(), council_meeting)
        self.assertEqual(council_publicItem.getCategory(), COUNCIL_DEFAULT_CATEGORY)
        # secretItem is not presented and is still validated
        self.assertFalse(council_secretItem.hasMeeting())

    def test_ClassifierIsSetWhenMeetingItemIsClonedToCouncil(self):
        """
        When a MeetingItem is sent from College to Council, a default classifier
        must be set in order to present it.
        """
        self.changeUser('siteadmin')
        self.setMeetingConfig('meeting-config-council')
        self.meetingConfig.setUseGroupsAsCategories(False)
        self.setupCouncilConfig()
        self.meetingConfig.setUsedItemAttributes(
            list(self.meetingConfig.getUsedItemAttributes()) + ['classifier']
        )
        # Council
        council_meeting = self.create('Meeting', date=DateTime() + 1)
        # College
        self.setMeetingConfig('meeting-config-college')
        self.meetingConfig.setMeetingConfigsToCloneTo(({
            'meeting_config': 'meeting-config-council',
            'trigger_workflow_transitions_until': 'meeting-config-council.present'
        },))

        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        item.setOtherMeetingConfigsClonableTo((u'meeting-config-council',))
        item = self.create('MeetingItem', category=COUNCIL_DEFAULT_CATEGORY)
        item.setOtherMeetingConfigsClonableTo((u'meeting-config-council',))
        item.setOtherMeetingConfigsClonableToPrivacy(())
        gic2_uid = org_id_to_uid('groupincharge2')
        item.setProposingGroupWithGroupInCharge(
            '{0}__groupincharge__{1}'.format(self.developers_uid, gic2_uid))

        private_item = self.create('MeetingItem', category=COUNCIL_DEFAULT_CATEGORY)
        private_item.setOtherMeetingConfigsClonableTo((u'meeting-config-council',))
        private_item.setOtherMeetingConfigsClonableToPrivacy((u'meeting-config-council',))
        private_item.setProposingGroupWithGroupInCharge(
            '{0}__groupincharge__{1}'.format(self.developers_uid, gic2_uid))
        college_meeting = self.create('Meeting', date=DateTime('2021/07/19'))
        self.presentItem(item)
        self.presentItem(private_item)
        self.closeMeeting(college_meeting)

        council_item = item.getItemClonedToOtherMC('meeting-config-council')
        self.assertEqual(council_item.getClassifier(), COUNCIL_DEFAULT_CLASSIFIER)
        self.assertEqual(council_item.queryState(), 'presented')

        council_private_item = private_item.getItemClonedToOtherMC('meeting-config-council')
        self.assertEqual(council_private_item.getClassifier(), COUNCIL_DEFAULT_CLASSIFIER)
        # Private items are not presented by default
        self.assertNotEqual(council_private_item.queryState(), 'presented')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeeting, prefix='test_'))
    return suite
