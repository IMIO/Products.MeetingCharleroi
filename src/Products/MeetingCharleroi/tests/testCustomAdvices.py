# -*- coding: utf-8 -*-
#
# File: testAdvices.py
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
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from Products.MeetingCharleroi.config import FINANCE_GROUP_ID
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase


class testCustomAdvices(MeetingCharleroiTestCase, ):
    ''' '''
    def test_AdviceCategoryCorrectlyIndexed(self):
        """When an advice_category is defined, it is correctly indexed
           it's parent after add/modify/delete."""
        catalog = self.portal.portal_catalog
        cfg = self.meetingConfig
        self.changeUser('siteadmin')
        self._configureFinancesAdvice(cfg)
        # put users in finances group
        self._setupFinancesGroup()
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem', title='The first item')
        # ask finances advice
        item.setOptionalAdvisers(('dirfin__rowid__2016-05-01.0', ))
        self.proposeItem(item)
        self.changeUser('pmReviewer1')
        self.do(item, 'wait_advices_from_prevalidated')

        # now act as the finances users
        # advice may be added/edit when item is considered 'complete'
        self.changeUser('pmFinController')
        changeCompleteness = item.restrictedTraverse('@@change-item-completeness')
        self.request.set('new_completeness_value', 'completeness_complete')
        self.request.form['form.submitted'] = True
        changeCompleteness()
        # add advice
        advice = createContentInContainer(
            item,
            'meetingadvicefinances',
            **{'advice_group': FINANCE_GROUP_ID,
               'advice_type': u'positive_finance',
               'advice_comment': RichTextValue(u'My comment finances'),
               'advice_category': u'acquisitions'})
        # reindexed when advice added
        itemUID = item.UID()
        self.assertEquals(catalog(meta_type='MeetingItem',
                                  financesAdviceCategory=advice.advice_category)[0].UID,
                          itemUID)
        # reindexed when advice edited
        advice.advice_category = u'attributions'
        # notify modified
        notify(ObjectModifiedEvent(advice))
        self.assertEquals(catalog(meta_type='MeetingItem',
                                  financesAdviceCategory=advice.advice_category)[0].UID,
                          itemUID)
        # reindexed when advice deleted
        self.portal.restrictedTraverse('@@delete_givenuid')(advice.UID())
        self.assertEquals(len(catalog(meta_type='MeetingItem',
                              financesAdviceCategory=advice.advice_category)),
                          0)

    def test_MayChangeDelayTo(self):
        """Method MeetingItem.mayChangeDelayTo is made to control the 'available_on'
           of customAdvisers used for finance advice (5, 10 or 20 days).
           - 10 days is the only advice selectable thru the item edit form;
           - the delay '5' must be changed using the change delay widdget;
           - the delay '20' is reserved to finance advisers."""
        cfg = self.meetingConfig
        self.changeUser('siteadmin')
        self._configureFinancesAdvice(cfg)
        # put users in finances group
        self._setupFinancesGroup()
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        # by default, only the 10 days delay is selectable
        self.assertEqual(item.listOptionalAdvisers().keys(),
                         ['not_selectable_value_delay_aware_optional_advisers',
                          '%s__rowid__2016-05-01.0' % FINANCE_GROUP_ID,
                          'not_selectable_value_non_delay_aware_optional_advisers',
                          'developers',
                          'vendors'])
        # select the 10 days delay
        item.setOptionalAdvisers(('%s__rowid__2016-05-01.0' % FINANCE_GROUP_ID, ))
        item.at_post_edit_script()
        self.assertEquals(item.adviceIndex[FINANCE_GROUP_ID]['delay'], '10')
        # Managers, are also required to use change delay widget for 5/20 delays
        self.changeUser('pmManager')
        self.assertFalse(item.adapted().mayChangeDelayTo(5))
        self.assertTrue(item.adapted().mayChangeDelayTo(10))
        self.assertFalse(item.adapted().mayChangeDelayTo(20))

        # user having 'Modify portal content' may select 10 but not others
        self.changeUser('pmCreator1')
        self.assertFalse(item.adapted().mayChangeDelayTo(5))
        self.assertTrue(item.adapted().mayChangeDelayTo(10))
        self.assertFalse(item.adapted().mayChangeDelayTo(20))
        # may select 5 if using change delay widget
        # aka 'managing_available_delays' is found in the REQUEST
        self.request.set('managing_available_delays', True)
        self.assertTrue(item.adapted().mayChangeDelayTo(5))
        self.assertTrue(item.adapted().mayChangeDelayTo(10))
        self.assertFalse(item.adapted().mayChangeDelayTo(20))
        # change to 5 days
        item.setOptionalAdvisers(('%s__rowid__2016-05-01.1' % FINANCE_GROUP_ID, ))
        item.at_post_edit_script()
        self.assertEquals(item.adviceIndex[FINANCE_GROUP_ID]['delay'], '5')
        # could back to 10 days
        self.assertTrue(item.adapted().mayChangeDelayTo(5))
        self.assertTrue(item.adapted().mayChangeDelayTo(10))
        self.assertFalse(item.adapted().mayChangeDelayTo(20))
        # Managers have bypass when using change delay widget
        self.changeUser('pmManager')
        self.assertTrue(item.adapted().mayChangeDelayTo(5))
        self.assertTrue(item.adapted().mayChangeDelayTo(10))
        self.assertTrue(item.adapted().mayChangeDelayTo(20))

        # now, when item is 'wait_advices_from_prevalidated', finance advisers
        # may select the 20 days delay
        self.changeUser('pmReviewer1')
        self.proposeItem(item)
        self.do(item, 'wait_advices_from_prevalidated')
        self.changeUser('pmFinController')
        # may change to 20
        self.assertFalse(item.adapted().mayChangeDelayTo(5))
        self.assertFalse(item.adapted().mayChangeDelayTo(10))
        self.assertTrue(item.adapted().mayChangeDelayTo(20))
        # change to 20 days
        item.setOptionalAdvisers(('%s__rowid__2016-05-01.2' % FINANCE_GROUP_ID, ))
        item.at_post_edit_script()
        self.assertEquals(item.adviceIndex[FINANCE_GROUP_ID]['delay'], '20')
        # once to 20, may back to 10
        self.assertFalse(item.adapted().mayChangeDelayTo(5))
        self.assertTrue(item.adapted().mayChangeDelayTo(10))
        self.assertTrue(item.adapted().mayChangeDelayTo(20))

        # if item no more waiting finances advice, finances may not
        # change delay anymore
        self.do(item, 'backTo_proposed_to_refadmin_from_waiting_advices')
        self.assertFalse(item.adapted().mayChangeDelayTo(5))
        self.assertFalse(item.adapted().mayChangeDelayTo(10))
        self.assertFalse(item.adapted().mayChangeDelayTo(20))

        # if advice delay is set to 20, user have edit rights may not change it anymore
        self.changeUser('pmRefAdmin1')
        self.assertFalse(item.adapted().mayChangeDelayTo(5))
        self.assertFalse(item.adapted().mayChangeDelayTo(10))
        self.assertFalse(item.adapted().mayChangeDelayTo(20))

        # only a Manager will be able to change that delay now
        self.changeUser('pmManager')
        self.assertTrue(item.adapted().mayChangeDelayTo(5))
        self.assertTrue(item.adapted().mayChangeDelayTo(10))
        self.assertTrue(item.adapted().mayChangeDelayTo(20))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomAdvices, prefix='test_'))
    return suite
