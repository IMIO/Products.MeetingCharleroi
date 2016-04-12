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


class testCustomMeeting(MeetingCharleroiTestCase):
    """
        Tests the Meeting adapted methods
    """

    def test_GetPrintableItemsByCategoryWithMeetingCategory(self):
        """
            This method aimed to ease printings should return a list of items ordered by category
        """
        # a list of lists where inner lists contain
        # a categrory (MeetingCategory or MeetingGroup) as first element and items of this category

        # configure PloneMeeting
        # test if the category is a MeetingCategory
        # insert items in the meeting depending on the category
        self.changeUser('pmManager')
        self.setMeetingConfig(self.meetingConfig2.getId())
        meeting = self._createMeetingWithItems()
        i6 = self.create('MeetingItem', title='Item6')
        i6.setCategory('development')
        i7 = self.create('MeetingItem', title='Item7')
        i7.setCategory('development')
        self.presentItem(i6)
        self.presentItem(i7)
        # build the list of uids
        itemUids = [anItem.UID() for anItem in meeting.getItems(ordered=True)]
        # the 2 new development items are moved to the end of the meeting
        view = i6.restrictedTraverse('@@change-item-order')
        view('number', '7')
        view('down')
        view = i7.restrictedTraverse('@@change-item-order')
        view('number', '7')
        # test on the meeting
        # we should have a list containing 3 lists, 1 list by category
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(itemUids)), 3)
        # the order and the type should be kept, the first element of inner list is a MeetingCategory
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[0][0].getId(), 'development')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[1][0].getId(), 'events')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[2][0].getId(), 'research')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[0][0].meta_type, 'MeetingCategory')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[1][0].meta_type, 'MeetingCategory')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[2][0].meta_type, 'MeetingCategory')
        # the first category should have 4 items, the second 2 and the third 1 ( + 1 category element for each one)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(itemUids)[0]), 5)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(itemUids)[1]), 3)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(itemUids)[2]), 2)
        # other element of the list are MeetingItems...
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[0][1].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[0][2].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[0][3].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[0][4].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[1][1].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[1][2].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(itemUids)[2][1].meta_type, 'MeetingItem')

    def test_GetPrintableItemsByCategoryWithMeetingGroup(self):
        """
            This method aimed to ease printings should return a list of items ordered by category
        """
        # a list of lists where inner lists contain
        # a categrory (MeetingCategory or MeetingGroup) as first element and items of this category

        # configure PloneMeeting
        # test if the category is a MeetingCategory
        # insert items in the meeting depending on the category
        self.changeUser('pmManager')
        self.meetingConfig.setInsertingMethodsOnAddItem(({'insertingMethod': 'on_proposing_groups',
                                                         'reverse': '0'}, ))

        # add a Meeting and present several items in different categories
        self.changeUser('pmManager')
        i1 = self.create('MeetingItem', title='Item1')
        i1.setProposingGroup('developers')
        i2 = self.create('MeetingItem', title='Item2')
        i2.setProposingGroup('developers')
        i3 = self.create('MeetingItem', title='Item3')
        i3.setProposingGroup('developers')
        i4 = self.create('MeetingItem', title='Item4')
        i4.setProposingGroup('vendors')
        i5 = self.create('MeetingItem', title='Item5')
        i5.setProposingGroup('vendors')
        i6 = self.create('MeetingItem', title='Item6')
        i6.setProposingGroup('vendors')
        i7 = self.create('MeetingItem', title='Item7')
        i7.setProposingGroup('vendors')
        items = (i1, i2, i3, i4, i5, i6, i7)
        m = self.create('Meeting', date='2007/12/11 09:00:00')
        # present every items in a meeting
        for item in items:
            self.presentItem(item)
        # build the list of uids
        itemUids = [anItem.UID() for anItem in m.getItems(ordered=True)]
        # test on the meeting
        # we should have a list containing 3 lists, 1 list by category
        self.assertEquals(len(m.adapted().getPrintableItemsByCategory(itemUids)), 2)
        # the order and the type should be kept, the first element of inner list is a MeetingCategory
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[0][0].getId(), 'developers')
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[1][0].getId(), 'vendors')
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[0][0].meta_type, 'MeetingGroup')
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[1][0].meta_type, 'MeetingGroup')
        # other element of the list are MeetingItems...
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[0][1].meta_type, 'MeetingItem')
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[0][2].meta_type, 'MeetingItem')
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[0][3].meta_type, 'MeetingItem')
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[1][1].meta_type, 'MeetingItem')
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[1][2].meta_type, 'MeetingItem')
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[1][3].meta_type, 'MeetingItem')
        self.assertEquals(m.adapted().getPrintableItemsByCategory(itemUids)[1][4].meta_type, 'MeetingItem')

    def test_GetPrintableItemsByCategoryWithBothLateItems(self):
        self.changeUser('pmManager')
        self.setMeetingConfig(self.meetingConfig2.getId())
        meeting = self._createMeetingWithItems()
        orderedItems = meeting.getItems(ordered=True)
        item1 = orderedItems[0]
        item2 = orderedItems[1]
        item3 = orderedItems[2]
        self.backToState(item1, 'prevalidated')
        self.backToState(item2, 'prevalidated')
        self.backToState(item3, 'prevalidated')
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
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[0][0].getId(), 'development')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[1][0].getId(), 'events')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[2][0].getId(), 'research')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[0][0].meta_type, 'MeetingCategory')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[1][0].meta_type, 'MeetingCategory')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[2][0].meta_type, 'MeetingCategory')
        # the event category should have 2 items, research 1 and development 2 ( + 1 category element for each one)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[0]), 3)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[1]), 3)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[2]), 2)
        # other element of the list are MeetingItems...
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[0][1].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[0][2].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[1][1].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[1][2].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, listTypes=['late', 'normal'])[2][1].meta_type, 'MeetingItem')

    def test_GetPrintableItemsByCategoryWhenForceCategOrderFromConfig(self):
        self.changeUser('pmManager')
        self.setMeetingConfig(self.meetingConfig2.getId())
        meeting = self._createMeetingWithItems()
        orderedItems = meeting.getItems(ordered=True)
        # the 2 development items are moved to the end of the meeting
        item1 = orderedItems[0]
        item2 = orderedItems[1]
        itemUids = [anItem.UID() for anItem in meeting.getItems(ordered=True)]
        view = item1.restrictedTraverse('@@change-item-order')
        view('number', '5')
        view('down')
        view = item2.restrictedTraverse('@@change-item-order')
        view('number', '5')
        # we should have a list containing 3 lists, 1 list by category
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(itemUids,
                                                                            forceCategOrderFromConfig=True)), 3)
        # the order and the type should be kept, the first element of inner list is a MeetingCategory
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[0][0].getId(), 'development')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[1][0].getId(), 'events')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[2][0].getId(), 'research')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[0][0].meta_type, 'MeetingCategory')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[1][0].meta_type, 'MeetingCategory')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[2][0].meta_type, 'MeetingCategory')
        # the first category should have 4 items, the second 2 and the third 1 ( + 1 category element for each one)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[0]), 3)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[1]), 3)
        self.assertEquals(len(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[2]), 2)
        # other element of the list are MeetingItems...
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[0][1].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[0][2].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[1][1].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[1][2].meta_type, 'MeetingItem')
        self.assertEquals(meeting.adapted().getPrintableItemsByCategory(
            itemUids, forceCategOrderFromConfig=True)[2][1].meta_type, 'MeetingItem')

    def test_InitializeDecisionField(self):
        """
            In the doDecide method, we initialize the Decision field to a default value made of
            Title+Description if the field is empty...
        """
        # make sure we are not hit by any other xhtmlTransformations
        self.meetingConfig.setXhtmlTransformTypes(())
        # check that it works
        # check that if the field contains something, it is not intialized again
        self.changeUser('pmManager')
        # create some items
        # empty decision
        i1 = self.create('MeetingItem', title='Item1', description="<p>Description Item1</p>")
        i1.setDecision("")
        i1.setProposingGroup('developers')
        # decision field is already filled
        i2 = self.create('MeetingItem', title='Item2', description="<p>Description Item2</p>")
        i2.setDecision("<p>Decision Item2</p>")
        i2.setProposingGroup('developers')
        # create an item with the default Kupu empty value
        i3 = self.create('MeetingItem', title='Item3', description="<p>Description Item3</p>")
        i3.setDecision("<p>&nbsp;</p>")
        i3.setProposingGroup('developers')
        meeting = self.create('Meeting', date='2007/12/11 09:00:00')
        # present every items in the meeting
        items = (i1, i2, i3)
        for item in items:
            self.do(item, 'propose')
            self.do(item, 'proposeToRefAdmin')
            self.do(item, 'prevalidate')
            self.do(item, 'validate')
            self.do(item, 'present')
        # check the decision field of every item
        self.assertTrue(i1.getDecision(keepWithNext=False) == "")
        self.assertTrue(i2.getDecision(keepWithNext=False) == '<p>Decision Item2</p>')
        self.assertTrue(i3.getDecision(keepWithNext=False) == '<p>&nbsp;</p>')
        # if cfg.initItemDecisionIfEmptyOnDecide is False, the decision field is not initialized
        self.meetingConfig.setInitItemDecisionIfEmptyOnDecide(False)
        self.decideMeeting(meeting)
        self.assertTrue(i1.getDecision(keepWithNext=False) == "")
        self.assertTrue(i2.getDecision(keepWithNext=False), '<p>Decision Item2</p>')
        # a complex HTML is not 'touched'
        self.assertTrue(i3.getDecision(keepWithNext=False), '<p>&nbsp;</p>')
        # now if cfg.initItemDecisionIfEmptyOnDecide is True
        # fields will be initialized
        self.meetingConfig.setInitItemDecisionIfEmptyOnDecide(True)
        # decide the meeting again
        self.backToState(meeting, 'created')
        self.decideMeeting(meeting)
        # i1 should contains now the concatenation of title and description
        self.assertEquals(i1.getDecision(keepWithNext=False), '<p>Item1</p><p>Description Item1</p>')
        # i2 sould not have changed
        self.assertEquals(i2.getDecision(keepWithNext=False), '<p>Decision Item2</p>')
        # i3 is initlaized because the decision field contained an empty_value
        self.assertEquals(i3.getDecision(keepWithNext=False), '<p>Item3</p><p>Description Item3</p>')

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
        self.backToState(item1, 'prevalidated')
        self.backToState(item2, 'prevalidated')
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
