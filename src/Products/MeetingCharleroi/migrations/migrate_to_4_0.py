# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingCharleroi')

from Products.PloneMeeting.migrations.migrate_to_4_0 import Migrate_To_4_0 as PMMigrate_To_4_0
from Products.MeetingCharleroi.config import FINANCE_GROUP_ID


# The migration class ----------------------------------------------------------
class Migrate_To_4_0(PMMigrate_To_4_0):

    def _createSearches(self):
        """Call MeetingConfig.createSearches."""
        logger.info('Calling MeetingConfig.createSearches...')
        for cfg in self.tool.objectValues('MeetingConfig'):
            cfg.createSearches(cfg._searchesInfo())
            cfg.updateCollectionColumns()
        # if search 'searchadviceproposedtoeditor' is in the last position
        # move it up 2 times
        cfg = self.tool.get('meeting-config-college')
        if cfg.searches.searches_items.objectIds()[-1] == 'searchadviceproposedtoeditor':
            cfg.searches.searches_items.folder_position_typeaware(position='up',
                                                                  id='searchadviceproposedtoeditor')
            cfg.searches.searches_items.folder_position_typeaware(position='up',
                                                                  id='searchadviceproposedtoeditor')
        logger.info('Done.')

    def _createFinancialEditorsPloneGroup(self):
        """Call MeetingGroup._createPloneGroupForAllSuffixes
           on the FINANCE_GROUP_ID MeetingGroup."""
        logger.info('Creating new Plone group for financial editors...')
        mGroup = self.tool.get(FINANCE_GROUP_ID)
        mGroup._createPloneGroupForAllSuffixes()
        logger.info('Done.')

    def run(self):
        # change self.profile_name that is reinstalled at the beginning of the PM migration
        self.profile_name = u'profile-Products.MeetingCharleroi:default'
        # call steps from Products.PloneMeeting
        PMMigrate_To_4_0.run(self)
        # now MeetingCharleroi specific steps
        logger.info('Migrating to MeetingCharleroi 4.0...')
        self._createSearches()
        self._createFinancialEditorsPloneGroup()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Reinstall Products.MeetingCharleroi and execute the Products.PloneMeeting migration;
       2) Call MeetingConfig.createSearches;
       3) Add Plone group 'financial editors' for FINANCE_GROUP_ID.
    '''
    migrator = Migrate_To_4_0(context)
    migrator.run()
    migrator.finish()
# ------------------------------------------------------------------------------
