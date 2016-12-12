# -*- coding: utf-8 -*-

from DateTime import DateTime

from Products.PloneMeeting.config import DEFAULT_LIST_TYPES
from Products.PloneMeeting.profiles import AnnexTypeDescriptor
from Products.PloneMeeting.profiles import CategoryDescriptor
from Products.PloneMeeting.profiles import GroupDescriptor
from Products.PloneMeeting.profiles import ItemAnnexTypeDescriptor
from Products.PloneMeeting.profiles import ItemTemplateDescriptor
from Products.PloneMeeting.profiles import MeetingConfigDescriptor
from Products.PloneMeeting.profiles import MeetingUserDescriptor
from Products.PloneMeeting.profiles import PloneMeetingConfiguration
from Products.PloneMeeting.profiles import PodTemplateDescriptor
from Products.PloneMeeting.profiles import RecurringItemDescriptor
from Products.PloneMeeting.profiles import UserDescriptor

from Products.MeetingCharleroi.config import COMMUNICATION_CAT_ID
from Products.MeetingCharleroi.config import POLICE_GROUP_ID

today = DateTime().strftime('%Y/%m/%d')

# File types -------------------------------------------------------------------
annexe = ItemAnnexTypeDescriptor('annexe', 'Annexe', u'attach.png', '')
annexeBudget = ItemAnnexTypeDescriptor('annexeBudget', 'Article Budgétaire', u'budget.png', '')
annexeCahier = ItemAnnexTypeDescriptor('annexeCahier', 'Cahier des Charges', u'cahier.gif', '')
annexeDecision = ItemAnnexTypeDescriptor('annexeDecision', 'Annexe à la décision', u'attach.png', '', 'item_decision')
annexeAvis = AnnexTypeDescriptor('annexeAvis', 'Annexe à un avis', u'attach.png', '', 'advice')
annexeAvisLegal = AnnexTypeDescriptor('annexeAvisLegal', 'Extrait article de loi', u'legalAdvice.png', '', 'advice')

# Categories -------------------------------------------------------------------
recurring = CategoryDescriptor('recurrents', 'Récurrents')
categories = [recurring,
              CategoryDescriptor('divers',
                                 'Divers',
                                 description='Bourgmestre|P. Magnette'),
              CategoryDescriptor('affaires-juridiques',
                                 'Affaires juridiques',
                                 description='Bourgmestre|P. Magnette'),
              CategoryDescriptor('occupation-privative',
                                 'Occupation privative',
                                 description='Bourgmestre|P. Magnette'),
              CategoryDescriptor('dispenses-de-service',
                                 'Dispenses de service',
                                 description='Bourgmestre|P. Magnette'),
              CategoryDescriptor('remboursement',
                                 'Remboursement',
                                 description='Bourgmestre|P. Magnette'),
              CategoryDescriptor('pop-inscription-office',
                                 'Population – Inscriptions d’office',
                                 description='L’Echevine|F. Daspremont'),
              CategoryDescriptor('non-valeurs',
                                 'Non-valeurs',
                                 description='L’Echevine|F. Daspremont'),
              CategoryDescriptor('droits-contates',
                                 'Droits constatés',
                                 description='L’Echevine|F. Daspremont'),
              CategoryDescriptor('deplacements-etranger',
                                 'Déplacement à l’étranger',
                                 description='L’Echevine|J. Patte'),
              CategoryDescriptor('partenariat',
                                 'Partenariat',
                                 description='L’Echevine|J. Patte'),
              CategoryDescriptor('fin-de-bail',
                                 'Fin de bail',
                                 description='L’Echevin|E. Goffart'),
              CategoryDescriptor('droit-constates',
                                 'Droits constatés',
                                 description='L’Echevin|E. Goffart'),
              CategoryDescriptor(COMMUNICATION_CAT_ID,
                                 'Communication',
                                 description=''),
              ]

# Pod templates ----------------------------------------------------------------
agendaTemplate = PodTemplateDescriptor('oj', 'Ordre du jour')
agendaTemplate.odt_file = 'oj.odt'
agendaTemplate.pod_formats = ['odt', 'pdf', ]
agendaTemplate.pod_portal_types = ['MeetingCollege']
agendaTemplate.tal_condition = 'python:tool.isManager(here)'

decisionsTemplate = PodTemplateDescriptor('pv', 'Procès-verbal')
decisionsTemplate.odt_file = 'pv.odt'
decisionsTemplate.pod_formats = ['odt', 'pdf', ]
decisionsTemplate.pod_portal_types = ['MeetingCollege']
decisionsTemplate.tal_condition = 'python:tool.isManager(here)'

itemProjectTemplate = PodTemplateDescriptor('projet-deliberation', 'Projet délibération')
itemProjectTemplate.odt_file = 'projet-deliberation.odt'
itemProjectTemplate.pod_formats = ['odt', 'pdf', ]
itemProjectTemplate.pod_portal_types = ['MeetingItemCollege']
itemProjectTemplate.tal_condition = 'python:not here.hasMeeting()'

itemTemplate = PodTemplateDescriptor('deliberation', 'Délibération')
itemTemplate.odt_file = 'deliberation.odt'
itemTemplate.pod_formats = ['odt', 'pdf', ]
itemTemplate.pod_portal_types = ['MeetingItemCollege']
itemTemplate.tal_condition = 'python:here.hasMeeting()'

