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
from Products.PloneMeeting.profiles import PloneGroupDescriptor
from Products.PloneMeeting.profiles import PloneMeetingConfiguration
from Products.PloneMeeting.profiles import PodTemplateDescriptor
from Products.PloneMeeting.profiles import RecurringItemDescriptor
from Products.PloneMeeting.profiles import UserDescriptor

from Products.MeetingCharleroi.config import CC_ARRET_OJ_CAT_ID
from Products.MeetingCharleroi.config import COMMUNICATION_CAT_ID
from Products.MeetingCharleroi.config import POLICE_GROUP_PREFIX

today = DateTime().strftime('%Y/%m/%d')

# File types -------------------------------------------------------------------
annexe = ItemAnnexTypeDescriptor('annexe', 'Annexe', u'attach.png')
annexeBudget = ItemAnnexTypeDescriptor('annexeBudget', 'Article Budgétaire', u'budget.png')
annexeCahier = ItemAnnexTypeDescriptor('annexeCahier', 'Cahier des Charges', u'cahier.gif')
annexeDecision = ItemAnnexTypeDescriptor('annexeDecision', 'Annexe à la décision', u'attach.png',
                                         relatedTo='item_decision')
annexeAvis = AnnexTypeDescriptor('annexeAvis', 'Annexe à un avis', u'attach.png',
                                 relatedTo='advice')
annexeAvisLegal = AnnexTypeDescriptor('annexeAvisLegal', 'Extrait article de loi', u'legalAdvice.png',
                                      relatedTo='advice')

# Categories -------------------------------------------------------------------
recurring = CategoryDescriptor('recurrents', 'Récurrents')
college_categories = [
    recurring,
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
    CategoryDescriptor(CC_ARRET_OJ_CAT_ID,
                       'Conseil communal - Arrêt de l\'ordre du jour',
                       description=''),
    CategoryDescriptor(COMMUNICATION_CAT_ID,
                       'Communication',
                       description=''),
]
council_categories = [
    CategoryDescriptor('entetes',
                       'Entêtes'),
    CategoryDescriptor('proposition-de-motion',
                       'Proposition de motion'),
    CategoryDescriptor('proposes-par-un-conseiller',
                       'Proposés par un Conseiller'),
    CategoryDescriptor('interventions',
                       'Interventions'),
    CategoryDescriptor('questions-actualite',
                       "Questions d'actualité"),
    CategoryDescriptor('indeterminee',
                       'Indéterminée'),
    CategoryDescriptor('designations',
                       'Désignations'),
    CategoryDescriptor('nominations',
                       'Nominations'),
    CategoryDescriptor('engagements',
                       'Engagements'),
    CategoryDescriptor('mises-a-disposition',
                       'Mises à disposition'),
    CategoryDescriptor('autorisations',
                       'Autorisations'),
    CategoryDescriptor('conges',
                       'Congés'),
    CategoryDescriptor('disponibilites',
                       'Disponibilités'),
    CategoryDescriptor('interruptions-de-carriere',
                       'Interruptions de carrière'),
    CategoryDescriptor('occupations-complementaires',
                       'Occupations complémentaires'),
    CategoryDescriptor('demissions',
                       'Démissions'),
    CategoryDescriptor('pensions-diverses',
                       'Pensions diverses'),
    CategoryDescriptor('ecartements',
                       'Ecartements'),
    CategoryDescriptor('divers',
                       'Divers'),
    CategoryDescriptor('contentieux',
                       'Contentieux'),

]

# Pod templates ----------------------------------------------------------------
agendaTemplate = PodTemplateDescriptor('oj', 'Ordre du jour')
agendaTemplate.odt_file = 'college-oj.odt'
agendaTemplate.pod_formats = ['odt', 'pdf', ]
agendaTemplate.pod_portal_types = ['MeetingCollege']
agendaTemplate.tal_condition = 'python:tool.isManager(here)'
agendaTemplate.context_variables = [{'name': u'oj_type', 'value': u'full'}]

