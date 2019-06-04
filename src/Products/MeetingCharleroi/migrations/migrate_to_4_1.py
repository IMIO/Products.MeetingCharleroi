# -*- coding: utf-8 -*-


from Products.MeetingCommunes.migrations.migrate_to_4_1 import Migrate_To_4_1 as MCMigrate_To_4_1

import logging


logger = logging.getLogger('MeetingCharleroi')


class Migrate_To_4_1(MCMigrate_To_4_1):

    def run(self):
        # reapply the actions.xml of collective.iconifiedcategory
        self.ps.runImportStepFromProfile('profile-collective.iconifiedcategory:default', 'actions')
        MCMigrate_To_4_1.run(self, profile_name=u'profile-Products.MeetingCharleroi:default')


def migrate(context):
    '''This migration will:

       1) Execute Products.MeetingCommunes migration.
    '''
    migrator = Migrate_To_4_1(context)
    migrator.run()
    migrator.finish()
