# -*- coding: utf-8 -*-

from Products.GenericSetup.tool import DEPENDENCY_STRATEGY_NEW
from Products.MeetingCommunes.migrations.migrate_to_4_1 import Migrate_To_4_1 as MCMigrate_To_4_1

import logging


logger = logging.getLogger('MeetingCharleroi')


class Migrate_To_4_1(MCMigrate_To_4_1):

    def run(self):
        # reapply the actions.xml of collective.iconifiedcategory
        self.ps.runImportStepFromProfile('profile-collective.iconifiedcategory:default', 'actions')
        super(Migrate_To_4_1, self).run(extra_omitted=['Products.MeetingCharleroi:default'])
        self.reinstall(profiles=[u'profile-Products.MeetingCharleroi:default'],
                       ignore_dependencies=True,
                       dependency_strategy=DEPENDENCY_STRATEGY_NEW)


def migrate(context):
    '''This migration will:

       1) Execute Products.MeetingCommunes migration.
    '''
    migrator = Migrate_To_4_1(context)
    migrator.run()
    migrator.finish()