agendaTemplateBg = PodTemplateDescriptor('oj-bg', 'Ordre du jour Bourgmestre')
agendaTemplateBg.odt_file = 'college-oj.odt'
agendaTemplateBg.pod_formats = ['odt', 'pdf', ]
agendaTemplateBg.pod_portal_types = ['MeetingCollege']
agendaTemplateBg.tal_condition = 'python:tool.isManager(here)'
agendaTemplateBg.context_variables = [{'name': u'oj_type', 'value': u'bg'}]

decisionsTemplate = PodTemplateDescriptor('pv', 'Procès-verbal')
decisionsTemplate.odt_file = 'college-pv.odt'
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

dfAdviceTemplate = PodTemplateDescriptor('df-advice', 'Avis DF')
dfAdviceTemplate.odt_file = 'df-advice.odt'
dfAdviceTemplate.pod_formats = ['odt', 'pdf', ]
dfAdviceTemplate.pod_portal_types = ['MeetingItemCollege']
dfAdviceTemplate.tal_condition = \
    'python:(here.meta_type=="MeetingItem") and context.adapted().showFinanceAdviceDocuments()'

dashboardTemplate = PodTemplateDescriptor('recapitulatif', 'Récapitulatif', dashboard=True)
dashboardTemplate.odt_file = 'recapitulatif-tb.odt'
dashboardTemplate.tal_condition = 'python: context.absolute_url().endswith("/searches_items")'

historyTemplate = PodTemplateDescriptor('historique', 'Historique')
historyTemplate.odt_file = 'history.odt'
historyTemplate.pod_formats = ['odt', 'pdf', ]
historyTemplate.pod_portal_types = ['MeetingItemCollege']

collegeTemplates = [agendaTemplate, agendaTemplateBg, decisionsTemplate,
                    itemProjectTemplate, itemTemplate,
                    dfAdvicesTemplate, dashboardTemplate,
                    historyTemplate]

# Pod templates ----------------------------------------------------------------
agendaCouncilTemplateIni = PodTemplateDescriptor('oj-initial', 'Ordre du jour Initial')
agendaCouncilTemplateIni.odt_file = 'council-oj.odt'
agendaCouncilTemplateIni.pod_formats = ['odt', 'pdf', ]
agendaCouncilTemplateIni.pod_portal_types = ['MeetingCouncil']
agendaCouncilTemplateIni.tal_condition = 'python:tool.isManager(here)'
agendaCouncilTemplateIni.context_variables = [{'name': u'oj_type', 'value': u'initial'}]

agendaCouncilTemplateComp = PodTemplateDescriptor('oj-comp', 'Ordre du jour Complémentaire')
agendaCouncilTemplateComp.odt_file = 'council-oj.odt'
agendaCouncilTemplateComp.pod_formats = ['odt', 'pdf', ]
agendaCouncilTemplateComp.pod_portal_types = ['MeetingCouncil']
agendaCouncilTemplateComp.tal_condition = 'python:tool.isManager(here)'
agendaCouncilTemplateComp.context_variables = [{'name': u'oj_type', 'value': u'full'}]

agendaCouncilTemplateBg = PodTemplateDescriptor('oj-bg', 'Ordre du jour Bourgmestre')
agendaCouncilTemplateBg.odt_file = 'council-oj.odt'
agendaCouncilTemplateBg.pod_formats = ['odt', 'pdf', ]
agendaCouncilTemplateBg.pod_portal_types = ['MeetingCouncil']
agendaCouncilTemplateBg.tal_condition = 'python:tool.isManager(here)'
agendaCouncilTemplateBg.context_variables = [{'name': u'oj_type', 'value': u'bg'}]

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

