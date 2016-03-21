# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.PloneMeeting.profiles import MeetingFileTypeDescriptor
from Products.PloneMeeting.profiles import CategoryDescriptor
from Products.PloneMeeting.profiles import PodTemplateDescriptor
from Products.PloneMeeting.profiles import UserDescriptor
from Products.PloneMeeting.profiles import GroupDescriptor
from Products.PloneMeeting.profiles import MeetingConfigDescriptor
from Products.PloneMeeting.profiles import PloneMeetingConfiguration

today = DateTime().strftime('%Y/%m/%d')

# File types -------------------------------------------------------------------
annexe = MeetingFileTypeDescriptor('annexe', 'Annexe', 'attach.png', '')
annexeDecision = MeetingFileTypeDescriptor('annexeDecision', 'Annexe à la décision', 'attach.png', '', 'item_decision')
annexeAvis = MeetingFileTypeDescriptor('annexeAvis', 'Annexe à un avis',
                                       'attach.png', '', 'advice')

# Categories -------------------------------------------------------------------
categories = [CategoryDescriptor('category1', 'Catégorie 1'),
              CategoryDescriptor('category2', 'Catégorie 2'),
              CategoryDescriptor('category3', 'Catégorie 3'),
              CategoryDescriptor('category4', 'Catégorie 4'),
              CategoryDescriptor('category5', 'Catégorie 5')]

# Pod templates ----------------------------------------------------------------
agendaTemplate = PodTemplateDescriptor('oj', 'Ordre du jour')
agendaTemplate.odt_file = '../../examples_fr/templates/oj.odt'
agendaTemplate.pod_formats = ['odt', 'pdf', ]
agendaTemplate.pod_portal_types = ['MeetingCA']
agendaTemplate.tal_condition = 'python:tool.isManager(here)'

decisionsTemplate = PodTemplateDescriptor('pv', 'Procès-verbal')
decisionsTemplate.odt_file = '../../examples_fr/templates/pv.odt'
decisionsTemplate.pod_formats = ['odt', 'pdf', ]
decisionsTemplate.pod_portal_types = ['MeetingCA']
decisionsTemplate.tal_condition = 'python:tool.isManager(here)'

itemProjectTemplate = PodTemplateDescriptor('projet-deliberation', 'Projet délibération')
itemProjectTemplate.odt_file = '../../examples_fr/templates/projet-deliberation.odt'
itemProjectTemplate.pod_formats = ['odt', 'pdf', ]
itemProjectTemplate.pod_portal_types = ['MeetingItemCA']
itemProjectTemplate.tal_condition = 'python:not here.hasMeeting()'

itemTemplate = PodTemplateDescriptor('deliberation', 'Délibération')
itemTemplate.odt_file = '../../examples_fr/templates/deliberation.odt'
itemTemplate.pod_formats = ['odt', 'pdf', ]
itemTemplate.pod_portal_types = ['MeetingItemCA']
itemTemplate.tal_condition = 'python:here.hasMeeting()'

caTemplates = [agendaTemplate, decisionsTemplate,
               itemProjectTemplate, itemTemplate]

# Users and groups -------------------------------------------------------------
dgen = UserDescriptor('dgen', [], email="test@test.be", fullname="Henry Directeur")
dfin = UserDescriptor('dfin', [], email="test@test.be", fullname="Directeur Financier")
agentInfo = UserDescriptor('agentInfo', [], email="test@test.be", fullname="Agent Service Informatique")
agentCompta = UserDescriptor('agentCompta', [], email="test@test.be", fullname="Agent Service Comptabilité")
agentPers = UserDescriptor('agentPers', [], email="test@test.be", fullname="Agent Service du Personnel")
chefPers = UserDescriptor('chefPers', [], email="test@test.be", fullname="Chef Personnel")
chefCompta = UserDescriptor('chefCompta', [], email="test@test.be", fullname="Chef Comptabilité")

