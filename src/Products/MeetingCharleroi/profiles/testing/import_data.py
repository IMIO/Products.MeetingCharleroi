# -*- coding: utf-8 -*-
from Products.PloneMeeting.config import MEETINGREVIEWERS
from Products.PloneMeeting.profiles import CategoryDescriptor
from Products.PloneMeeting.profiles import GroupDescriptor
from Products.PloneMeeting.profiles import ItemTemplateDescriptor
from Products.PloneMeeting.profiles import MeetingConfigDescriptor
from Products.PloneMeeting.profiles import MeetingFileTypeDescriptor
from Products.PloneMeeting.profiles import MeetingUserDescriptor
from Products.PloneMeeting.profiles import PloneGroupDescriptor
from Products.PloneMeeting.profiles import PloneMeetingConfiguration
from Products.PloneMeeting.profiles import PodTemplateDescriptor
from Products.PloneMeeting.profiles import RecurringItemDescriptor
from Products.PloneMeeting.profiles import UserDescriptor


# File types -------------------------------------------------------------------
annexe = MeetingFileTypeDescriptor('annexe', 'Annexe', 'attach.png', '')
annexeBudget = MeetingFileTypeDescriptor('annexeBudget', 'Article Budgetaire', 'budget.png', '')
annexeCahier = MeetingFileTypeDescriptor('annexeCahier', 'Cahier des Charges', 'cahier.gif', '')
itemAnnex = MeetingFileTypeDescriptor('item-annex', 'Other annex(es)', 'attach.png', '')
annexeDecision = MeetingFileTypeDescriptor('annexeDecision', 'Annexe a la decision', 'attach.png', '', 'item_decision')
# Some type of annexes taken from the default PloneMeeting test profile
marketingAnalysis = MeetingFileTypeDescriptor(
    'marketing-annex', 'Marketing annex(es)', 'attach.png', '', 'item_decision',
    active=False)
overheadAnalysis = MeetingFileTypeDescriptor(
    'overhead-analysis', 'Administrative overhead analysis',
    'attach.png', '')
# Advice annexes types
adviceAnnex = MeetingFileTypeDescriptor(
    'advice-annex', 'Advice annex(es)', 'attach.png', '', 'advice')
adviceLegalAnalysis = MeetingFileTypeDescriptor(
    'advice-legal-analysis', 'Advice legal analysis', 'attach.png', '', 'advice')


# Pod templates ----------------------------------------------------------------
agendaTemplate = PodTemplateDescriptor('agendaTemplate', 'Meeting agenda')
agendaTemplate.odt_file = 'Agenda.odt'
agendaTemplate.pod_portal_types = ['MeetingCollege']
agendaTemplate.tal_condition = ''

decisionsTemplate = PodTemplateDescriptor('decisionsTemplate',
                                          'Meeting decisions')
decisionsTemplate.odt_file = 'Decisions.odt'
decisionsTemplate.pod_portal_types = ['MeetingCollege']
decisionsTemplate.tal_condition = 'python:here.adapted().isDecided()'

itemTemplate = PodTemplateDescriptor('itemTemplate', 'Meeting item')
itemTemplate.odt_file = 'Item.odt'
itemTemplate.pod_portal_types = ['MeetingItemCollege']
itemTemplate.tal_condition = ''