councilTemplates = [agendaCouncilTemplateIni, agendaCouncilTemplateComp,
                    agendaCouncilTemplateBg, decisionsCouncilTemplate,
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

police_grp = GroupDescriptor(POLICE_GROUP_PREFIX, 'Zone de Police', 'ZPL',
                             groupsInCharge=('bourgmestre',))
police_compta_grp = GroupDescriptor(
    POLICE_GROUP_PREFIX + '-compta', 'Zone de Police comptable spécial', 'ZPLCS',
    groupsInCharge=('bourgmestre',))
dirgen_grp = GroupDescriptor('dirgen', 'Directeur Général', 'DG',
                             groupsInCharge=('bourgmestre',))
secr_grp = GroupDescriptor('secretariat', 'Secrétariat communal', 'Secr',
                           groupsInCharge=('bourgmestre',))
info_grp = GroupDescriptor('informatique', 'Service informatique', 'Info',
                           groupsInCharge=('echevin2',))
pers_grp = GroupDescriptor('personnel', 'Service du personnel', 'Pers',
                           groupsInCharge=('echevin1',))
dirfin_grp = GroupDescriptor('dirfin', 'Directeur Financier', 'DF',
                             groupsInCharge=('echevin2',))
compta_grp = GroupDescriptor('comptabilite', 'Service comptabilité', 'Compt',
                             groupsInCharge=('echevin2',))
trav_grp = GroupDescriptor('travaux', 'Service travaux', 'Trav',
                           groupsInCharge=('echevin3',))
bourg_grp = GroupDescriptor('bourgmestre', 'Bourgmestre', 'BG', '1')
ech1_grp = GroupDescriptor('echevin1', 'Echevin 1', 'Ech1', '2')
ech2_grp = GroupDescriptor('echevin2', 'Echevin 2', 'Ech2', '3')
ech3_grp = GroupDescriptor('echevin3', 'Echevin 3', 'Ech3', '4')

dirgen_grp.creators.append(dgen)
dirgen_grp.serviceheads.append(dgen)
dirgen_grp.prereviewers.append(dgen)
dirgen_grp.reviewers.append(dgen)
dirgen_grp.observers.append(dgen)
dirgen_grp.advisers.append(dgen)

secr_grp.creators.append(dgen)
secr_grp.serviceheads.append(dgen)
secr_grp.prereviewers.append(dgen)
secr_grp.reviewers.append(dgen)
secr_grp.observers.append(dgen)
secr_grp.advisers.append(dgen)

info_grp.creators.append(agentInfo)
info_grp.creators.append(dgen)
info_grp.serviceheads.append(agentInfo)
info_grp.serviceheads.append(dgen)
info_grp.prereviewers.append(agentInfo)
info_grp.prereviewers.append(dgen)
info_grp.reviewers.append(agentInfo)
info_grp.reviewers.append(dgen)
info_grp.observers.append(agentInfo)
info_grp.advisers.append(agentInfo)

pers_grp.creators.append(agentPers)
pers_grp.observers.append(agentPers)
pers_grp.creators.append(dgen)
pers_grp.reviewers.append(dgen)
pers_grp.creators.append(chefPers)
pers_grp.observers.append(chefPers)
pers_grp.serviceheads.append(chefPers)
pers_grp.creators.append(refPers)
pers_grp.serviceheads.append(refPers)
pers_grp.prereviewers.append(refPers)
pers_grp.creators.append(dirPers)
pers_grp.serviceheads.append(dirPers)
pers_grp.prereviewers.append(dirPers)
pers_grp.reviewers.append(dirPers)
pers_grp.observers.append(dirPers)
pers_grp.advisers.append(dirPers)
pers_grp.observers.append(echevinPers)
pers_grp.advisers.append(emetteuravisPers)

dirfin_grp.itemAdviceStates = ('meeting-config-college__state__prevalidated_waiting_advices',)
dirfin_grp.itemAdviceEditStates = ('meeting-config-college__state__prevalidated_waiting_advices',)
dirfin_grp.keepAccessToItemWhenAdviceIsGiven = True
dirfin_grp.creators.append(dfin)
dirfin_grp.serviceheads.append(dfin)
dirfin_grp.prereviewers.append(dfin)
dirfin_grp.reviewers.append(dfin)
dirfin_grp.observers.append(dfin)
dirfin_grp.advisers.append(dfin)
dirfin_grp.financialcontrollers.append(dfin)
dirfin_grp.financialeditors.append(dfin)
dirfin_grp.financialreviewers.append(dfin)
dirfin_grp.financialmanagers.append(dfin)

compta_grp.creators.append(agentCompta)
compta_grp.creators.append(dfin)
compta_grp.creators.append(dgen)
compta_grp.creators.append(chefCompta)
compta_grp.observers.append(chefCompta)
compta_grp.serviceheads.append(chefCompta)
compta_grp.creators.append(refCompta)
compta_grp.serviceheads.append(refCompta)
compta_grp.prereviewers.append(refCompta)
compta_grp.creators.append(dirCompta)
compta_grp.serviceheads.append(dirCompta)
compta_grp.prereviewers.append(dirCompta)
compta_grp.reviewers.append(dirCompta)
compta_grp.observers.append(dirCompta)
compta_grp.advisers.append(dfin)

trav_grp.creators.append(agentTrav)
trav_grp.creators.append(dgen)
trav_grp.serviceheads.append(agentTrav)
trav_grp.serviceheads.append(dgen)
trav_grp.prereviewers.append(agentTrav)
trav_grp.prereviewers.append(dgen)
trav_grp.reviewers.append(agentTrav)
trav_grp.reviewers.append(dgen)
trav_grp.observers.append(agentTrav)
trav_grp.observers.append(echevinTrav)
trav_grp.advisers.append(agentTrav)

bourg_grp.creators.append(dgen)
bourg_grp.serviceheads.append(dgen)
bourg_grp.prereviewers.append(dgen)
bourg_grp.reviewers.append(dgen)
bourg_grp.observers.append(dgen)
bourg_grp.advisers.append(dgen)

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
collegeMeeting.signatures = \
    'Le Secrétaire communal\nPierre Dupont\nDirecteur général f.f.\nLe Président\nCharles Exemple\nÉchevin délégué'

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
collegeMeeting.categories = college_categories
collegeMeeting.shortName = 'College'
collegeMeeting.annexTypes = [annexe, annexeBudget, annexeCahier,
                             annexeDecision, annexeAvis, annexeAvisLegal]
collegeMeeting.usedItemAttributes = ['completeness',
                                     'budgetInfos',
                                     'manuallyLinkedItems',
                                     'motivation',
                                     'observations',
                                     'toDiscuss',
                                     'otherMeetingConfigsClonableToPrivacy',
                                     'itemAssembly',
                                     'itemIsSigned',
                                     'bourgmestreObservations',
                                     'proposingGroupWithGroupInCharge']
collegeMeeting.usedMeetingAttributes = ['startDate',
                                        'endDate',
                                        'approvalDate',
                                        'signatures',
                                        'assembly',
                                        'assemblyExcused',
                                        'assemblyAbsents',
                                        'assemblyGuests',
                                        'assemblyStaves',
                                        'place',
                                        'extraordinarySession',
                                        'observations',
                                        'assemblyPolice']
collegeMeeting.recordMeetingHistoryStates = []
collegeMeeting.itemsListVisibleColumns = ('Creator', 'item_reference', 'review_state', 'getCategory',
                                          'proposing_group_acronym', 'group_in_charge_acronym',
                                          'advices', 'toDiscuss', 'actions')
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
collegeMeeting.itemReferenceFormat = "python: here.adapted().getItemRefForActe()"
collegeMeeting.insertingMethodsOnAddItem = (
    {'insertingMethod': 'on_police_then_other_groups', 'reverse': '0'},
    {'insertingMethod': 'on_communication', 'reverse': '1'},
    {'insertingMethod': 'on_other_mc_to_clone_to', 'reverse': '1'},
    {'insertingMethod': 'on_list_type', 'reverse': '0'},
    {'insertingMethod': 'on_groups_in_charge', 'reverse': '0'},
    {'insertingMethod': 'on_categories', 'reverse': '0'})
collegeMeeting.listTypes = DEFAULT_LIST_TYPES + \
    [{'identifier': 'depose', 'label': u'Déposé en séance', 'used_in_inserting_method': '0'}]
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
                                  'cautious_finance', 'negative_finance', 'not_given_finance', 'not_required_finance')