groups = [GroupDescriptor('dirgen', 'Directeur Général', 'DG'),
          GroupDescriptor('secretariat', 'Secrétariat communal', 'Secr'),
          GroupDescriptor('informatique', 'Service informatique', 'Info'),
          GroupDescriptor('personnel', 'Service du personnel', 'Pers'),
          GroupDescriptor('dirfin', 'Directeur Financier', 'DF'),
          GroupDescriptor('comptabilite', 'Service comptabilité', 'Compt')]

# MeetingManager
groups[0].creators.append(dgen)
groups[0].reviewers.append(dgen)
groups[0].observers.append(dgen)
groups[0].advisers.append(dgen)

groups[1].creators.append(dgen)
groups[1].reviewers.append(dgen)
groups[1].observers.append(dgen)
groups[1].advisers.append(dgen)

groups[2].creators.append(agentInfo)
groups[2].creators.append(dgen)
groups[2].reviewers.append(agentInfo)
groups[2].reviewers.append(dgen)
groups[2].observers.append(agentInfo)
groups[2].advisers.append(agentInfo)

groups[3].creators.append(agentPers)
groups[3].observers.append(agentPers)
groups[3].creators.append(dgen)
groups[3].reviewers.append(dgen)
groups[3].creators.append(chefPers)
groups[3].reviewers.append(chefPers)
groups[3].observers.append(chefPers)

groups[4].creators.append(dfin)
groups[4].reviewers.append(dfin)
groups[4].observers.append(dfin)
groups[4].advisers.append(dfin)

groups[5].creators.append(agentCompta)
groups[5].creators.append(chefCompta)
groups[5].creators.append(dfin)
groups[5].creators.append(dgen)
groups[5].reviewers.append(chefCompta)
groups[5].reviewers.append(dfin)
groups[5].reviewers.append(dgen)
groups[5].observers.append(agentCompta)
groups[5].advisers.append(chefCompta)
groups[5].advisers.append(dfin)

# Meeting configurations -------------------------------------------------------
# ca
caMeeting = MeetingConfigDescriptor(
    'ca', 'Conseil d\'Administration',
    'Conseil d\'Administration')
caMeeting.meetingManagers = ['dgen', ]
caMeeting.assembly = 'Pierre Dupont - Président,\n' \
                     'Charles Exemple - Premier membre assemblée,\n' \
                     'Luc Un, Luc Deux, Luc Trois - Membres,\n' \
                     'Jacqueline Exemple, Observateur'
caMeeting.signatures = 'Le Secrétaire communal\nPierre Dupont\nLe Bourgmestre\nCharles Exemple'
caMeeting.certifiedSignatures = [
    {'signatureNumber': '1',
     'name': u'Vraiment Présent',
     'function': u'Le Secrétaire communal',
     'date_from': '',
     'date_to': '',
     },
    {'signatureNumber': '2',
     'name': u'Charles Exemple',
     'function': u'Le Bourgmestre',
     'date_from': '',
     'date_to': '',
     },
]
caMeeting.places = """Place1\r
Place2\r
Place3\r"""
caMeeting.categories = categories
caMeeting.shortName = 'CA'
caMeeting.meetingFileTypes = [annexe, annexeDecision, annexeAvis]
caMeeting.usedItemAttributes = ['detailedDescription',
                                'budgetInfos',
                                'observations',
                                'toDiscuss',
                                'itemAssembly',
                                'itemIsSigned', ]