# item templates
template1 = ItemTemplateDescriptor(id='template1',
                                   title='Tutelle CPAS',
                                   description='<p>Tutelle CPAS</p>',
                                   category='',
                                   proposingGroup='developers',
                                   templateUsingGroups=['developers', 'vendors'],
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
<p>Copie de la présente délibération sera transmise au Bureau permanent/Conseil de l'Action sociale.</p>""")
template2 = ItemTemplateDescriptor(id='template2',
                                   title='Contrôle médical systématique agent contractuel',
                                   description='<p>Contrôle médical systématique agent contractuel</p>',
                                   category='',
                                   proposingGroup='vendors',
                                   templateUsingGroups=['vendors', ],
                                   decision="""<p>Vu la loi du 26 mai 2002 instituant le droit à l’intégration sociale;</p>
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
<p><strong>Article 3</strong> : De charger le service du personnel du suivi de ce dossier.</p>""")


# Categories -------------------------------------------------------------------
categories = [
    CategoryDescriptor('deployment', 'Deployment topics'),
    CategoryDescriptor('maintenance', 'Maintenance topics'),
    CategoryDescriptor('development', 'Development topics'),
    CategoryDescriptor('events', 'Events'),
    CategoryDescriptor('research', 'Research topics'),
    CategoryDescriptor('projects', 'Projects'),
    # A vintage category
    CategoryDescriptor('marketing', 'Marketing', active=False),
    # usingGroups category
    CategoryDescriptor('subproducts', 'Subproducts wishes', usingGroups=('vendors',)),
]

# Users and groups -------------------------------------------------------------
pmManager = UserDescriptor('pmManager', [])
pmCreator1 = UserDescriptor('pmCreator1', [])
pmCreator1b = UserDescriptor('pmCreator1b', [])
pmReviewer1 = UserDescriptor('pmReviewer1', [])
pmReviewerLevel1 = UserDescriptor('pmReviewerLevel1', [],
                                  email="pmreviewerlevel1@plonemeeting.org", fullname='M. PMReviewer Level One')
pmCreator2 = UserDescriptor('pmCreator2', [])
pmReviewer2 = UserDescriptor('pmReviewer2', [])
pmReviewerLevel2 = UserDescriptor('pmReviewerLevel2', [],
                                  email="pmreviewerlevel2@plonemeeting.org", fullname='M. PMReviewer Level Two')
pmAdviser1 = UserDescriptor('pmAdviser1', [])
voter1 = UserDescriptor('voter1', [], fullname='M. Voter One')
voter2 = UserDescriptor('voter2', [], fullname='M. Voter Two')
powerobserver1 = UserDescriptor('powerobserver1',
                                [],
                                email="powerobserver1@plonemeeting.org",
                                fullname='M. Power Observer1')
# powerobserver1 is 'power observer' because in the meeting-config-college '_powerobservers' group
college_powerobservers = PloneGroupDescriptor('meeting-config-college_powerobservers',
                                              'meeting-config-college_powerobservers',
                                              [])
powerobserver1.ploneGroups = [college_powerobservers, ]
powerobserver2 = UserDescriptor('powerobserver2',
                                [],
                                email="powerobserver2@plonemeeting.org",
                                fullname='M. Power Observer2')
restrictedpowerobserver1 = UserDescriptor('restrictedpowerobserver1',
                                          [],
                                          email="restrictedpowerobserver1@plonemeeting.org",
                                          fullname='M. Restricted Power Observer 1')
college_restrictedpowerobservers = PloneGroupDescriptor('meeting-config-college_restrictedpowerobservers',
                                                        'meeting-config-college_restrictedpowerobservers',
                                                        [])
restrictedpowerobserver1.ploneGroups = [college_restrictedpowerobservers, ]
restrictedpowerobserver2 = UserDescriptor('restrictedpowerobserver2',
                                          [],
                                          email="restrictedpowerobserver2@plonemeeting.org",
                                          fullname='M. Restricted Power Observer 2')
council_restrictedpowerobservers = PloneGroupDescriptor('meeting-config-council_restrictedpowerobservers',
                                                        'meeting-config-council_restrictedpowerobservers',
                                                        [])
restrictedpowerobserver2.ploneGroups = [council_restrictedpowerobservers, ]

developers = GroupDescriptor('developers', 'Developers', 'Devel')
developers.creators.append(pmCreator1)
developers.creators.append(pmCreator1b)
developers.creators.append(pmManager)
developers.reviewers.append(pmReviewer1)
developers.reviewers.append(pmManager)
developers.observers.append(pmReviewer1)
developers.observers.append(pmManager)
developers.advisers.append(pmAdviser1)
developers.advisers.append(pmManager)
developers.serviceheads.append(pmManager)
developers.prereviewers.append(pmManager)
developers.serviceheads.append(pmReviewer1)
developers.prereviewers.append(pmReviewer1)
setattr(developers, 'signatures', 'developers signatures')
setattr(developers, 'echevinServices', 'developers')
# put pmReviewerLevel1 in first level of reviewers from what is in MEETINGREVIEWERS
getattr(developers, MEETINGREVIEWERS.keys()[-1]).append(pmReviewerLevel1)
# put pmReviewerLevel2 in second level of reviewers from what is in MEETINGREVIEWERS
getattr(developers, MEETINGREVIEWERS.keys()[0]).append(pmReviewerLevel2)

#give an advice on recurring items
vendors = GroupDescriptor('vendors', 'Vendors', 'Devil')
vendors.creators.append(pmCreator2)
vendors.reviewers.append(pmReviewer2)
vendors.observers.append(pmReviewer2)
vendors.advisers.append(pmReviewer2)
vendors.advisers.append(pmManager)
vendors.serviceheads.append(pmManager)
vendors.prereviewers.append(pmManager)
vendors.serviceheads.append(pmReviewer2)
vendors.prereviewers.append(pmReviewer2)
setattr(vendors, 'signatures', '')

# Do voters able to see items to vote for
developers.observers.append(voter1)
developers.observers.append(voter2)
vendors.observers.append(voter1)
vendors.observers.append(voter2)
# Add a vintage group
endUsers = GroupDescriptor('endUsers', 'End users', 'EndUsers', active=False)

pmManager_observer = MeetingUserDescriptor('pmManager',
                                           duty='Secrétaire de la Chancellerie',
                                           usages=['assemblyMember'])
cadranel_signer = MeetingUserDescriptor('cadranel', duty='Secrétaire',
                                        usages=['assemblyMember', 'signer'],
                                        signatureImage='SignatureCadranel.jpg',
                                        signatureIsDefault=True)
# Add meeting users (voting purposes)
muser_voter1 = MeetingUserDescriptor('voter1', duty='Voter1',
                                     usages=['assemblyMember', 'voter', ])
muser_voter2 = MeetingUserDescriptor('voter2', duty='Voter2',
                                     usages=['assemblyMember', 'voter', ])

# budget impact editors
budgetimpacteditor = UserDescriptor('budgetimpacteditor',
                                    [],
                                    email="budgetimpacteditor@plonemeeting.org",
                                    fullname='M. Budget Impact Editor')
college_budgetimpacteditors = PloneGroupDescriptor('meeting-config-college_budgetimpacteditors',
                                                   'meeting-config-college_budgetimpacteditors',
                                                   [])
budgetimpacteditor.ploneGroups = [college_budgetimpacteditors,
                                  college_powerobservers]

# Meeting configurations -------------------------------------------------------
# college
collegeMeeting = MeetingConfigDescriptor(
    'meeting-config-college', 'College Communal',
    'College communal', isDefault=True)
collegeMeeting.meetingManagers = ['pmManager', ]
collegeMeeting.assembly = 'Pierre Dupont - Bourgmestre,\n' \
                          'Charles Exemple - 1er Echevin,\n' \
                          'Echevin Un, Echevin Deux, Echevin Trois - Echevins,\n' \
                          'Jacqueline Exemple, Responsable du CPAS'
collegeMeeting.signatures = 'Pierre Dupont, Bourgmestre - Charles Exemple, Secrétaire communal'
collegeMeeting.certifiedSignatures = []
collegeMeeting.categories = categories
collegeMeeting.shortName = 'College'
collegeMeeting.meetingFileTypes = [annexe, annexeBudget, annexeCahier, itemAnnex,
                                   annexeDecision, overheadAnalysis, marketingAnalysis,
                                   adviceAnnex, adviceLegalAnalysis]
collegeMeeting.usedItemAttributes = ('toDiscuss', 'associatedGroups', 'itemIsSigned',)
collegeMeeting.itemWorkflow = 'meetingitemcommunes_workflow'
collegeMeeting.meetingWorkflow = 'meetingcommunes_workflow'
collegeMeeting.itemConditionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingItemCollegeWorkflowConditions'
collegeMeeting.itemActionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingItemCollegeWorkflowActions'
collegeMeeting.meetingConditionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingCollegeWorkflowConditions'
collegeMeeting.meetingActionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingCollegeWorkflowActions'
collegeMeeting.transitionsToConfirm = []
collegeMeeting.transitionsForPresentingAnItem = ('propose', 'proposeToRefAdmin', 'prevalidate', 'validate', 'present', )
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
                                                              'item_transition': 'accept'},

                                                             {'meeting_transition': 'backToCreated',
                                                              'item_transition': 'backToPresented'},)