dfAdvicesTemplate = PodTemplateDescriptor('synthese-avis-df', 'Synthèse Avis DF', dashboard=True)
dfAdvicesTemplate.odt_file = 'synthese-avis-df.odt'
dfAdvicesTemplate.pod_formats = ['odt', 'pdf', ]
dfAdvicesTemplate.dashboard_collections_ids = ['searchitemswithfinanceadvice']

dashboardTemplate = PodTemplateDescriptor('recapitulatif', 'Récapitulatif', dashboard=True)
dashboardTemplate.odt_file = 'recapitulatif-tb.odt'
dashboardTemplate.tal_condition = 'python: context.absolute_url().endswith("/searches_items")'

historyTemplate = PodTemplateDescriptor('historique', 'Historique')
historyTemplate.odt_file = 'history.odt'
historyTemplate.pod_formats = ['odt', 'pdf', ]
historyTemplate.pod_portal_types = ['MeetingItemCollege']

collegeTemplates = [agendaTemplate, decisionsTemplate,
                    itemProjectTemplate, itemTemplate,
                    dfAdvicesTemplate, dashboardTemplate,
                    historyTemplate]

# Pod templates ----------------------------------------------------------------
agendaCouncilTemplate = PodTemplateDescriptor('oj', 'Ordre du jour')
agendaCouncilTemplate.odt_file = 'council-oj.odt'
agendaCouncilTemplate.pod_formats = ['odt', 'pdf', ]
agendaCouncilTemplate.pod_portal_types = ['MeetingCouncil']
agendaCouncilTemplate.tal_condition = 'python:tool.isManager(here)'

decisionsCouncilTemplate = PodTemplateDescriptor('pv', 'Procès-verbal')
decisionsCouncilTemplate.odt_file = 'council-pv.odt'
decisionsCouncilTemplate.pod_formats = ['odt', 'pdf', ]
decisionsCouncilTemplate.pod_portal_types = ['MeetingCouncil']
decisionsCouncilTemplate.tal_condition = 'python:tool.isManager(here)'

itemCouncilRapportTemplate = PodTemplateDescriptor('rapport', 'Rapport')
itemCouncilRapportTemplate.odt_file = 'council-rapport.odt'
itemCouncilRapportTemplate.pod_formats = ['odt', 'pdf', ]
itemCouncilRapportTemplate.pod_portal_types = ['MeetingItemCouncil']
itemCouncilRapportTemplate.tal_condition = ''

itemCouncilProjectTemplate = PodTemplateDescriptor('projet-deliberation', 'Projet délibération')
itemCouncilProjectTemplate.odt_file = 'projet-deliberation.odt'
itemCouncilProjectTemplate.pod_formats = ['odt', 'pdf', ]
itemCouncilProjectTemplate.pod_portal_types = ['MeetingItemCouncil']
itemCouncilProjectTemplate.tal_condition = 'python:not here.hasMeeting()'

itemCouncilTemplate = PodTemplateDescriptor('deliberation', 'Délibération')
itemCouncilTemplate.odt_file = 'deliberation.odt'
itemCouncilTemplate.pod_formats = ['odt', 'pdf', ]
itemCouncilTemplate.pod_portal_types = ['MeetingItemCouncil']
itemCouncilTemplate.tal_condition = 'python:here.hasMeeting()'

councilTemplates = [agendaCouncilTemplate, decisionsCouncilTemplate,
                    itemCouncilRapportTemplate, itemCouncilTemplate,
                    itemCouncilProjectTemplate, dashboardTemplate]

# Users and groups -------------------------------------------------------------
dgen = UserDescriptor('dgen', [], email="test@test.be", fullname="Henry Directeur")
bourgmestre = UserDescriptor('bourgmestre', [], email="test@test.be", fullname="Pierre Bourgmestre")
dfin = UserDescriptor('dfin', [], email="test@test.be", fullname="Directeur Financier")
agentInfo = UserDescriptor('agentInfo', [], email="test@test.be", fullname="Agent Service Informatique")
agentCompta = UserDescriptor('agentCompta', [], email="test@test.be", fullname="Agent Service Comptabilité")
agentPers = UserDescriptor('agentPers', [], email="test@test.be", fullname="Agent Service du Personnel")
agentTrav = UserDescriptor('agentTrav', [], email="test@test.be", fullname="Agent Travaux")
chefPers = UserDescriptor('chefPers', [], email="test@test.be", fullname="Chef Personnel")
chefCompta = UserDescriptor('chefCompta', [], email="test@test.be", fullname="Chef Comptabilité")
refPers = UserDescriptor('refPers', [], email="test@test.be", fullname="Référent Administratif du Personnel")
refCompta = UserDescriptor('refCompta', [], email="test@test.be", fullname="Référent Administratif Comptabilité")
dirPers = UserDescriptor('dirPers', [], email="test@test.be", fullname="Directeur du Personnel")
dirCompta = UserDescriptor('dirCompta', [], email="test@test.be", fullname="Directeur Comptabilité")
echevinPers = UserDescriptor('echevinPers', [], email="test@test.be", fullname="Echevin du Personnel")
echevinTrav = UserDescriptor('echevinTrav', [], email="test@test.be", fullname="Echevin des Travaux")
conseiller = UserDescriptor('conseiller', [], email="test@test.be", fullname="Conseiller")

emetteuravisPers = UserDescriptor('emetteuravisPers', [], email="test@test.be", fullname="Emetteur avis Personnel")

