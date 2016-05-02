# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingCharleroi')

from Products.PloneMeeting.migrations.migrate_to_4_0 import Migrate_To_4_0 as PMMigrate_To_4_0


# The migration class ----------------------------------------------------------
class Migrate_To_4_0(PMMigrate_To_4_0):

    def run(self):
        # change self.profile_name that is reinstalled at the beginning of the PM migration
        self.profile_name = u'profile-Products.MeetingCharleroi:default'
        # call steps from Products.PloneMeeting
        PMMigrate_To_4_0.run(self)
        # now MeetingLiege specific steps
        logger.info('Migrating to MeetingCharleroi 4.0...')


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Reinstall Products.MeetingCharleroi and execute the Products.PloneMeeting migration.
    '''
    migrator = Migrate_To_4_0(context)
    migrator.run()
    migrator.finish()
# ------------------------------------------------------------------------------
