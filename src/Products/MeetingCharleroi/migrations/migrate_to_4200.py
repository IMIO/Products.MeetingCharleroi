# -*- coding: utf-8 -*-
from copy import deepcopy

from Products.MeetingCommunes.migrations.migrate_to_4200 import Migrate_To_4200 as MCMigrate_To_4200
from Products.MeetingCharleroi.config import CHARLEROI_COLLEGE_ITEM_WF_VALIDATION_LEVELS
from Products.MeetingCharleroi.config import CHARLEROI_COUNCIL_ITEM_WF_VALIDATION_LEVELS

import logging

from imio.helpers.content import richtextval
from imio.pyutils.utils import replace_in_list
from plone import api

logger = logging.getLogger("MeetingCharleroi")


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
        new.assembly_police = old.getRawAssemblyPolice() and \
            richtextval(old.getRawAssemblyPolice()) or None
        new.assembly_privacy_secret_absents = old.getRawAssemblyPrivacySecretAbsents() and \
            richtextval(old.getRawAssemblyPrivacySecretAbsents()) or None

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

    def _applyCustomMeetingSchemaPolicy(self):
        """
        Apply our custom meeting policy
        """
        portal_types = api.portal.get_tool('portal_types')
        portal_types["Meeting"].schema_policy = "custom_charleroi_schema_policy_meeting"
        for cfg in self.tool.objectValues("MeetingConfig"):
            MeetingTypeInfo = portal_types[cfg.getMeetingTypeName()]
            MeetingTypeInfo.schema_policy = "custom_charleroi_schema_policy_meeting"

    def run(self, profile_name="profile-Products.MeetingCharleroi:default", extra_omitted=[]):
        super(Migrate_To_4200, self).run(extra_omitted=extra_omitted)
        self._applyCustomMeetingSchemaPolicy()
        logger.info("Done migrating to MeetingCharleroi 4200...")


# The migration function -------------------------------------------------------
def migrate(context):
    """This migration function:
    1) Call PloneMeeting migration to 4200 and 4201;
    2) Apply our custom meeting policy
    """
    migrator = Migrate_To_4200(context)
    migrator.run()
    migrator.finish()