collegeMeeting.meetingTopicStates = ('created', 'frozen')
collegeMeeting.decisionTopicStates = ('decided', 'closed')
collegeMeeting.recordItemHistoryStates = []
collegeMeeting.maxShownMeetings = 5
collegeMeeting.maxDaysDecisions = 60
collegeMeeting.meetingAppDefaultView = 'searchallitems'
collegeMeeting.itemDocFormats = ('odt', 'pdf')
collegeMeeting.meetingDocFormats = ('odt', 'pdf')
collegeMeeting.useAdvices = True
collegeMeeting.itemAdviceStates = ['prevalidated', ]
collegeMeeting.itemAdviceEditStates = ['prevalidated', 'validated', ]
collegeMeeting.itemAdviceViewStates = ['presented', ]
collegeMeeting.transitionsReinitializingDelays = ('backToItemCreated', )
collegeMeeting.enforceAdviceMandatoriness = False
collegeMeeting.itemPowerObserversStates = ('itemcreated', 'presented', 'accepted', 'delayed', 'refused')
collegeMeeting.itemDecidedStates = ['accepted', 'refused', 'delayed', 'accepted_but_modified', 'pre_accepted']
collegeMeeting.workflowAdaptations = ['no_publication', 'no_global_observation', 'return_to_proposing_group',
                                      'pre_validation', 'charleroi_add_refadmin']