caMeeting.usedMeetingAttributes = ['startDate', 'endDate', 'signatures', 'assembly', 'place', 'observations', ]
caMeeting.recordMeetingHistoryStates = []
caMeeting.xhtmlTransformFields = ()
caMeeting.xhtmlTransformTypes = ()
caMeeting.itemWorkflow = 'meetingitemcommunes_workflow'
caMeeting.meetingWorkflow = 'meetingcommunes_workflow'
caMeeting.itemConditionsInterface = 'Products.MeetingCommunes.interfaces.IMeetingItemCollegeWorkflowConditions'
caMeeting.itemActionsInterface = 'Products.MeetingCommunes.interfaces.IMeetingItemCollegeWorkflowActions'
caMeeting.meetingConditionsInterface = 'Products.MeetingCommunes.interfaces.IMeetingCollegeWorkflowConditions'
caMeeting.meetingActionsInterface = 'Products.MeetingCommunes.interfaces.IMeetingCollegeWorkflowActions'
caMeeting.transitionsToConfirm = ['MeetingItem.delay', ]
caMeeting.meetingTopicStates = ('created', 'frozen')
caMeeting.decisionTopicStates = ('decided', 'closed')
caMeeting.enforceAdviceMandatoriness = False
caMeeting.insertingMethodsOnAddItem = ({'insertingMethod': 'on_proposing_groups',
                                        'reverse': '0'}, )
caMeeting.recordItemHistoryStates = []
caMeeting.maxShownMeetings = 5
caMeeting.maxDaysDecisions = 60
caMeeting.meetingAppDefaultView = 'searchmyitems'
caMeeting.useAdvices = True
caMeeting.itemAdviceStates = ('validated',)
caMeeting.itemAdviceEditStates = ('validated',)
caMeeting.itemAdviceViewStates = ('validated',
                                  'presented',
                                  'itemfrozen',
                                  'accepted',
                                  'refused',
                                  'accepted_but_modified',
                                  'delayed',
                                  'pre_accepted',)
caMeeting.usedAdviceTypes = ['positive', 'positive_with_remarks', 'negative', 'nil', ]
caMeeting.enableAdviceInvalidation = False
caMeeting.itemAdviceInvalidateStates = []
caMeeting.customAdvisers = []
caMeeting.itemPowerObserversStates = ('itemfrozen',
                                      'accepted',
                                      'delayed',
                                      'refused',
                                      'accepted_but_modified',
                                      'pre_accepted')
caMeeting.itemDecidedStates = ['accepted', 'refused', 'delayed', 'accepted_but_modified', 'pre_accepted']
caMeeting.workflowAdaptations = ['no_publication', 'no_global_observation', 'return_to_proposing_group']
caMeeting.transitionsForPresentingAnItem = ('propose', 'validate', 'present', )
caMeeting.onTransitionFieldTransforms = (
    ({'transition': 'delay',
      'field_name': 'MeetingItem.decision',
      'tal_expression': "string:<p>Le Comité décide de reporter le point.</p>"},))
caMeeting.onMeetingTransitionItemTransitionToTrigger = ({'meeting_transition': 'freeze',
                                                         'item_transition': 'itemfreeze'},

                                                        {'meeting_transition': 'decide',
                                                         'item_transition': 'itemfreeze'},

                                                        {'meeting_transition': 'publish_decisions',
                                                         'item_transition': 'itemfreeze'},
                                                        {'meeting_transition': 'publish_decisions',
                                                         'item_transition': 'accept'},

                                                        {'meeting_transition': 'close',
                                                         'item_transition': 'itemfreeze'},
                                                        {'meeting_transition': 'close',
                                                         'item_transition': 'accept'},)
caMeeting.meetingPowerObserversStates = ('frozen', 'decided', 'closed')
caMeeting.powerAdvisersGroups = ('dirgen', 'dirfin', )
caMeeting.itemBudgetInfosStates = ('proposed', 'validated', 'presented')
caMeeting.useCopies = True
caMeeting.selectableCopyGroups = [groups[0].getIdSuffixed('reviewers'),
                                  groups[1].getIdSuffixed('reviewers'),
                                  groups[2].getIdSuffixed('reviewers'),
                                  groups[4].getIdSuffixed('reviewers')]
caMeeting.podTemplates = caTemplates
caMeeting.meetingConfigsToCloneTo = []
caMeeting.recurringItems = []
caMeeting.itemTemplates = []

data = PloneMeetingConfiguration(meetingFolderTitle='Mes séances',
                                 meetingConfigs=(caMeeting, ),
                                 groups=groups)
data.enableUserPreferences = False
# ------------------------------------------------------------------------------