groups = [GroupDescriptor(POLICE_GROUP_ID, 'Zone de Police', 'ZPL',
                          groupInCharge=({'group_id': 'bourgmestre', 'date_to': ''},)),
          GroupDescriptor('dirgen', 'Directeur Général', 'DG',
                          groupInCharge=({'group_id': 'bourgmestre', 'date_to': ''},)),
          GroupDescriptor('secretariat', 'Secrétariat communal', 'Secr',
                          groupInCharge=({'group_id': 'bourgmestre', 'date_to': ''},)),
          GroupDescriptor('personnel', 'Service du personnel', 'Pers',
                          groupInCharge=({'group_id': 'echevin1', 'date_to': ''},)),
          GroupDescriptor('informatique', 'Service informatique', 'Info',
                          groupInCharge=({'group_id': 'echevin2', 'date_to': ''},)),
          GroupDescriptor('dirfin', 'Directeur Financier', 'DF',
                          groupInCharge=({'group_id': 'echevin2', 'date_to': ''},)),
          GroupDescriptor('comptabilite', 'Service comptabilité', 'Compt',
                          groupInCharge=({'group_id': 'echevin2', 'date_to': ''},)),
          GroupDescriptor('travaux', 'Service travaux', 'Trav',
                          groupInCharge=({'group_id': 'echevin3', 'date_to': ''},)),
          GroupDescriptor('bourgmestre', 'Bourgmestre', 'BG'),
          GroupDescriptor('echevin1', 'Echevin 1', 'Ech1'),
          GroupDescriptor('echevin2', 'Echevin 2', 'Ech2'),
          GroupDescriptor('echevin3', 'Echevin 3', 'Ech3'),
          ]

# MeetingManager
groups[0].creators.append(dgen)
groups[0].serviceheads.append(dgen)
groups[0].prereviewers.append(dgen)
groups[0].reviewers.append(dgen)
groups[0].observers.append(dgen)
groups[0].advisers.append(dgen)

groups[1].creators.append(dgen)
groups[1].serviceheads.append(dgen)
groups[1].prereviewers.append(dgen)
groups[1].reviewers.append(dgen)
groups[1].observers.append(dgen)
groups[1].advisers.append(dgen)

groups[2].creators.append(agentInfo)
groups[2].creators.append(dgen)
groups[2].serviceheads.append(agentInfo)
groups[2].serviceheads.append(dgen)
groups[2].prereviewers.append(agentInfo)
groups[2].prereviewers.append(dgen)
groups[2].reviewers.append(agentInfo)
groups[2].reviewers.append(dgen)
groups[2].observers.append(agentInfo)
groups[2].advisers.append(agentInfo)

groups[3].creators.append(agentPers)
groups[3].observers.append(agentPers)
groups[3].creators.append(dgen)
groups[3].reviewers.append(dgen)
groups[3].creators.append(chefPers)
groups[3].observers.append(chefPers)
groups[3].serviceheads.append(chefPers)
groups[3].creators.append(refPers)
groups[3].serviceheads.append(refPers)
groups[3].prereviewers.append(refPers)
groups[3].creators.append(dirPers)
groups[3].serviceheads.append(dirPers)
groups[3].prereviewers.append(dirPers)
groups[3].reviewers.append(dirPers)
groups[3].observers.append(dirPers)
groups[3].advisers.append(dirPers)
groups[3].observers.append(echevinPers)
groups[3].advisers.append(emetteuravisPers)

# dirfin
groups[4].itemAdviceStates = ('meeting-config-college__state__prevalidated_waiting_advices',)
groups[4].itemAdviceEditStates = ('meeting-config-college__state__prevalidated_waiting_advices',)
groups[4].keepAccessToItemWhenAdviceIsGiven = True
groups[4].creators.append(dfin)
groups[4].serviceheads.append(dfin)
groups[4].prereviewers.append(dfin)
groups[4].reviewers.append(dfin)
groups[4].observers.append(dfin)
groups[4].advisers.append(dfin)

groups[5].creators.append(agentCompta)
groups[5].creators.append(dfin)
groups[5].creators.append(dgen)
groups[5].creators.append(chefCompta)
groups[5].observers.append(chefCompta)
groups[5].serviceheads.append(chefCompta)
groups[5].creators.append(refCompta)
groups[5].serviceheads.append(refCompta)
groups[5].prereviewers.append(refCompta)
groups[5].creators.append(dirCompta)
groups[5].serviceheads.append(dirCompta)
groups[5].prereviewers.append(dirCompta)
groups[5].reviewers.append(dirCompta)
groups[5].observers.append(dirCompta)
groups[5].advisers.append(dfin)

groups[6].creators.append(agentTrav)
groups[6].creators.append(dgen)
groups[6].serviceheads.append(agentTrav)
groups[6].serviceheads.append(dgen)
groups[6].prereviewers.append(agentTrav)
groups[6].prereviewers.append(dgen)
groups[6].reviewers.append(agentTrav)
groups[6].reviewers.append(dgen)
groups[6].observers.append(agentTrav)
groups[6].observers.append(echevinTrav)
groups[6].advisers.append(agentTrav)

groups[7].creators.append(dgen)
groups[7].serviceheads.append(dgen)
groups[7].prereviewers.append(dgen)
groups[7].reviewers.append(dgen)
groups[7].observers.append(dgen)
groups[7].advisers.append(dgen)

# Meeting configurations -------------------------------------------------------
# college
collegeMeeting = MeetingConfigDescriptor(
    'meeting-config-college', 'Collège Communal',
    'Collège communal', isDefault=True)
