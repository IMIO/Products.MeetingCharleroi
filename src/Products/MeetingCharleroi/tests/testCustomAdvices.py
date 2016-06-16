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


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomAdvices, prefix='test_'))
    return suite
