# -*- coding: utf-8 -*-

from Products.MeetingCharleroi.tests.MeetingCharleroiTestCase import MeetingCharleroiTestCase
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.MeetingCommunes.tests.testWFAdaptations import testWFAdaptations as mctwfa


class testWFAdaptations(MeetingCharleroiTestCase, mctwfa):
    """See doc string in PloneMeeting.tests.testWFAdaptations."""

    def test_pm_WFA_availableWFAdaptations(self):
        """Test what are the available wfAdaptations."""
        # we removed the 'archiving' and 'creator_initiated_decisions' wfAdaptations
        self.assertEqual(
            sorted(self.meetingConfig.listWorkflowAdaptations().keys()),
            sorted([
                "only_creator_may_delete",
                "no_publication",
                "accepted_but_modified",
                "postpone_next_meeting",
                "mark_not_applicable",
                "removed",
                "removed_and_duplicated",
                "refused",
                "delayed",
                "pre_accepted",
                "return_to_proposing_group",
                "decide_item_when_back_to_meeting_from_returned_to_proposing_group",
                "hide_decisions_when_under_writing",
                "waiting_advices",
                "waiting_advices_proposing_group_send_back",
                "meetingmanager_correct_closed_meeting",
                "charleroi_return_to_any_state_when_prevalidated",
            ]),
        )

    def test_pm_Validate_workflowAdaptations_dependencies(self):
        """Bypass as all WFA are not available"""

    def test_pm_WFA_pre_validation(self):
        """Will not work as we have also a state before...
        Tested in testCustomWorkflows.py"""
        pass

    def test_pm_WFA_waiting_advices_unknown_state(self):
        """Bypass as we have more states from which we can return from waiting advice"""

    def test_pm_WFA_charleroi_return_to_any_state_when_prevalidated(self):
        """Test that permissions are correct when the WFA is enabled."""
        cfg = self.meetingConfig
        self.changeUser("siteadmin")
        cfg.setWorkflowAdaptations(())
        cfg.at_post_edit_script()
        itemWF = self.wfTool.getWorkflowsFor(cfg.getItemTypeName())[0]
        self.assertFalse("backToProposedFromPrevalidated" in itemWF.transitions)
        self.assertFalse("backToItemCreatedFromPrevalidated" in itemWF.transitions)
        # activate, needs the 'charleroi_return_to_any_state_when_prevalidated' WFA
        cfg.setWorkflowAdaptations(("charleroi_return_to_any_state_when_prevalidated",))
        cfg.at_post_edit_script()
        itemWF = self.wfTool.getWorkflowsFor(cfg.getItemTypeName())[0]
        self.assertTrue("backToProposedFromPrevalidated" in itemWF.transitions)
        self.assertTrue("backToItemCreatedFromPrevalidated" in itemWF.transitions)

        # test that transitions do the work
        self.changeUser("pmManager")
        item = self.create("MeetingItem")

        # back to proposed to servicehead
        self.do(item, "propose")
        self.do(item, "proposeToRefAdmin")
        self.do(item, "prevalidate")
        # MeetingMember can not trigger the transitions
        self.changeUser("pmCreator1")
        self.assertEqual(self.transitions(item), [])
        self.changeUser("pmManager")
        self.do(item, "backToProposedFromPrevalidated")
        self.assertEqual(item.query_state(), "proposed")

        # back to itemcreated
        self.do(item, "proposeToRefAdmin")
        self.do(item, "prevalidate")
        self.do(item, "backToItemCreatedFromPrevalidated")
        self.assertEqual(item.query_state(), "itemcreated")

    def _setItemToWaitingAdvices(self, item, transition=None):
        """We need to ask finances advice to be able to do the transition."""
        originalMember = self.member.getId()
        self.changeUser("siteadmin")
        self._configureFinancesAdvice(self.meetingConfig)
        self.changeUser(originalMember)
        item.setOptionalAdvisers(
            item.getOptionalAdvisers() + ("{0}__rowid__unique_id_002".format(finance_group_uid()),)
        )
        item.at_post_edit_script()
        if transition:
            self.do(item, transition)

    def test_pm_WFA_waiting_advices_with_prevalidation(self):
        """Bypass it's tested in testCustomWorkflow."""


    def _userAbleToBackFromWaitingAdvices(self, currentState):
        """Return username able to back from waiting advices."""
        if currentState == "prevalidated_waiting_advices":
            return "siteadmin"
        else:
            return super(testWFAdaptations, self)._userAbleToBackFromWaitingAdvices(currentState)


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testWFAdaptations, prefix="test_pm_"))
    return suite
