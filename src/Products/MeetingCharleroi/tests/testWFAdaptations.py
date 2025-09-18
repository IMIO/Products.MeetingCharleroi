# -*- coding: utf-8 -*-

from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.MeetingCommunes.tests.testWFAdaptations import testWFAdaptations as mctwfa


class testWFAdaptations(MeetingCharleroiTestCase, mctwfa):
    """See doc string in PloneMeeting.tests.testWFAdaptations."""

    def _setItemToWaitingAdvices(self, item, transition=None):
        """We need to ask finances advice to be able to do the transition."""
        originalMember = self.member.getId()
        self.changeUser("siteadmin")
        self._configureCharleroiFinancesAdvice(self.meetingConfig)
        self.changeUser(originalMember)
        item.setOptionalAdvisers(
            item.getOptionalAdvisers() + ("{0}__rowid__unique_id_002".format(finance_group_uid()),)
        )
        item.at_post_edit_script()
        if transition:
            self.do(item, transition)

    def _userAbleToBackFromWaitingAdvices(self, currentState):
        """Return username able to back from waiting advices."""
        if currentState == "prevalidated_waiting_advices":
            return "siteadmin"
        else:
            return super(testWFAdaptations, self)._userAbleToBackFromWaitingAdvices(currentState)

    def test_pm_WFA_waiting_advices_with_prevalidation(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_WFA_waiting_advices_unknown_state(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_Validate_workflowAdaptations_removed_return_to_proposing_group_with_all_validations(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_WFA_return_to_proposing_group_with_all_validations(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_WFA_return_to_proposing_group_with_last_validation(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_WFA_waiting_advices_adviser_send_back(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_WFA_waiting_advices_from_before_last_val_level(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_WFA_waiting_advices_from_every_val_levels(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_WFA_waiting_advices_from_last_and_before_last_val_level(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_WFA_waiting_advices_from_last_val_level(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_WFA_waiting_advices_given_advices_required_to_validate(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass

    def test_pm_WFA_waiting_advices_adviser_may_validate(self):
        """Bypass as we overrided WAITING_ADVICES_FROM_STATES."""
        pass


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix="test_pm_"))
    return suite
