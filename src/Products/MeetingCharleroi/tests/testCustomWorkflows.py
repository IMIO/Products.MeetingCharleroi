# -*- coding: utf-8 -*-
#
# File: testWorkflows.py
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

from DateTime import DateTime
from zope.i18n import translate
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase


class testCustomWorkflows(MeetingCharleroiTestCase):
    """Tests the default workflows implemented in MeetingCharleroi."""

    def test_FreezeMeeting(self):
        """
           When we freeze a meeting, every presented items will be frozen
           too and their state will be set to 'itemfrozen'.  When the meeting
           come back to 'created', every items will be corrected and set in the
           'presented' state
        """
        # First, define recurring items in the meeting config
        self.changeUser('pmManager')
        # create a meeting
        meeting = self.create('Meeting', date='2007/12/11 09:00:00')
        # create 2 items and present it to the meeting
        item1 = self.create('MeetingItem', title='The first item')
        self.presentItem(item1)
        item2 = self.create('MeetingItem', title='The second item')
        self.presentItem(item2)
        wftool = self.portal.portal_workflow
        # every presented items are in the 'presented' state
        self.assertEquals('presented', wftool.getInfoFor(item1, 'review_state'))
        self.assertEquals('presented', wftool.getInfoFor(item2, 'review_state'))
        # every items must be in the 'itemfrozen' state if we freeze the meeting
        self.freezeMeeting(meeting)
        self.assertEquals('itemfrozen', wftool.getInfoFor(item1, 'review_state'))
        self.assertEquals('itemfrozen', wftool.getInfoFor(item2, 'review_state'))
        # when an item is 'itemfrozen' it will stay itemfrozen if nothing
        # is defined in the meetingConfig.onMeetingTransitionItemTransitionToTrigger
        self.meetingConfig.setOnMeetingTransitionItemTransitionToTrigger([])
        self.backToState(meeting, 'created')
        self.assertEquals('itemfrozen', wftool.getInfoFor(item1, 'review_state'))
        self.assertEquals('itemfrozen', wftool.getInfoFor(item2, 'review_state'))

    def test_CloseMeeting(self):
        """
           When we close a meeting, every items are set to accepted if they are still
           not decided...
        """
        # First, define recurring items in the meeting config
        self.changeUser('pmManager')
        # create a meeting (with 7 items)
        meetingDate = DateTime().strftime('%y/%m/%d %H:%M:00')
        meeting = self.create('Meeting', date=meetingDate)
        item1 = self.create('MeetingItem')  # id=o2
        item1.setProposingGroup('vendors')
        item1.setAssociatedGroups(('developers',))
        item2 = self.create('MeetingItem')  # id=o3
        item2.setProposingGroup('developers')
        item3 = self.create('MeetingItem')  # id=o4
        item3.setProposingGroup('vendors')
        item4 = self.create('MeetingItem')  # id=o5
        item4.setProposingGroup('developers')
        item5 = self.create('MeetingItem')  # id=o7
        item5.setProposingGroup('vendors')
        item6 = self.create('MeetingItem', title='The sixth item')
        item6.setProposingGroup('vendors')
        item7 = self.create('MeetingItem')  # id=o8
        item7.setProposingGroup('vendors')
        for item in (item1, item2, item3, item4, item5, item6, item7):
            self.presentItem(item)
        # we freeze the meeting
        self.freezeMeeting(meeting)
        # a MeetingManager can put the item back to presented
        self.backToState(item7, 'presented')
        # we decide the meeting
        # while deciding the meeting, every items that where presented are frozen
        self.decideMeeting(meeting)
        # change all items in all different state (except first who is in good state)
        self.backToState(item7, 'presented')
        self.do(item2, 'delay')
        self.do(item3, 'pre_accept')
        self.do(item4, 'accept_but_modify')
        self.do(item5, 'refuse')
        self.do(item6, 'accept')
        # we close the meeting
        self.do(meeting, 'close')
        # every items must be in the 'decided' state if we close the meeting
        wftool = self.portal.portal_workflow
        # itemfrozen change into accepted
        self.assertEquals('accepted', wftool.getInfoFor(item1, 'review_state'))
        # delayed rest delayed (it's already a 'decide' state)
        self.assertEquals('delayed', wftool.getInfoFor(item2, 'review_state'))
        # pre_accepted change into accepted
        self.assertEquals('accepted', wftool.getInfoFor(item3, 'review_state'))
        # accepted_but_modified rest accepted_but_modified (it's already a 'decide' state)
        self.assertEquals('accepted_but_modified', wftool.getInfoFor(item4, 'review_state'))
        # refused rest refused (it's already a 'decide' state)
        self.assertEquals('refused', wftool.getInfoFor(item5, 'review_state'))
        # accepted rest accepted (it's already a 'decide' state)
        self.assertEquals('accepted', wftool.getInfoFor(item6, 'review_state'))
        # presented change into accepted
        self.assertEquals('accepted', wftool.getInfoFor(item7, 'review_state'))

    def test_CollegeProcessWithNormalAdvices(self):
        '''How does the process behave when some 'normal' advices,
           aka no 'finances' advice is aksed.'''
        # normal advices can be given when item in state 'itemcreated_waiting_advices',
        cfg = self.meetingConfig
        cfg.setUsedAdviceTypes(('asked_again', ) + self.meetingConfig.getUsedAdviceTypes())
        cfg.setItemAdviceStates(('itemcreated_waiting_advices', ))
        cfg.setItemAdviceEditStates = (('itemcreated_waiting_advices', ))
        cfg.setItemAdviceViewStates = (('itemcreated_waiting_advices', ))
        cfg.setKeepAccessToItemWhenAdviceIsGiven(True)

        self.changeUser('pmCreator1')
        item = self.create('MeetingItem', title='The first item')
        # if no advice to ask, pmCreator may only 'propose' the item
        self.assertTrue(self.transitions(item) == ['propose', ])
        # the mayWait_advices_from_itemcreated wfCondition returns a 'No' instance
        advice_required_to_ask_advices = translate('advice_required_to_ask_advices',
                                                   domain='PloneMeeting',
                                                   context=self.request)
        self.assertEqual(item.wfConditions().mayWait_advices_from_itemcreated().msg,
                         advice_required_to_ask_advices)
        # now ask 'vendors' advice
        item.setOptionalAdvisers(('vendors', ))
        item.at_post_edit_script()
        self.assertTrue(self.transitions(item) == ['wait_advices_from_itemcreated',
                                                   'propose', ])
        # give advice
        self.do(item, 'wait_advices_from_itemcreated')
        # pmReviewer2 is adviser for vendors
        self.changeUser('pmReviewer2')
        advice = createContentInContainer(item,
                                          'meetingadvice',
                                          **{'advice_group': 'vendors',
                                             'advice_type': u'positive',
                                             'advice_comment': RichTextValue(u'My comment vendors')})
        # no more advice to give
        self.assertTrue(not item.hasAdvices(toGive=True))
        # item may be proposed directly to administrative reviewer
        # from state 'itemcreated_waiting_advices'
        # we continue wf as internal reviewer may also ask advice
        self.changeUser('pmCreator1')
        self.do(item, 'proposeToAdministrativeReviewer')
        self.changeUser('pmAdminReviewer1')
        self.do(item, 'proposeToInternalReviewer')
        self.changeUser('pmInternalReviewer1')
        # no advice to give so not askable
        self.assertTrue(self.transitions(item) == ['backToProposedToAdministrativeReviewer',
                                                   'proposeToDirector', ])
        # advice could be asked again
        self.assertTrue(item.adapted().mayAskAdviceAgain(advice))
        item.setOptionalAdvisers(('vendors', 'developers'))
        item.at_post_edit_script()
        # now that there is an advice to give (developers)
        # internal reviewer may ask it
        self.assertTrue(self.transitions(item) == ['askAdvicesByInternalReviewer',
                                                   'backToProposedToAdministrativeReviewer',
                                                   'proposeToDirector', ])
        # give advice
        self.do(item, 'askAdvicesByInternalReviewer')
        # pmAdviser1 is adviser for developers
        self.changeUser('pmAdviser1')
        createContentInContainer(item,
                                 'meetingadvicefinances',
                                 **{'advice_group': 'developers',
                                    'advice_type': u'positive',
                                    'advice_comment': RichTextValue(u'My comment developers')})
        # item may be proposed directly to director
        # from state 'proposed_to_internal_reviewer_waiting_advices'
        self.changeUser('pmInternalReviewer1')
        self.do(item, 'proposeToDirector')
