# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('PloneMeeting')

from Products.CMFCore.utils import getToolByName
from Products.PloneMeeting.migrations import Migrator
from Products.PloneMeeting.profiles import PodTemplateDescriptor


# The migration class ----------------------------------------------------------
class Migrate_To_3_3(Migrator):

    def _migrateItemDecisionReportTextAttributeOnConfigs(self):
        '''
          The attribute is now managed by the MeetingConfig.onTransitionFieldTransforms functionnality, so :
          - if it was used, migrate it to MeetingConfig.onTransitionFieldTransforms;
          - removes the obsolete 'itemDecisionReportText' attribute.'''
        logger.info('Removing obsolete attribute \'itemDecisionReportText\' of every MeetingConfigs...')
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if hasattr(cfg, 'itemDecisionReportText'):
                if cfg.itemDecisionReportText.raw.strip():
                    # attribute was used, migrate to MeetingConfig.onTransitionFieldTransforms
                    cfg.setOnTransitionFieldTransforms(
                        ({'transition': 'delay',
                          'field_name': 'MeetingItem.decision',
                          'tal_expression': cfg.itemDecisionReportText.raw.strip()},))
                delattr(cfg, 'itemDecisionReportText')
        logger.info('Done.')

    def _updateOnMeetingTransitionItemTransitionToTrigger(self):
        '''Set a value for each MeetingConfig.onMeetingTransitionItemTransitionToTrigger
           attribute so it behaves like before.'''
        logger.info('Updating attribute \'onMeetingTransitionItemTransitionToTrigger\' of every MeetingConfigs...')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            onMeetingTransitionItemTransitionToTrigger = cfg.getOnMeetingTransitionItemTransitionToTrigger()
            if not onMeetingTransitionItemTransitionToTrigger:
                meetingWFTransitions = wfTool.getWorkflowsFor(cfg.getMeetingTypeName())[0].transitions
                newValue = [{'meeting_transition': 'freeze',
                             'item_transition': 'itemfreeze'}, ]
                # if we have a 'publish' transition in the meeting workflow
                # we take it into account
                if 'publish' in meetingWFTransitions:
                    newValue.append({'meeting_transition': 'publish',
                                     'item_transition': 'itemfreeze'})
                    newValue.append({'meeting_transition': 'publish',
                                     'item_transition': 'itempublish'})
                # manage the 'decide' meeting transition
                newValue.append({'meeting_transition': 'decide',
                                 'item_transition': 'itemfreeze'})
                if 'publish' in meetingWFTransitions:
                    newValue.append({'meeting_transition': 'decide',
                                     'item_transition': 'itempublish'})
                if 'publish_decisions' in meetingWFTransitions:
                    newValue.append({'meeting_transition': 'publish_decisions',
                                     'item_transition': 'itemfreeze'})
                    if 'publish' in meetingWFTransitions:
                        newValue.append({'meeting_transition': 'publish_decisions',
                                         'item_transition': 'itempublish'})
                    newValue.append({'meeting_transition': 'publish_decisions',
                                     'item_transition': 'accept'})
                # manage the 'close' meeting transition
                newValue.append({'meeting_transition': 'close',
                                 'item_transition': 'itemfreeze'})
                if 'publish' in meetingWFTransitions:
                    newValue.append({'meeting_transition': 'close',
                                     'item_transition': 'itempublish'})
                newValue.append({'meeting_transition': 'close',
                                 'item_transition': 'accept'})
                cfg.setOnMeetingTransitionItemTransitionToTrigger(newValue)
        logger.info('Done.')

    def _addCDLDTopics(self):
        '''
          Add CDLD topics for synthesis of all advice.'''
        logger.info('Adding CDLD topics...')
        # add some extra topics to each MeetingConfig
        topicsInfo = (
            # Items for cdld synthesis
            ('searchcdlditems',
            (('Type', 'ATPortalTypeCriterion', ('MeetingItem',)),
             ),
            'created',
            'searchCDLDItems',
            "python: '%s_budgetimpacteditors' % here.portal_plonemeeting.getMeetingConfig(here)"
            ".getId() in member.getGroups() or here.portal_plonemeeting.isManager(here)", ),
        )

        site = self.portal
        for cfg in site.portal_plonemeeting.objectValues('MeetingConfig'):
            cfg.createTopics(topicsInfo)
            # add template for cdld
            cdldTemplate = PodTemplateDescriptor('generate-cdld', 'generate CDLD')
            cdldTemplate.podTemplate = 'synthese cdld.odt'
            cdldTemplate.podCondition = 'python:False'
            cfg.addPodTemplate(cdldTemplate,
                               site.portal_setup.getProfileInfo(u'profile-Products.MeetingCommunes:examples_fr')['path'])
        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingCommunes 3.3...')
        self._migrateItemDecisionReportTextAttributeOnConfigs()
        self._updateOnMeetingTransitionItemTransitionToTrigger()
        self._addCDLDTopics()
        # reinstall so skins and so on are correct
        self.reinstall(profiles=[u'profile-Products.MeetingCommunes:default', ])
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Remove obsolete attribut 'itemDecisionReportText' from every meetingConfigs;
       2) Reinstall Products.MeetingCommunes so skin and so on are correct.
    '''
    Migrate_To_3_3(context).run()
# ------------------------------------------------------------------------------