collegeMeeting.transitionsReinitializingDelays = ()
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
                                      'pre_validation', 'charleroi_add_refadmin', 'waiting_advices',
                                      'postpone_next_meeting', 'mark_not_applicable', 'removed']
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
collegeMeeting.selectableCopyGroups = [police_grp.getIdSuffixed('reviewers'),
                                       police_compta_grp.getIdSuffixed('reviewers'),
                                       dirgen_grp.getIdSuffixed('reviewers'),
                                       dirfin_grp.getIdSuffixed('reviewers'),
                                       pers_grp.getIdSuffixed('reviewers')]
collegeMeeting.podTemplates = collegeTemplates
collegeMeeting.meetingConfigsToCloneTo = [{'meeting_config': 'meeting-config-council',
                                           'trigger_workflow_transitions_until': '__nothing__'}, ]
collegeMeeting.itemAutoSentToOtherMCStates = ('accepted', 'accepted_but_modified', )
collegeMeeting.itemManualSentToOtherMCStates = ('itemfrozen', 'pre_accepted', )
collegeMeeting.keepAdvicesOnSentToOtherMC = True
collegeMeeting.advicesKeptOnSentToOtherMC = ('delay_real_group_id__unique_id_002',
                                             'delay_real_group_id__unique_id_003',
                                             'delay_real_group_id__unique_id_004')
