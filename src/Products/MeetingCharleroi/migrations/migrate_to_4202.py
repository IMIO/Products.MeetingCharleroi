# -*- coding: utf-8 -*-

from plone import api
from Products.PloneMeeting.migrations import Migrator

import logging


logger = logging.getLogger("MeetingCharleroi")


class Migrate_To_4202(Migrator):

    def _removeProposedToRefAdminItemCollegeState(self):
        """State "proposed_to_refadmin" is removed for College items."""
        logger.info('Removing "proposed_to_refadmin" state for College items...')
        catalog = api.portal.get_tool('portal_catalog')
        # make sure no more items in state "proposed_to_refadmin",
        # moved back to "proposed" if any
        brains = catalog(portal_type="MeetingItemCollege", review_state="proposed_to_refadmin")
        for brain in brains:
            logger.info("Item at \"{0}\" was set back to review_state \"Proposed\"".format(brain.getPath()))
            item = brain.getObject()
            self.portal.portal_workflow.doActionFor(
                item,
                'backToProposed',
                comment="Automatically set to \"Proposed\" while removing state \"Proposed to refadmin\".")
        # clean MeetingConfig College
        cfg = self.tool.get("meeting-config-college")
        # itemWFValidationLevels
        review_states = cfg.getItemWFValidationLevels(data='state', only_enabled=True)
        if "proposed_to_refadmin" in review_states:
            item_wf_val_levels = list(cfg.getItemWFValidationLevels())
            item_wf_val_levels.pop(review_states.index("proposed_to_refadmin"))
            cfg.setItemWFValidationLevels(item_wf_val_levels)
        # transitionsToConfirm
        transitions_to_confirm = list(cfg.getTransitionsToConfirm())
        if "MeetingItem.proposeToRefAdmin" in transitions_to_confirm:
            transitions_to_confirm.remove("MeetingItem.proposeToRefAdmin")
        if "MeetingItem.backToProposedToRefAdmin" in transitions_to_confirm:
            transitions_to_confirm.remove("MeetingItem.backToProposedToRefAdmin")
        cfg.setTransitionsToConfirm(transitions_to_confirm)
        # searchitemsproposedtorefadmin
        collection = cfg.searches.searches_items.get('searchitemsproposedtorefadmin')
        if collection:
            collection.enabled = False
        # remove from ITEM_WF_STATE_ATTRS/ITEM_WF_TRANSITION_ATTRS
        self.update_cfg_wf_attrs(
            to_remove=['proposed_to_refadmin'],
            cfg_ids=["meeting-config-college"])
        self.update_cfg_wf_attrs(
            is_review_state=False,
            to_remove=['proposeToRefAdmin'],
            cfg_ids=["meeting-config-college"])
        # remove "suffix_proposing_group_prereviewers" and "suffix_profile_prereviewers"
        # from MeetingConfig attrs
        for attr_name in ['adviceAnnexConfidentialVisibleFor',
                          'adviceAnnexConfidentialVisibleFor',
                          'meetingAnnexConfidentialVisibleFor',
                          'itemInternalNotesEditableBy']:
            values = list(getattr(cfg, attr_name))
            if "suffix_proposing_group_prereviewers" in values:
                values.remove("suffix_proposing_group_prereviewers")
            if "suffix_profile_prereviewers" in values:
                values.remove("suffix_profile_prereviewers")
            setattr(cfg, attr_name, values)
        self.reloadMeetingConfigs(full=True, cfg_ids=["meeting-config-college"])
        logger.info('Done.')

    def run(self,
            profile_name=u'profile-Products.MeetingCharleroi:default',
            extra_omitted=[]):

        # this will upgrade Products.PloneMeeting and dependencies
        self.upgradeAll(omit=[profile_name.replace('profile-', '')])
        self._removeProposedToRefAdminItemCollegeState()


# The migration function -------------------------------------------------------
def migrate(context):
    """This migration function:

       1) Remove College item state "proposed_to_refadmin".
    """
    migrator = Migrate_To_4202(context)
    migrator.run()
    migrator.finish()