collegeMeeting.meetingManagers = ['dgen', ]
collegeMeeting.assembly = 'Pierre Dupont - Bourgmestre,\n' \
                          'Charles Exemple - 1er Echevin,\n' \
                          'Echevin Un, Echevin Deux, Echevin Trois - Echevins,\n' \
                          'Jacqueline Exemple, Responsable du CPAS'
collegeMeeting.signatures = 'Le Secrétaire communal\nPierre Dupont\nLe Bourgmestre\nCharles Exemple'
collegeMeeting.certifiedSignatures = [
    {'signatureNumber': '1',
     'name': u'Mr Vraiment Présent',
     'function': u'Le Secrétaire communal',
     'date_from': '',
     'date_to': '',
     },
    {'signatureNumber': '2',
     'name': u'Mr Charles Exemple',
     'function': u'Le Bourgmestre',
     'date_from': '',
     'date_to': '',
     },
]
collegeMeeting.places = """Aile Dauphin 101 - Hôtel de Ville de Charleroi"""
collegeMeeting.categories = categories
collegeMeeting.shortName = 'College'
collegeMeeting.annexTypes = [annexe, annexeBudget, annexeCahier,
                             annexeDecision, annexeAvis, annexeAvisLegal]
collegeMeeting.usedItemAttributes = ['completeness',
                                     'budgetInfos',
                                     'motivation',
                                     'observations',
                                     'toDiscuss',
                                     'otherMeetingConfigsClonableToPrivacy',
                                     'itemAssembly',
                                     'itemIsSigned', ]
collegeMeeting.usedMeetingAttributes = ['startDate',
                                        'endDate',
                                        'approvalDate',
                                        'signatures',
                                        'assembly',
                                        'assemblyExcused',
                                        'assemblyGuests',
                                        'assemblyStaves',
                                        'place',
                                        'observations',
                                        'assemblyPolice']
collegeMeeting.recordMeetingHistoryStates = []
collegeMeeting.itemsListVisibleColumns = ('Creator', 'CreationDate', 'review_state', 'getCategory',
                                          'proposing_group_acronym', 'advices', 'toDiscuss', 'actions')
collegeMeeting.itemColumns = ('Creator', 'CreationDate', 'ModificationDate', 'review_state',
                              'getCategory', 'proposing_group_acronym', 'advices', 'toDiscuss',
                              'getItemIsSigned', 'linkedMeetingDate', 'actions')
collegeMeeting.xhtmlTransformFields = ('MeetingItem.description',
                                       'MeetingItem.decision',
                                       'MeetingItem.observations',
                                       'Meeting.observations', )
collegeMeeting.dashboardItemsListingsFilters = ('c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'c11',
                                                'c12', 'c13', 'c14', 'c15', 'c16', 'c18')
collegeMeeting.dashboardMeetingAvailableItemsFilters = ('c4', 'c5', 'c11', 'c16')
collegeMeeting.dashboardMeetingLinkedItemsFilters = ('c4', 'c5', 'c6', 'c7', 'c11', 'c16')
collegeMeeting.xhtmlTransformTypes = ('removeBlanks',)
collegeMeeting.itemWorkflow = 'meetingitemcommunes_workflow'
collegeMeeting.meetingWorkflow = 'meetingcommunes_workflow'
collegeMeeting.itemConditionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingItemCharleroiCollegeWorkflowConditions'
collegeMeeting.itemActionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingItemCharleroiCollegeWorkflowActions'
collegeMeeting.meetingConditionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingCharleroiCollegeWorkflowConditions'
collegeMeeting.meetingActionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingCharleroiCollegeWorkflowActions'
collegeMeeting.transitionsToConfirm = ['MeetingItem.delay', ]
collegeMeeting.meetingTopicStates = ('created', 'frozen')
collegeMeeting.decisionTopicStates = ('decided', 'closed')
collegeMeeting.enforceAdviceMandatoriness = False
collegeMeeting.insertingMethodsOnAddItem = (
    {'insertingMethod': 'on_police_then_other_groups', 'reverse': '0'},
    {'insertingMethod': 'on_communication', 'reverse': '1'},
    {'insertingMethod': 'on_other_mc_to_clone_to', 'reverse': '1'},
    {'insertingMethod': 'on_list_type', 'reverse': '0'},
    {'insertingMethod': 'on_groups_in_charge', 'reverse': '0'},
    {'insertingMethod': 'on_categories', 'reverse': '0'})
collegeMeeting.listTypes = DEFAULT_LIST_TYPES + \
    [{'identifier': 'depose', 'label': u'Déposé', 'used_in_inserting_method': '0'}]
collegeMeeting.useGroupsAsCategories = False
collegeMeeting.toDiscussSetOnItemInsert = True
collegeMeeting.toDiscussDefault = False
collegeMeeting.recordItemHistoryStates = []
collegeMeeting.maxShownMeetings = 5
collegeMeeting.maxDaysDecisions = 60
collegeMeeting.meetingAppDefaultView = 'searchmyitems'
collegeMeeting.useAdvices = True
collegeMeeting.itemAdviceStates = ('itemcreated_waiting_advices', 'proposed_waiting_advices',)
collegeMeeting.itemAdviceEditStates = ('itemcreated_waiting_advices', 'proposed_waiting_advices',)
collegeMeeting.itemAdviceViewStates = ('itemcreated_waiting_advices',
                                       'proposed_waiting_advices',
                                       'proposed',
                                       'proposed_to_refadmin',
                                       'prevalidated',
                                       'prevalidated_waiting_advices',
                                       'validated',
                                       'presented',
                                       'itemfrozen',
                                       'returned_to_proposing_group',
                                       'pre_accepted',
                                       'accepted',
                                       'accepted_but_modified',
                                       'refused',
                                       'delayed',)
