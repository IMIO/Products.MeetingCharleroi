# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingCharleroi')

from plone import api

from Products.PloneMeeting.migrations.migrate_to_3_4 import Migrate_To_3_4 as PMMigrate_To_3_4


# The migration class ----------------------------------------------------------
class Migrate_To_3_4(PMMigrate_To_3_4):

    def _cleanCDLD(self):
        """We removed things related to 'CDLD' finance advice, so:
           - remove the 'cdld-document-generate' from document_actions;
           - remove the MeetingConfig.CdldProposingGroup attribute.
        """
        logger.info('Removing CDLD related things...')
        doc_actions = self.portal.portal_actions.document_actions
        # remove the action from document_actions
        if 'cdld-document-generate' in doc_actions:
            doc_actions.manage_delObjects(ids=['cdld-document-generate', ])
        # clean the MeetingConfigs
        for cfg in self.tool.objectValues('MeetingConfig'):
            if hasattr(cfg, 'cdldProposingGroup'):
                delattr(cfg, 'cdldProposingGroup')
        logger.info('Done.')

    def _migrateItemPositiveDecidedStates(self):
        """Before, the states in which an item was auto sent to
           selected other meetingConfig was defined in a method
           'itemPositiveDecidedStates' now it is stored in MeetingConfig.itemAutoSentToOtherMCStates."""
        logger.info('Defining values for MeetingConfig.itemAutoSentToOtherMCStates...')
        for cfg in self.tool.objectValues('MeetingConfig'):
            cfg.setItemAutoSentToOtherMCStates(('accepted', 'accepted_but_modified', ))
        logger.info('Done.')

    def _after_reinstall(self):
        """Use that hook that is called just after the profile has been reinstalled by
           PloneMeeting, this way, we may launch some steps before PloneMeeting ones.
           Here we will update used workflows before letting PM do his job."""
        logger.info('Replacing old no more existing workflows...')
        for cfg in self.tool.objectValues('MeetingConfig'):
            # MeetingItem workflow
            if cfg.getItemWorkflow() == 'meetingitemcollege_workflow':
                cfg.setItemWorkflow('meetingitemcommunes_workflow')
                cfg._v_oldItemWorkflow = 'meetingitemcollege_workflow'
                wfAdaptations = list(cfg.getWorkflowAdaptations())
                if not 'no_publication' in wfAdaptations:
                    wfAdaptations.append('no_publication')
                if not 'no_global_observation' in wfAdaptations:
                    wfAdaptations.append('no_global_observation')
                cfg.setWorkflowAdaptations(wfAdaptations)
            if cfg.getItemWorkflow() == 'meetingitemcouncil_workflow':
                cfg.setItemWorkflow('meetingitemcommunes_workflow')
                cfg._v_oldItemWorkflow = 'meetingitemcouncil_workflow'
            # Meeting workflow
            if cfg.getMeetingWorkflow() == 'meetingcollege_workflow':
                cfg.setMeetingWorkflow('meetingcharleroi_workflow')
                cfg._v_oldMeetingWorkflow = 'meetingcollege_workflow'
            if cfg.getMeetingWorkflow() == 'meetingcouncil_workflow':
                cfg.setMeetingWorkflow('meetingcharleroi_workflow')
                cfg._v_oldMeetingWorkflow = 'meetingcouncil_workflow'
        # delete old unused workflows, aka every workflows containing 'college' or 'council'
        wfTool = api.portal.get_tool('portal_workflow')
        toDelete = [wfId for wfId in wfTool.listWorkflows()
                    if wfId.endswith(('meetingitemcollege_workflow',
                                      'meetingitemcouncil_workflow',
                                      'meetingcollege_workflow',
                                      'meetingcouncil_workflow'))]
        if toDelete:
            wfTool.manage_delObjects(toDelete)
        logger.info('Done.')

    def run(self):
        # change self.profile_name that is reinstalled at the beginning of the PM migration
        self.profile_name = u'profile-Products.MeetingCharleroi:default'
        # call steps from Products.PloneMeeting
        PMMigrate_To_3_4.run(self)
        # now MeetingLiege specific steps
        logger.info('Migrating to MeetingCharleroi 3.4...')
        self._cleanCDLD()
        self._migrateItemPositiveDecidedStates()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Reinstall Products.MeetingCharleroi and execute the Products.PloneMeeting migration;
       2) Clean CDLD attributes;
       3) Migrate positive decided states.
    '''
    migrator = Migrate_To_3_4(context)
    migrator.run()
    migrator.finish()
# ------------------------------------------------------------------------------