collegeMeeting.recurringItems = [
    RecurringItemDescriptor(
        id='recurringagenda1',
        title='Approuve le procès-verbal de la séance antérieure',
        description='Approuve le procès-verbal de la séance antérieure',
        category='recurrents',
        proposingGroup='secretariat',
        proposingGroupWithGroupInCharge='secretariat__groupincharge__bourgmestre',
        decision='Procès-verbal approuvé'),
    RecurringItemDescriptor(
        id='recurringofficialreport1',
        title='Autorise et signe les bons de commande de la semaine',
        description='Autorise et signe les bons de commande de la semaine',
        category='recurrents',
        proposingGroup='secretariat',
        proposingGroupWithGroupInCharge='secretariat__groupincharge__bourgmestre',
        decision='Bons de commande signés'),
    RecurringItemDescriptor(
        id='recurringofficialreport2',
        title='Ordonnance et signe les mandats de paiement de la semaine',
        description='Ordonnance et signe les mandats de paiement de la semaine',
        category='recurrents',
        proposingGroup='secretariat',
        proposingGroupWithGroupInCharge='secretariat__groupincharge__bourgmestre',
        decision='Mandats de paiement de la semaine approuvés'), ]
collegeMeeting.itemTemplates = [
    ItemTemplateDescriptor(
        id='template1',
        title='Tutelle CPAS',
        description='Tutelle CPAS',
        category='divers',
        proposingGroup='',
        proposingGroupWithGroupInCharge='',
        templateUsingGroups=[],
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
        proposingGroupWithGroupInCharge='personnel__groupincharge__echevin1',
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
        proposingGroupWithGroupInCharge='personnel__groupincharge__echevin1',
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
        proposingGroupWithGroupInCharge='personnel__groupincharge__echevin1',
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
councilMeeting.categories = council_categories
councilMeeting.shortName = 'Council'
councilMeeting.itemCreatedOnlyUsingTemplate = True
councilMeeting.listTypes = DEFAULT_LIST_TYPES + \
    [{'identifier': 'lateextracollege',
      'label': u'Urgence (Collège extraordinaire)',
      'used_in_inserting_method': '1'}]
councilMeeting.selectablePrivacies = ('secret_heading', 'public', 'secret')
councilMeeting.useGroupsAsCategories = False
councilMeeting.annexTypes = [annexe, annexeBudget, annexeCahier,
                             annexeDecision, annexeAvis, annexeAvisLegal]
councilMeeting.usedItemAttributes = ['motivation',
                                     'observations',
                                     'privacy',
                                     'itemAssembly',
                                     'budgetInfos',
                                     'manuallyLinkedItems',
                                     'pollType',
                                     'pollTypeObservations',
                                     'itemInitiator',
                                     'bourgmestreObservations',
                                     'proposingGroupWithGroupInCharge']
councilMeeting.usedMeetingAttributes = ['startDate',
                                        'endDate',
                                        'signatures',
                                        'assembly',
                                        'assemblyExcused',
                                        'assemblyAbsents',
                                        'assemblyGuests',
                                        'assemblyStaves',
                                        'assemblyPrivacySecretAbsents',
                                        'place',
                                        'authorityNotice',
                                        'observations', ]
councilMeeting.recordMeetingHistoryStates = []
councilMeeting.itemsListVisibleColumns = ('Creator',
                                          'item_reference',
                                          'review_state',
                                          'getCategory',
                                          'proposing_group_acronym',
                                          'group_in_charge_acronym',
                                          'advices',
                                          'pollType',
                                          'actions')
councilMeeting.itemColumns = ('Creator', 'CreationDate', 'ModificationDate', 'review_state',
                              'getCategory', 'proposing_group_acronym', 'advices', 'linkedMeetingDate', 'actions')
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
councilMeeting.itemReferenceFormat = "python: here.adapted().getItemRefForActeCouncil()"
councilMeeting.insertingMethodsOnAddItem = (
    {'insertingMethod': 'on_privacy', 'reverse': '0'},
    {'insertingMethod': 'on_list_type', 'reverse': '0'},
    {'insertingMethod': 'on_poll_type', 'reverse': '0'},
    {'insertingMethod': 'on_categories', 'reverse': '0'},
    {'insertingMethod': 'on_police_then_other_groups', 'reverse': '1'},
    {'insertingMethod': 'on_groups_in_charge', 'reverse': '0'},
    {'insertingMethod': 'on_proposing_groups', 'reverse': '0'},)
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
councilMeeting.selectableCopyGroups = [police_grp.getIdSuffixed('reviewers'),
                                       police_compta_grp.getIdSuffixed('reviewers'),
                                       dirgen_grp.getIdSuffixed('reviewers'),
                                       dirfin_grp.getIdSuffixed('reviewers'),
                                       pers_grp.getIdSuffixed('reviewers')]
councilMeeting.usedPollTypes = ('secret', 'no_vote', 'secret_separated', 'freehand')

councilMeeting.podTemplates = councilTemplates

conseiller1_mu = MeetingUserDescriptor('BAKKDJ018', gender='f', duty='Conseillère', usages=['asker', ])
conseiller1 = UserDescriptor('BAKKDJ018', [], email="test@test.be", fullname="BAKKOUCHE Djamila")
conseiller2_mu = MeetingUserDescriptor('BANGSE231', duty='Conseiller', usages=['asker', ])
conseiller2 = UserDescriptor('BANGSE231', [], email="test@test.be", fullname="BANGISA Serge")
conseiller3_mu = MeetingUserDescriptor('CASALE201', duty='Conseiller', usages=['asker', ])
conseiller3 = UserDescriptor('CASALE201', [], email="test@test.be", fullname="CASAERT Léon")
conseiller4_mu = MeetingUserDescriptor('CHASOL115', duty='Conseiller', usages=['asker', ])
conseiller4 = UserDescriptor('CHASOL115', [], email="test@test.be", fullname="CHASTEL Olivier")
conseiller5_mu = MeetingUserDescriptor('DEMALU140', gender='f', duty='Conseillère', usages=['asker', ])
conseiller5 = UserDescriptor('DEMALU140', [], email="test@test.be", fullname="DEMARET Lucie")
conseiller6_mu = MeetingUserDescriptor('DEPRJE105', duty='Conseiller', usages=['asker', ])
conseiller6 = UserDescriptor('DEPRJE105', [], email="test@test.be", fullname="DEPREZ Jean-Pierre")
conseiller7_mu = MeetingUserDescriptor('DESGXA103', duty='Conseiller', usages=['asker', ])
conseiller7 = UserDescriptor('DESGXA103', [], email="test@test.be", fullname="DESGAIN Xavier")
conseiller8_mu = MeetingUserDescriptor('DEVIFA128', gender='f', duty='Conseillère', usages=['asker', ])
conseiller8 = UserDescriptor('DEVIFA128', [], email="test@test.be", fullname="DEVILERS Fabienne")
conseiller9_mu = MeetingUserDescriptor('DOGRMA293', duty='Conseiller', usages=['asker', ])
conseiller9 = UserDescriptor('DOGRMA293', [], email="test@test.be", fullname="DOGRU Mahmut")
conseiller10_mu = MeetingUserDescriptor('DUFRAN251', duty='Conseiller', usages=['asker', ])
conseiller10 = UserDescriptor('DUFRAN251', [], email="test@test.be", fullname="DUFRANE Anthony")
conseiller11_mu = MeetingUserDescriptor('ELBOMA166', gender='f', duty='Conseillère', usages=['asker', ])
conseiller11 = UserDescriptor('ELBOMA166', [], email="test@test.be", fullname="EL BOUREZGUI Malika")
conseiller12_mu = MeetingUserDescriptor('FELOMA103', duty='Conseiller', usages=['asker', ])
conseiller12 = UserDescriptor('FELOMA103', [], email="test@test.be", fullname="FELON Maxime")
conseiller13_mu = MeetingUserDescriptor('FOTIDO146', gender='f', duty='Conseillère', usages=['asker', ])
conseiller13 = UserDescriptor('FOTIDO146', [], email="test@test.be", fullname="FOTIA Dominique")
conseiller14_mu = MeetingUserDescriptor('FRERAL093', duty='Conseiller', usages=['asker', ])
conseiller14 = UserDescriptor('FRERAL093', [], email="test@test.be", fullname="FRERE Albert")
conseiller15_mu = MeetingUserDescriptor('GAHOLA116', gender='f', duty='Conseillère', usages=['asker', ])
conseiller15 = UserDescriptor('GAHOLA116', [], email="test@test.be", fullname="GAHOUCHI Latifa")
conseiller16_mu = MeetingUserDescriptor('HERMMA071', duty='Conseiller', usages=['asker', ])
conseiller16 = UserDescriptor('HERMMA071', [], email="test@test.be", fullname="HERMAN Maurice")
conseiller17_mu = MeetingUserDescriptor('HEMBPH039', duty='Conseiller', usages=['asker', ])
conseiller17 = UserDescriptor('HEMBPH039', [], email="test@test.be", fullname="HEMBISE Philippe")
conseiller18_mu = MeetingUserDescriptor('HOEBMA186', gender='f', duty='Conseillère', usages=['asker', ])
conseiller18 = UserDescriptor('HOEBMA186', [], email="test@test.be", fullname="HOEBEKE Maryse")
conseiller19_mu = MeetingUserDescriptor('IMANHI167', duty='Conseiller', usages=['asker', ])
conseiller19 = UserDescriptor('IMANHI167', [], email="test@test.be", fullname="IMANE Hicham")
conseiller20_mu = MeetingUserDescriptor('ITALGA169', duty='Conseiller', usages=['asker', ])
conseiller20 = UserDescriptor('ITALGA169', [], email="test@test.be", fullname="ITALIANO Gaetano")
conseiller21_mu = MeetingUserDescriptor('JADODA369', duty='Conseiller', usages=['asker', ])
conseiller21 = UserDescriptor('JADODA369', [], email="test@test.be", fullname="JADOUL David")
conseiller22_mu = MeetingUserDescriptor('KADIMO133', duty='Conseiller', usages=['asker', ])
conseiller22 = UserDescriptor('KADIMO133', [], email="test@test.be", fullname="KADIM Mohamed")
conseiller23_mu = MeetingUserDescriptor('KILISE305', duty='Conseiller', usages=['asker', ])
conseiller23 = UserDescriptor('KILISE305', [], email="test@test.be", fullname="KILIC Serdar")
conseiller24_mu = MeetingUserDescriptor('MAGNPA235', duty='Conseiller', usages=['asker', ])
conseiller24 = UserDescriptor('MAGNPA235', [], email="test@test.be", fullname="MAGNETTE Paul")
conseiller25_mu = MeetingUserDescriptor('MANOLI138', gender='f', duty='Conseillère', usages=['asker', ])
conseiller25 = UserDescriptor('MANOLI138', [], email="test@test.be", fullname="MANOUVRIER Line")

council_restrictedpowerobservers = PloneGroupDescriptor('meeting-config-council_restrictedpowerobservers',
                                                        'meeting-config-council_restrictedpowerobservers',
                                                        [])
conseiller1.ploneGroups = [council_restrictedpowerobservers, ]
conseiller2.ploneGroups = [council_restrictedpowerobservers, ]
conseiller3.ploneGroups = [council_restrictedpowerobservers, ]
conseiller4.ploneGroups = [council_restrictedpowerobservers, ]
conseiller5.ploneGroups = [council_restrictedpowerobservers, ]
conseiller6.ploneGroups = [council_restrictedpowerobservers, ]
conseiller7.ploneGroups = [council_restrictedpowerobservers, ]
conseiller8.ploneGroups = [council_restrictedpowerobservers, ]
conseiller9.ploneGroups = [council_restrictedpowerobservers, ]
conseiller10.ploneGroups = [council_restrictedpowerobservers, ]
conseiller11.ploneGroups = [council_restrictedpowerobservers, ]
conseiller12.ploneGroups = [council_restrictedpowerobservers, ]
conseiller13.ploneGroups = [council_restrictedpowerobservers, ]
conseiller14.ploneGroups = [council_restrictedpowerobservers, ]
conseiller15.ploneGroups = [council_restrictedpowerobservers, ]
conseiller16.ploneGroups = [council_restrictedpowerobservers, ]
conseiller17.ploneGroups = [council_restrictedpowerobservers, ]
conseiller18.ploneGroups = [council_restrictedpowerobservers, ]
conseiller19.ploneGroups = [council_restrictedpowerobservers, ]
conseiller20.ploneGroups = [council_restrictedpowerobservers, ]
conseiller21.ploneGroups = [council_restrictedpowerobservers, ]
conseiller22.ploneGroups = [council_restrictedpowerobservers, ]
conseiller23.ploneGroups = [council_restrictedpowerobservers, ]
conseiller24.ploneGroups = [council_restrictedpowerobservers, ]
conseiller25.ploneGroups = [council_restrictedpowerobservers, ]

councilMeeting.meetingUsers = [conseiller1_mu, conseiller2_mu, conseiller3_mu, conseiller4_mu,
                               conseiller5_mu, conseiller6_mu, conseiller7_mu, conseiller8_mu,
                               conseiller9_mu, conseiller10_mu, conseiller11_mu, conseiller12_mu,
                               conseiller13_mu, conseiller14_mu, conseiller15_mu, conseiller16_mu,
                               conseiller17_mu, conseiller18_mu, conseiller19_mu, conseiller20_mu,
                               conseiller21_mu, conseiller22_mu, conseiller23_mu, conseiller24_mu,
                               conseiller25_mu]

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
        category='entetes',
        proposingGroup='secretariat',
        proposingGroupWithGroupInCharge='secretariat__groupincharge__bourgmestre',
        decision='Procès-verbal approuvé'), ]

data = PloneMeetingConfiguration(meetingFolderTitle='Mes séances',
                                 meetingConfigs=(collegeMeeting, councilMeeting),
                                 groups=[police_grp, police_compta_grp, dirgen_grp,
                                         secr_grp, info_grp, pers_grp,
                                         dirfin_grp, compta_grp, trav_grp,
                                         bourg_grp, ech1_grp, ech2_grp, ech3_grp])
data.enableUserPreferences = False
data.usersOutsideGroups = [bourgmestre, conseiller,
                           conseiller1, conseiller2, conseiller3, conseiller4, conseiller5,
                           conseiller6, conseiller7, conseiller8, conseiller9, conseiller10,
                           conseiller11, conseiller12, conseiller13, conseiller14, conseiller15,
                           conseiller16, conseiller17, conseiller18, conseiller19, conseiller20,
                           conseiller21, conseiller22, conseiller23, conseiller24, conseiller25]
# ------------------------------------------------------------------------------