collegeMeeting.usedAdviceTypes = ('asked_again', 'positive', 'positive_with_remarks',
                                  'negative', 'nil', 'positive_finance', 'positive_with_remarks_finance',
                                  'cautious_finance', 'negative_finance', 'not_given_finance')
collegeMeeting.transitionsReinitializingDelays = ('backTo_prevalidated_from_waiting_advices',
                                                  'backTo_proposed_to_refadmin_from_waiting_advices')
collegeMeeting.enableAdviceInvalidation = False
collegeMeeting.itemAdviceInvalidateStates = []
collegeMeeting.keepAccessToItemWhenAdviceIsGiven = False
collegeMeeting.customAdvisers = [
    {'row_id': 'unique_id_001',
     'group': 'comptabilite',
     'gives_auto_advice_on': 'item/getBudgetRelated',
     'for_item_created_from': today,
     'is_linked_to_previous_row': '0'},
    {'row_id': 'unique_id_002',
     'group': 'dirfin',
     'for_item_created_from': today,
     'delay': '5',
     'delay_left_alert': '2',
     'delay_label': 'Incidence financière >= 22.000€',
     'available_on': 'python: item.adapted().mayChangeDelayTo(5)',
     'is_linked_to_previous_row': '0'},
    {'row_id': 'unique_id_003',
     'group': 'dirfin',
     'for_item_created_from': today,
     'delay': '10',
     'delay_left_alert': '4',
     'delay_label': 'Incidence financière >= 22.000€',
     'available_on': 'python: item.adapted().mayChangeDelayTo(10)',
     'is_linked_to_previous_row': '1'},
    {'row_id': 'unique_id_004',
     'group': 'dirfin',
     'for_item_created_from': today,
     'delay': '20',
     'delay_left_alert': '4',
     'delay_label': 'Incidence financière >= 22.000€',
     'available_on': 'python: item.adapted().mayChangeDelayTo(20)',
     'is_linked_to_previous_row': '1'}, ]

collegeMeeting.itemPowerObserversStates = ('itemfrozen',
                                           'accepted',
                                           'delayed',
                                           'refused',
                                           'accepted_but_modified',
                                           'pre_accepted')
collegeMeeting.itemGroupInChargeStates = collegeMeeting.itemPowerObserversStates + ('validated', 'presented')
collegeMeeting.itemDecidedStates = ['accepted', 'refused', 'delayed', 'accepted_but_modified', 'pre_accepted']
collegeMeeting.workflowAdaptations = ['no_publication', 'no_global_observation',
                                      'only_creator_may_delete', 'return_to_proposing_group',
                                      'pre_validation', 'charleroi_add_refadmin', 'waiting_advices']
collegeMeeting.transitionsForPresentingAnItem = ('propose', 'proposeToRefAdmin', 'prevalidate', 'validate', 'present', )
collegeMeeting.onTransitionFieldTransforms = (
    ({'transition': 'delay',
      'field_name': 'MeetingItem.decision',
      'tal_expression': "string:<p>Le Collège décide de reporter le point.</p>${here/getDecision}"},))
