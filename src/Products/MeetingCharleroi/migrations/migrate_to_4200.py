# -*- coding: utf-8 -*-
from copy import deepcopy

from Products.MeetingCommunes.migrations.migrate_to_4200 import Migrate_To_4200 as MCMigrate_To_4200
from Products.MeetingCharleroi.config import CHARLEROI_COLLEGE_ITEM_WF_VALIDATION_LEVELS
from Products.MeetingCharleroi.config import CHARLEROI_COUNCIL_ITEM_WF_VALIDATION_LEVELS

import logging

from imio.pyutils.utils import replace_in_list

logger = logging.getLogger("MeetingSeraing")


class Migrate_To_4200(MCMigrate_To_4200):
    def _hook_before_meeting_to_dx(self):
        super(Migrate_To_4200, self)._hook_before_meeting_to_dx()
        for cfg in self.tool.objectValues("MeetingConfig"):
            used_attrs = cfg.getUsedMeetingAttributes()
            used_attrs = replace_in_list(used_attrs, "assemblyPolice", "assembly_police")
            used_attrs = replace_in_list(
                used_attrs, "assemblyPrivacySecretAbsents", "assembly_privacy_secret_absents"
            )
            cfg.setUsedMeetingAttributes(used_attrs)

    def _hook_custom_meeting_to_dx(self, old, new):
        new.assembly_police = deepcopy(old.assemblyPolice)
        new.assembly_privacy_secret_absents = deepcopy(old.assemblyPrivacySecretAbsents)

    def _doConfigureItemWFValidationLevels(self, cfg):
        """Apply correct itemWFValidationLevels and fix WFAs."""
        stored_itemWFValidationLevels = getattr(cfg, "itemWFValidationLevels", [])
        if not stored_itemWFValidationLevels and cfg.id == "meeting-config-college":
            cfg.setItemWFValidationLevels(CHARLEROI_COLLEGE_ITEM_WF_VALIDATION_LEVELS)
        if not stored_itemWFValidationLevels and cfg.id == "meeting-config-council":
            cfg.setItemWFValidationLevels(CHARLEROI_COUNCIL_ITEM_WF_VALIDATION_LEVELS)

        # charleroi_add_refadmin has been replaced by itemWFValidationLevels
        if "charleroi_add_refadmin" in cfg.getWorkflowAdaptations():
            cfg.setWorkflowAdaptations(
                tuple(wfa for wfa in cfg.getWorkflowAdaptations() if wfa != "charleroi_add_refadmin")
            )
        super(Migrate_To_4200, self)._doConfigureItemWFValidationLevels(cfg)

    def run(self, profile_name="profile-Products.MeetingCharleroi:default", extra_omitted=[]):
        super(Migrate_To_4200, self).run(extra_omitted=extra_omitted)

        logger.info("Done migrating to MeetingCharleroi 4200...")


# The migration function -------------------------------------------------------
def migrate(context):
    """This migration function:

    1) Change MeetingConfig workflows to use meeting_workflow/meetingitem_workflow;
    2) Call PloneMeeting migration to 4200 and 4201;
    3) In _after_reinstall hook, adapt items and meetings workflow_history
       to reflect new defined workflow done in 1);
    4) Add new searches.
    """
    migrator = Migrate_To_4200(context)
    migrator.run()
    migrator.finish()