collegeMeeting.insertingMethodsOnAddItem = ({'insertingMethod': 'on_proposing_groups',
                                             'reverse': '0'}, )
collegeMeeting.useGroupsAsCategories = True
collegeMeeting.meetingPowerObserversStates = ('frozen', 'decided', 'closed')
collegeMeeting.useCopies = True
collegeMeeting.selectableCopyGroups = [developers.getIdSuffixed('reviewers'), vendors.getIdSuffixed('reviewers'), ]
collegeMeeting.podTemplates = [agendaTemplate, decisionsTemplate, itemTemplate]
collegeMeeting.meetingConfigsToCloneTo = [{'meeting_config': 'meeting-config-council',
                                           'trigger_workflow_transitions_until': '__nothing__'}, ]
collegeMeeting.itemAutoSentToOtherMCStates = ('accepted', 'accepted_but_modified', )
collegeMeeting.recurringItems = [
    RecurringItemDescriptor(
        id='recItem1',
        description='<p>This is the first recurring item.</p>',
        title='Recurring item #1',
        proposingGroup='developers',
        decision='First recurring item approved'),

    RecurringItemDescriptor(
        id='recItem2',
        title='Recurring item #2',
        description='<p>This is the second recurring item.</p>',
        proposingGroup='developers',
        decision='Second recurring item approved'),
]
collegeMeeting.itemTemplates = (template1, template2)

# Conseil communal
councilMeeting = MeetingConfigDescriptor(
    'meeting-config-council', 'Conseil Communal',
    'Conseil Communal')
councilMeeting.meetingManagers = ['pmManager', ]
councilMeeting.assembly = 'Default assembly'
councilMeeting.signatures = 'Default signatures'
councilMeeting.certifiedSignatures = []
councilMeeting.categories = categories
councilMeeting.shortName = 'Council'
councilMeeting.meetingFileTypes = [annexe, annexeBudget, annexeCahier,
                                   itemAnnex, annexeDecision, adviceAnnex, adviceLegalAnalysis]
