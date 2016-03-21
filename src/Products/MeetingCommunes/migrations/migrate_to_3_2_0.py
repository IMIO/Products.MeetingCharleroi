# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('PloneMeeting')

from Acquisition import aq_base

from Products.PloneMeeting.profiles import MeetingFileTypeDescriptor
from Products.PloneMeeting.migrations import Migrator


# The migration class ----------------------------------------------------------
class Migrate_To_3_2_0(Migrator):

    def _addDefaultAdviceAnnexesFileTypes(self):
        '''Add some default MeetingFileType relatedTo 'advice' so we can add
           annexes on advices.'''
        logger.info('Addind default MeetingFileType relatedTo \'advice\'...')
        mfts = []
        mfts.append(MeetingFileTypeDescriptor(id='annexeAvis',
                                              title=u'Annexe à un avis',
                                              theIcon='attach.png',
                                              predefinedTitle='',
                                              relatedTo='advice',
                                              active=True))
        mfts.append(MeetingFileTypeDescriptor(id='annexeAvisLegal',
                                              title=u'Extrait article de loi',
                                              theIcon='legalAdvice.png',
                                              predefinedTitle='',
                                              relatedTo='advice',
                                              active=True))
        # find theIcon path so we can give it to MeetingConfig.addFileType
        mcProfilePath = [profile for profile in self.context.listProfileInfo() if 'id' in profile
                         and profile['id'] == u'Products.MeetingCommunes:default'][0]['path']
        # the icon are located in the example_fr/images folder
        mcProfilePath = mcProfilePath.replace('profiles/default', 'profiles/examples_fr')
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            for mft in mfts:
                if not hasattr(aq_base(cfg.meetingfiletypes), mft.id):
                    cfg.addFileType(mft, source=mcProfilePath)
        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingCommunes 3.2.0...')
        self._addDefaultAdviceAnnexesFileTypes()
        # reinstall so skins and so on are correct
        self.reinstall(profiles=[u'profile-Products.MeetingCommunes:default', ])
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Add some default MeetingFileType relatedTo 'advice' so we can add annexes on advices.
    '''
    Migrate_To_3_2_0(context).run()
# ------------------------------------------------------------------------------
