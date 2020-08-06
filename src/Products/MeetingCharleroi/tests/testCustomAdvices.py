# -*- coding: utf-8 -*-

from imio.helpers.content import get_vocab
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCharleroi.utils import finance_group_uid
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


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
        item.setOptionalAdvisers(('{0}__rowid__unique_id_002'.format(finance_group_uid()), ))
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
            **{'advice_group': finance_group_uid(),
               'advice_type': u'positive_finance',
               'advice_comment': RichTextValue(u'My comment finances'),
               'advice_category': u'acquisitions'})
        # reindexed when advice added
        itemUID = item.UID()
        self.assertEqual(catalog(meta_type='MeetingItem',
                                 financesAdviceCategory=advice.advice_category)[0].UID,
                         itemUID)
        # reindexed when advice edited
        advice.advice_category = u'attributions'
        # notify modified
        notify(ObjectModifiedEvent(advice))
        self.assertEqual(catalog(meta_type='MeetingItem',
                                 financesAdviceCategory=advice.advice_category)[0].UID,
                         itemUID)
        # reindexed when advice deleted
        self.portal.restrictedTraverse('@@delete_givenuid')(advice.UID())
        self.assertEqual(len(catalog(meta_type='MeetingItem',
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
        optional_advisers = get_vocab(
            item, 'Products.PloneMeeting.vocabularies.itemoptionaladvicesvocabulary')
        self.assertEqual([term.token for term in optional_advisers],
                         ['not_selectable_value_delay_aware_optional_advisers',
                          '{0}__rowid__unique_id_002'.format(finance_group_uid()),
                          'not_selectable_value_non_delay_aware_optional_advisers',
                          self.developers_uid,
                          self.vendors_uid])
        # select the 10 days delay
        item.setOptionalAdvisers(('%s__rowid__unique_id_002' % finance_group_uid(), ))
        item.at_post_edit_script()
        self.assertEqual(item.adviceIndex[finance_group_uid()]['delay'], '10')
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
        item.setOptionalAdvisers(('{0}__rowid__unique_id_003'.format(finance_group_uid()), ))
        item.at_post_edit_script()
        self.assertEqual(item.adviceIndex[finance_group_uid()]['delay'], '5')
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
        item.setOptionalAdvisers(('{0}__rowid__unique_id_004'.format(finance_group_uid()), ))
        item.at_post_edit_script()
        self.assertEqual(item.adviceIndex[finance_group_uid()]['delay'], '20')
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