councilMeeting.itemWorkflow = 'meetingitemcommunes_workflow'
councilMeeting.meetingWorkflow = 'meetingcommunes_workflow'
councilMeeting.itemConditionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingItemCouncilWorkflowConditions'
councilMeeting.itemActionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingItemCouncilWorkflowActions'
councilMeeting.meetingConditionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingCouncilWorkflowConditions'
councilMeeting.meetingActionsInterface = 'Products.MeetingCharleroi.interfaces.IMeetingCouncilWorkflowActions'
councilMeeting.transitionsToConfirm = []
councilMeeting.transitionsForPresentingAnItem = ['propose', 'validate', 'present', ]
councilMeeting.onMeetingTransitionItemTransitionToTrigger = ({'meeting_transition': 'freeze',
                                                              'item_transition': 'itemfreeze'},

                                                             {'meeting_transition': 'publish',
                                                              'item_transition': 'itemfreeze'},
                                                             {'meeting_transition': 'publish',
                                                              'item_transition': 'itempublish'},

                                                             {'meeting_transition': 'decide',
                                                              'item_transition': 'itemfreeze'},
                                                             {'meeting_transition': 'decide',
                                                              'item_transition': 'itempublish'},

                                                             {'meeting_transition': 'publish_decisions',
                                                              'item_transition': 'itemfreeze'},
                                                             {'meeting_transition': 'publish_decisions',
                                                              'item_transition': 'itempublish'},
                                                             {'meeting_transition': 'publish_decisions',
                                                              'item_transition': 'accept'},

                                                             {'meeting_transition': 'close',
                                                              'item_transition': 'itemfreeze'},
                                                             {'meeting_transition': 'close',
                                                              'item_transition': 'itempublish'},
                                                             {'meeting_transition': 'close',
                                                              'item_transition': 'accept'},

                                                             {'meeting_transition': 'backToCreated',
                                                              'item_transition': 'backToPresented'},)

councilMeeting.meetingTopicStates = ('created', 'frozen', 'published')
councilMeeting.decisionTopicStates = ('decided', 'closed')
councilMeeting.itemAdviceStates = ('validated',)
councilMeeting.recordItemHistoryStates = []
councilMeeting.maxShownMeetings = 5
councilMeeting.maxDaysDecisions = 60
councilMeeting.meetingAppDefaultView = 'searchallitems'
councilMeeting.usedItemAttributes = ('toDiscuss', 'associatedGroups', 'itemIsSigned',)
councilMeeting.insertingMethodsOnAddItem = ({'insertingMethod': 'on_categories',
                                             'reverse': '0'}, )
councilMeeting.useGroupsAsCategories = False
councilMeeting.useAdvices = False
councilMeeting.itemAdviceStates = ['proposed', ]
councilMeeting.itemAdviceEditStates = ['proposed', 'validated']
councilMeeting.itemAdviceViewStates = ['presented', ]
councilMeeting.transitionsReinitializingDelays = 'backToItemCreated'
councilMeeting.enforceAdviceMandatoriness = False
councilMeeting.itemDecidedStates = ['accepted', 'refused', 'delayed', 'accepted_but_modified', 'pre_accepted']
councilMeeting.workflowAdaptations = ['no_publication', 'no_global_observation', 'return_to_proposing_group',
                                      'pre_validation', 'charleroi_add_refadmin']
councilMeeting.itemPowerObserversStates = collegeMeeting.itemPowerObserversStates
councilMeeting.meetingPowerObserversStates = collegeMeeting.meetingPowerObserversStates
councilMeeting.useCopies = True
councilMeeting.selectableCopyGroups = [developers.getIdSuffixed('reviewers'), vendors.getIdSuffixed('reviewers'), ]
councilMeeting.useVotes = True
councilMeeting.meetingUsers = [muser_voter1, muser_voter2, ]
councilMeeting.recurringItems = []
councilMeeting.itemTemplates = (template1, template2)

#no recurring items for this meetingConfig, only for tests !!!
#so we can test a meetingConfig with recurring items (college) and without (council)

data = PloneMeetingConfiguration(
    meetingFolderTitle='Mes seances',
    meetingConfigs=(collegeMeeting, councilMeeting),
    groups=(developers, vendors, endUsers))
# necessary for testSetup.test_pm_ToolAttributesAreOnlySetOnFirstImportData
data.restrictUsers = False
data.usersOutsideGroups = [voter1, voter2, powerobserver1, powerobserver2,
                           restrictedpowerobserver1, restrictedpowerobserver2,
                           budgetimpacteditor]
# ------------------------------------------------------------------------------