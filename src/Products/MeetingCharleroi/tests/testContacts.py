from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCommunes.tests.testContacts import testContacts as mctc


class testContacts(mctc, MeetingCharleroiTestCase):
    '''Tests the contacts related methods.'''

    def setUp(self):
        ''' '''
        super(testContacts, self).setUp()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testContacts, prefix='test_pm_'))
    return suite