collegeMeeting.onMeetingTransitionItemTransitionToTrigger = ({'meeting_transition': 'freeze',
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
collegeMeeting.meetingPowerObserversStates = ('frozen', 'decided', 'closed')
collegeMeeting.powerAdvisersGroups = ('dirgen', 'dirfin', )
collegeMeeting.itemBudgetInfosStates = ('proposed', 'validated', 'presented')
collegeMeeting.useCopies = True
collegeMeeting.selectableCopyGroups = [groups[0].getIdSuffixed('reviewers'),
                                       groups[1].getIdSuffixed('reviewers'),
                                       groups[2].getIdSuffixed('reviewers'),
                                       groups[4].getIdSuffixed('reviewers')]
collegeMeeting.podTemplates = collegeTemplates
collegeMeeting.meetingConfigsToCloneTo = [{'meeting_config': 'meeting-config-council',
                                           'trigger_workflow_transitions_until': '__nothing__'}, ]
collegeMeeting.itemAutoSentToOtherMCStates = ('accepted', 'accepted_but_modified', )
collegeMeeting.itemManualSentToOtherMCStates = ('itemfrozen', 'pre_accepted', )
collegeMeeting.recurringItems = [
    RecurringItemDescriptor(
        id='recurringagenda1',
        title='Approuve le procès-verbal de la séance antérieure',
        description='Approuve le procès-verbal de la séance antérieure',
        category='recurrents',
        proposingGroup='secretariat',
        decision='Procès-verbal approuvé'),
    RecurringItemDescriptor(
        id='recurringofficialreport1',
        title='Autorise et signe les bons de commande de la semaine',
        description='Autorise et signe les bons de commande de la semaine',
        category='recurrents',
        proposingGroup='secretariat',
        decision='Bons de commande signés'),
    RecurringItemDescriptor(
        id='recurringofficialreport2',
        title='Ordonnance et signe les mandats de paiement de la semaine',
        description='Ordonnance et signe les mandats de paiement de la semaine',
        category='recurrents',
        proposingGroup='secretariat',
        decision='Mandats de paiement de la semaine approuvés'), ]
collegeMeeting.itemTemplates = [
    ItemTemplateDescriptor(
        id='template1',
        title='Tutelle CPAS',
        description='Tutelle CPAS',
        category='divers',
        proposingGroup='secretariat',
        templateUsingGroups=['secretariat', 'dirgen', ],
        decision="""<p>Vu la loi du 8 juillet 1976 organique des centres publics d'action sociale et plus particulièrement son article 111;</p>
<p>Vu l'Arrêté du Gouvernement Wallon du 22 avril 2004 portant codification de la législation relative aux pouvoirs locaux tel que confirmé par le décret du 27 mai 2004 du Conseil régional wallon;</p>
<p>Attendu que les décisions suivantes du Bureau permanent/du Conseil de l'Action sociale du XXX ont été reçues le XXX dans le cadre de la tutelle générale sur les centres publics d'action sociale :</p>
<p>- ...;</p>
<p>- ...;</p>
<p>- ...</p>
<p>Attendu que ces décisions sont conformes à la loi et à l'intérêt général;</p>
<p>Déclare à l'unanimité que :</p>
<p><strong>Article 1er :</strong></p>
<p>Les décisions du Bureau permanent/Conseil de l'Action sociale visées ci-dessus sont conformes à la loi et à l'intérêt général et qu'il n'y a, dès lors, pas lieu de les annuler.</p>
<p><strong>Article 2 :</strong></p>
<p>Copie de la présente délibération sera transmise au Bureau permanent/Conseil de l'Action sociale.</p>"""),
    ItemTemplateDescriptor(
        id='template2',
        title='Contrôle médical systématique agent contractuel',
        description='Contrôle médical systématique agent contractuel',
        category='divers',
        proposingGroup='personnel',
        templateUsingGroups=['personnel', ],
        decision="""
            <p>Vu la loi du 26 mai 2002 instituant le droit à l’intégration sociale;</p>
<p>Vu la délibération du Conseil communal du 29 juin 2009 concernant le cahier spécial des charges relatif au marché de services portant sur le contrôle des agents communaux absents pour raisons médicales;</p>
<p>Vu sa délibération du 17 décembre 2009 désignant le docteur XXX en qualité d’adjudicataire pour la mission de contrôle médical des agents de l’Administration communale;</p>
<p>Vu également sa décision du 17 décembre 2009 d’opérer les contrôles médicaux de manière systématique et pour une période d’essai d’un trimestre;</p>
<p>Attendu qu’un certificat médical a été  reçu le XXX concernant XXX la couvrant du XXX au XXX, avec la mention « XXX »;</p>
<p>Attendu que le Docteur XXX a transmis au service du Personnel, par fax, le même jour à XXX le rapport de contrôle mentionnant l’absence de XXX ce XXX à XXX;</p>
<p>Considérant que XXX avait été informée par le Service du Personnel de la mise en route du système de contrôle systématique que le médecin-contrôleur;</p>
<p>Considérant qu’ayant été absent(e) pour maladie la semaine précédente elle avait reçu la visite du médecin-contrôleur;</p>
<p>DECIDE :</p>
<p><strong>Article 1</strong> : De convoquer XXX devant  Monsieur le Secrétaire communal f.f. afin de lui rappeler ses obligations en la matière.</p>
<p><strong>Article 2</strong> :  De prévenir XXX, qu’en cas de récidive, il sera proposé par le Secrétaire communal au Collège de transformer les jours de congés de maladie en absence injustifiée (retenue sur traitement avec application de la loi du 26 mai 2002 citée ci-dessus).</p>
<p><strong>Article 3</strong> : De charger le service du personnel du suivi de ce dossier.</p>"""),
    ItemTemplateDescriptor(
        id='template3',
        title='Engagement temporaire',
        description='Engagement temporaire',
        category='divers',
        proposingGroup='personnel',
        templateUsingGroups=['personnel', ],
        decision="""<p>Considérant qu’il y a lieu de pourvoir au remplacement de Madame XXX, XXX bénéficiant d’une interruption de carrière pour convenances personnelles pour l’année scolaire 2009/2010. &nbsp;</p>
<p>Attendu qu’un appel public a été lancé au mois de mai dernier;</p>
<p>Vu la circulaire N° 2772 de la Communauté Française&nbsp;du 29 juin 2009 concernant &nbsp;la gestion des carrières administrative et pécuniaire dans l’enseignement fondamental ordinaire et principalement le chapitre 3 relatif aux engagements temporaires pendant l’année scolaire 2009/2010;</p>
<p>Vu la proposition du directeur concerné d’attribuer cet emploi à Monsieur XXX, titulaire des titres requis;</p>
<p>Vu le décret de la Communauté Française du 13 juillet 1998 portant restructuration de l’enseignement&nbsp;maternel et primaire ordinaires avec effet au 1er octobre 1998;</p>
<p>Vu la loi du 29 mai 1959 (Pacte scolaire) et les articles L1122-19 et L1213-1 du Code de la démocratie locale et de la décentralisation;</p>
<p>Vu l’avis favorable de l’Echevin de l’Enseignement;</p>
<p><b>DECIDE&nbsp;:</b><br>
<b><br> Article 1<sup>er</sup></b> :</p>
<p>Au scrutin secret et à l’unanimité, de désigner Monsieur XXX, né le XXX à XXX et domicilié à XXX, en qualité d’instituteur maternel temporaire mi-temps en remplacement de Madame XXX aux écoles communales fondamentales de Sambreville (section de XXX) du XXX au XXX.</p>
<p><b>Article 2</b> :</p>
<p>L’horaire hebdomadaire de l’intéressé est fixé à 13 périodes.</p>
<p><b>Article 3&nbsp;:</b></p>
<p>La présente délibération sera soumise à la ratification du Conseil Communal. Elle sera transmise au Bureau Régional de l’Enseignement primaire et maternel, à l’Inspectrice Cantonale et à la direction concernée.</p>"""),
    ItemTemplateDescriptor(
        id='template4',
        title='Prestation réduite',
        description='Prestation réduite',
        category='divers',
        proposingGroup='personnel',
        templateUsingGroups=['personnel', ],
        decision="""<p>Vu la loi de redressement du 22 janvier 1985 (article 99 et suivants) et de l’Arrêté Royal du 12 août 1991 (tel que modifié) relatifs à l’interruption de carrière professionnelle dans l’enseignement;</p>
<p>Vu la lettre du XXX par laquelle Madame XXX, institutrice maternelle, sollicite le renouvellement pendant l’année scolaire 2009/2010 de son congé pour prestations réduites mi-temps pour convenances personnelles dont elle bénéficie depuis le 01 septembre 2006;</p>
<p>Attendu que le remplacement de l’intéressée&nbsp;est assuré pour la prochaine rentrée scolaire;</p>
<p>Vu le décret de la Communauté Française du 13 juillet 1988 portant restructuration de l’enseignement maternel et primaire ordinaires avec effet au 1er octobre 1998;</p>
<p>Vu la loi du 29 mai 1959 (Pacte Scolaire) et les articles L1122-19 et L1213-1 du code de la démocratie locale et de la décentralisation;</p>
<p>Vu l’avis favorable de l’Echevin de l’Enseignement;</p>
<p><b>DECIDE&nbsp;:</b><br><b><br> Article 1<sup>er</sup></b>&nbsp;:</p>
<p>Au scrutin secret et à l’unanimité, d’accorder à Madame XXX le congé pour prestations réduites mi-temps sollicité pour convenances personnelles en qualité d’institutrice maternelle aux écoles communales fondamentales&nbsp;&nbsp;de Sambreville (section de XXX).</p>
<p><b>Article 2</b> :</p>
<p>Une activité lucrative est autorisée durant ce congé qui est assimilé à une période d’activité de service, dans le respect de la réglementation relative au cumul.</p>
<p><b>Article 3&nbsp;:</b></p>
<p>La présente délibération sera soumise pour accord au prochain Conseil, transmise au Bureau Régional de l’Enseignement primaire et maternel, à&nbsp;l’Inspectrice Cantonale, à la direction concernée et à l’intéressée.</p>"""),
    ItemTemplateDescriptor(
        id='template5',
        title='Exemple modèle disponible pour tous',
        description='Exemple modèle disponible pour tous',
        category='divers',
        proposingGroup='',
        templateUsingGroups=[],
        decision="""<p>Vu la loi du XXX;</p>
<p>Vu ...;</p>
<p>Attendu que ...;</p>
<p>Vu le décret de la Communauté Française du ...;</p>
<p>Vu la loi du ...;</p>
<p>Vu l’avis favorable de ...;</p>
<p><b>DECIDE&nbsp;:</b><br><b><br> Article 1<sup>er</sup></b>&nbsp;:</p>
<p>...</p>
<p><b>Article 2</b> :</p>
<p>...</p>
<p><b>Article 3&nbsp;:</b></p>
<p>...</p>"""),
]

# Conseil communal
councilMeeting = MeetingConfigDescriptor(
    'meeting-config-council', 'Conseil Communal',
    'Conseil Communal')
councilMeeting.meetingManagers = ['dgen', ]
councilMeeting.assembly = 'Pierre Dupont - Bourgmestre,\n' \
                          'Charles Exemple - 1er Echevin,\n' \
                          'Echevin Un, Echevin Deux, Echevin Trois - Echevins,\n' \
                          'Jacqueline Exemple, Responsable du CPAS'
councilMeeting.signatures = 'Le Secrétaire communal\nPierre Dupont\nLe Bourgmestre\nCharles Exemple'
councilMeeting.certifiedSignatures = [
    {'signatureNumber': '1',
     'name': u'Mr Vraiment Présent',
     'function': u'Le Secrétaire communal',
     'date_from': '',
     'date_to': '',
     },
    {'signatureNumber': '2',
     'name': u'Mr Charles Exemple',
     'function': u'Le Bourgmestre',
     'date_from': '',
     'date_to': '',
     },
]
councilMeeting.places = """Place1\n\r
Place2\n\r
Place3\n\r"""
councilMeeting.categories = categories
councilMeeting.shortName = 'Council'
councilMeeting.itemCreatedOnlyUsingTemplate = True
councilMeeting.useGroupsAsCategories = False
councilMeeting.annexTypes = [annexe, annexeBudget, annexeCahier,
                             annexeDecision, annexeAvis, annexeAvisLegal]
councilMeeting.usedItemAttributes = ['motivation',
                                     'observations',
                                     'privacy',
                                     'itemAssembly',
                                     'budgetInfos',
                                     'manuallyLinkedItems']
councilMeeting.usedMeetingAttributes = ['startDate',
                                        'midDate',
                                        'endDate',
                                        'signatures',
                                        'assembly',
                                        'assemblyExcused',
                                        'assemblyPrivacySecretAbsents',
                                        'place',
                                        'authorityNotice',
                                        'observations', ]
councilMeeting.recordMeetingHistoryStates = []
councilMeeting.xhtmlTransformFields = ('MeetingItem.description',
                                       'MeetingItem.decision',
                                       'MeetingItem.observations',
                                       'Meeting.observations', )
councilMeeting.xhtmlTransformTypes = ('removeBlanks',)
councilMeeting.itemWorkflow = 'meetingitemcommunes_workflow'
councilMeeting.meetingWorkflow = 'meetingcommunes_workflow'
councilMeeting.itemConditionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingItemCharleroiCouncilWorkflowConditions'
councilMeeting.itemActionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingItemCharleroiCouncilWorkflowActions'
councilMeeting.meetingConditionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingCharleroiCouncilWorkflowConditions'
councilMeeting.meetingActionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingCharleroiCouncilWorkflowActions'
councilMeeting.transitionsToConfirm = []
councilMeeting.meetingTopicStates = ('created', 'frozen')
councilMeeting.decisionTopicStates = ('decided', 'closed')
councilMeeting.itemAdviceStates = ('validated',)
councilMeeting.enforceAdviceMandatoriness = False
councilMeeting.insertingMethodsOnAddItem = ({'insertingMethod': 'on_proposing_groups',
                                             'reverse': '0'}, )
councilMeeting.recordItemHistoryStates = []
councilMeeting.maxShownMeetings = 5
councilMeeting.maxDaysDecisions = 60
councilMeeting.meetingAppDefaultView = 'searchmyitems'
councilMeeting.itemDocFormats = ('odt', 'pdf')
councilMeeting.meetingDocFormats = ('odt', 'pdf')
councilMeeting.useAdvices = False
councilMeeting.itemAdviceStates = ()
councilMeeting.itemAdviceEditStates = ()
councilMeeting.itemAdviceViewStates = ()
councilMeeting.itemDecidedStates = ['accepted', 'refused', 'delayed',
                                    'accepted_but_modified', 'pre_accepted',
                                    'marked_not_applicable']
councilMeeting.workflowAdaptations = ['no_publication', 'no_global_observation',
                                      'return_to_proposing_group', 'items_come_validated',
                                      'mark_not_applicable']
councilMeeting.transitionsForPresentingAnItem = ('present', )
councilMeeting.onMeetingTransitionItemTransitionToTrigger = ({'meeting_transition': 'freeze',
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
councilMeeting.itemPowerObserversStates = ('itemfrozen',
                                           'accepted', 'delayed',
                                           'refused',
                                           'accepted_but_modified', 'pre_accepted')
councilMeeting.itemRestrictedPowerObserversStates = councilMeeting.itemPowerObserversStates
councilMeeting.meetingPowerObserversStates = ('frozen', 'decided', 'closed')
councilMeeting.meetingRestrictedPowerObserversStates = councilMeeting.meetingPowerObserversStates
councilMeeting.powerAdvisersGroups = ()
councilMeeting.useCopies = True
councilMeeting.selectableCopyGroups = [groups[0].getIdSuffixed('reviewers'),
                                       groups[1].getIdSuffixed('reviewers'),
                                       groups[2].getIdSuffixed('reviewers'),
                                       groups[4].getIdSuffixed('reviewers')]
councilMeeting.podTemplates = councilTemplates

bourgmestre_mu = MeetingUserDescriptor('bourgmestre',
                                       duty='Bourgmestre',
                                       usages=['assemblyMember', 'signer', 'asker', ],
                                       signatureIsDefault=True)
receveur_mu = MeetingUserDescriptor('receveur',
                                    duty='Receveur communal',
                                    usages=['assemblyMember', 'signer', 'asker', ])
echevinPers_mu = MeetingUserDescriptor('echevinPers',
                                       duty='Echevin GRH',
                                       usages=['assemblyMember', 'asker', ])
echevinTrav_mu = MeetingUserDescriptor('echevinTrav',
                                       duty='Echevin Travaux',
                                       usages=['assemblyMember', 'asker', ])
dgen_mu = MeetingUserDescriptor('dgen',
                                duty='Directeur Général',
                                usages=['assemblyMember', 'signer', 'asker', ],
                                signatureIsDefault=True)

councilMeeting.meetingUsers = [bourgmestre_mu, receveur_mu, echevinPers_mu, echevinTrav_mu, dgen_mu]

councilMeeting.itemTemplates = [
    ItemTemplateDescriptor(
        id='template1',
        title='Point Conseil',
        description='',
        category='divers',
        proposingGroup='dirgen',
        templateUsingGroups=['dirgen', ],
        decision="""<p>&nbsp;</p>""")
    ]

councilMeeting.recurringItems = [
    RecurringItemDescriptor(
        id='recurringagenda1',
        title='Approuve le procès-verbal de la séance antérieure',
        description='Approuve le procès-verbal de la séance antérieure',
        category='recurrents',
        proposingGroup='secretariat',
        decision='Procès-verbal approuvé'), ]

data = PloneMeetingConfiguration(meetingFolderTitle='Mes séances',
                                 meetingConfigs=(collegeMeeting, councilMeeting),
                                 groups=groups)
data.enableUserPreferences = False
data.usersOutsideGroups = [bourgmestre, conseiller]
# ------------------------------------------------------------------------------
