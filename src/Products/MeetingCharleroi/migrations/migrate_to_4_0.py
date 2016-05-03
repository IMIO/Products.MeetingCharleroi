# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingCharleroi')

from Products.PloneMeeting.migrations.migrate_to_4_0 import Migrate_To_4_0 as PMMigrate_To_4_0


# The migration class ----------------------------------------------------------
class Migrate_To_4_0(PMMigrate_To_4_0):

    def _createSearches(self):
        """Call MeetingConfig.createSearches."""
        logger.info('Calling MeetingConfig.createSearches...')
        for cfg in self.tool.objectValues('MeetingConfig'):
            cfg.createSearches(cfg._searchesInfo())
        logger.info('Done.')

    def run(self):
        # change self.profile_name that is reinstalled at the beginning of the PM migration
        self.profile_name = u'profile-Products.MeetingCharleroi:default'
        # call steps from Products.PloneMeeting
        PMMigrate_To_4_0.run(self)
        # now MeetingCharleroi specific steps
        self._createSearches()
        logger.info('Migrating to MeetingCharleroi 4.0...')


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Reinstall Products.MeetingCharleroi and execute the Products.PloneMeeting migration;
       2) Call MeetingConfig.createSearches.
    '''
    migrator = Migrate_To_4_0(context)
    migrator.run()
    migrator.finish()
# ------------------------------------------------------------------------------
