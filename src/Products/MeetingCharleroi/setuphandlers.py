# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2016 by Imio.be
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

import os
import logging
from DateTime import DateTime
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from Products.CMFPlone.utils import _createObjectByType
from imio.helpers.catalog import addOrUpdateIndexes
from Products.PloneMeeting.exportimport.content import ToolInitializer
from Products.MeetingCharleroi.config import CC_ARRET_OJ_CAT_ID
from Products.MeetingCharleroi.config import COMMUNICATION_CAT_ID
from Products.MeetingCharleroi.config import COUNCIL_SPECIAL_CATEGORIES
from Products.MeetingCharleroi.config import FINANCE_GROUP_ID
from Products.MeetingCharleroi.config import POLICE_GROUP_PREFIX
from Products.MeetingCharleroi.config import PROJECTNAME

__author__ = """Gauthier Bastien <g.bastien@imio.be>, Andre NUYENS <a.nuyens@imio.be>"""
__docformat__ = 'plaintext'

logger = logging.getLogger('MeetingCharleroi: setuphandlers')


def isNotMeetingCharleroiProfile(context):
    return context.readDataFile("MeetingCharleroi_marker.txt") is None


def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotMeetingCharleroiProfile(context):
        return
    wft = api.portal.get_tool('portal_workflow')
    wft.updateRoleMappings()


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotMeetingCharleroiProfile(context):
        return
    logStep("postInstall", context)
    site = context.getSite()
    # need to reinstall PloneMeeting after reinstalling MC workflows to re-apply wfAdaptations
    reinstallPloneMeeting(context, site)
    showHomeTab(context, site)
    reorderSkinsLayers(context, site)
    # add the groupsOfMatter index
    addOrUpdateIndexes(site, {'financesAdviceCategory': ('FieldIndex', {})})
    # add our own faceted criteria
    addFacetedCriteria(context, site)


def logStep(method, context):
    logger.info("Applying '%s' in profile '%s'" %
                (method, '/'.join(context._profile_path.split(os.sep)[-3:])))


def isMeetingCharleroiConfigureProfile(context):
    return context.readDataFile("MeetingCharleroi_examples_fr_marker.txt") or \
        context.readDataFile("MeetingCharleroi_cpas_marker.txt") or \
        context.readDataFile("MeetingCharleroi_bourgmestre_marker.txt") or \
        context.readDataFile("MeetingCharleroi_codir_marker.txt") or \
        context.readDataFile("MeetingCharleroi_ca_marker.txt") or \
        context.readDataFile("MeetingCharleroi_coges_marker.txt") or \
        context.readDataFile("MeetingCharleroi_testing_marker.txt")


def isMeetingCharleroiTestingProfile(context):
    return context.readDataFile("MeetingCharleroi_testing_marker.txt")


def isMeetingCharleroiMigrationProfile(context):
    return context.readDataFile("MeetingCharleroi_migrations_marker.txt")


def installMeetingCharleroi(context):
    """ Run the default profile"""
    if not isMeetingCharleroiConfigureProfile(context):
        return
    logStep("installMeetingCharleroi", context)
    portal = context.getSite()
    portal.portal_setup.runAllImportStepsFromProfile('profile-Products.MeetingCharleroi:default')


def initializeTool(context):
    '''Initialises the PloneMeeting tool based on information from the current
       profile.'''
    if not isMeetingCharleroiConfigureProfile(context):
        return

    logStep("initializeTool", context)
    # PloneMeeting is no more a dependency to avoid
    # magic between quickinstaller and portal_setup
    # so install it manually
    _installPloneMeeting(context)
    return ToolInitializer(context, PROJECTNAME).run()


def reinstallPloneMeeting(context, site):
    '''Reinstall PloneMeeting so after install methods are called and applied,
       like performWorkflowAdaptations for example.'''

    if isNotMeetingCharleroiProfile(context):
        return

    logStep("reinstallPloneMeeting", context)
    _installPloneMeeting(context)


def _installPloneMeeting(context):
    site = context.getSite()
    profileId = u'profile-Products.PloneMeeting:default'
    site.portal_setup.runAllImportStepsFromProfile(profileId)


def showHomeTab(context, site):
    """
       Make sure the 'home' tab is shown...
    """
    if isNotMeetingCharleroiProfile(context):
        return

    logStep("showHomeTab", context)

    index_html = getattr(site.portal_actions.portal_tabs, 'index_html', None)
    if index_html:
        index_html.visible = True
    else:
        logger.info("The 'Home' tab does not exist !!!")


def reorderSkinsLayers(context, site):
    """
       Re-apply MeetingCharleroi skins.xml step as the reinstallation of
       MeetingCharleroi and PloneMeeting changes the portal_skins layers order
    """
    if isNotMeetingCharleroiProfile(context) and not isMeetingCharleroiConfigureProfile(context):
        return

    logStep("reorderSkinsLayers", context)
    site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingCharleroi:default', 'skins')


def addFacetedCriteria(context, site):
    """ """
    logStep("addFacetedCriteria", context)
    tool = api.portal.get_tool('portal_plonemeeting')
    for cfg in tool.objectValues('MeetingConfig'):
        tool._enableFacetedDashboardFor(cfg.searches.searches_items,
                                        os.path.dirname(__file__) +
                                        '/faceted_conf/meetingcharleroi_dashboard_items_widgets.xml')


def finalizeExampleInstance(context):
    """
       Some parameters can not be handled by the PloneMeeting installation,
       so we handle this here
    """
    if not isMeetingCharleroiConfigureProfile(context):
        return

    # finalizeExampleInstance will behave differently if on
    # a Commune instance or CPAS instance
    specialUserId = 'bourgmestre'
    meetingConfig1Id = 'meeting-config-college'
    meetingConfig2Id = 'meeting-config-council'
    if context.readDataFile("MeetingCharleroi_cpas_marker.txt"):
        specialUserId = 'president'
        meetingConfig1Id = 'meeting-config-bp'
        meetingConfig2Id = 'meeting-config-cas'

    site = context.getSite()

    logStep("finalizeExampleInstance", context)
    # add the test users 'dfin' and 'bourgmestre' to every '_powerobservers' groups
    mTool = api.portal.get_tool('portal_membership')
    groupsTool = api.portal.get_tool('portal_groups')
    member = mTool.getMemberById(specialUserId)
    for memberId in ('dfin', 'bourgmestre', ):
        member = mTool.getMemberById(memberId)
        if member:
            groupsTool.addPrincipalToGroup(member.getId(), '%s_powerobservers' % meetingConfig1Id)
            groupsTool.addPrincipalToGroup(member.getId(), '%s_powerobservers' % meetingConfig2Id)
    # add the test user 'conseiller' only to the 'meeting-config-council_powerobservers' group
    member = mTool.getMemberById('conseiller')
    if member:
        groupsTool.addPrincipalToGroup(member.getId(), '%s_powerobservers' % meetingConfig2Id)

    # add the test user 'dfin' and 'chefCompta' to the 'meeting-config-xxx_budgetimpacteditors' groups
    for memberId in ('dfin', 'chefCompta', ):
        member = mTool.getMemberById(memberId)
        if member:
            groupsTool.addPrincipalToGroup(memberId, '%s_budgetimpacteditors' % meetingConfig1Id)
            groupsTool.addPrincipalToGroup(memberId, '%s_budgetimpacteditors' % meetingConfig2Id)

    # add some topics to the portlet_todo
    mc_college_or_bp = getattr(site.portal_plonemeeting, meetingConfig1Id)
    mc_college_or_bp.setToDoListSearches(
        [getattr(mc_college_or_bp.searches.searches_items, 'searchdecideditems'),
         getattr(mc_college_or_bp.searches.searches_items, 'searchallitemsincopy'),
         getattr(mc_college_or_bp.searches.searches_items, 'searchitemstoadvicewithdelay'),
         getattr(mc_college_or_bp.searches.searches_items, 'searchallitemstoadvice'),
         ])

    # add some topics to the portlet_todo
    mc_council_or_cas = getattr(site.portal_plonemeeting, meetingConfig2Id)
    mc_council_or_cas.setToDoListSearches(
        [getattr(mc_council_or_cas.searches.searches_items, 'searchdecideditems'),
         getattr(mc_council_or_cas.searches.searches_items, 'searchallitemsincopy'),
         ])

    # finally, re-launch plonemeetingskin and MeetingCharleroi skins step
    # because PM has been installed before the import_data profile and messed up skins layers
    site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingCharleroi:default', 'skins')

    if not context.readDataFile("MeetingCharleroi_testing_marker.txt"):
        logStep("_createFinanceGroups", context)
        _createFinancesGroup(site)

    # add demo data
    collegeMeeting, collegeExtraMeeting = addCollegeDemoData(context)
    _addCouncilDemoData(collegeMeeting, collegeExtraMeeting)


def _configureCollegeCustomAdvisers(site):
    '''
    '''
    college = getattr(site.portal_plonemeeting, 'meeting-config-college')
    college.setCustomAdvisers((
        {'delay_label': 'Incidence financi\xc3\xa8re',
         'for_item_created_until': '',
         'group': FINANCE_GROUP_ID,
         'available_on': '',
         'delay': '10',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': '',
         'delay_left_alert': '3',
         'is_linked_to_previous_row': '0',
         'for_item_created_from': '2016/05/01',
         'available_on': 'python: item.adapted().mayChangeDelayTo(10)',
         'row_id': '2016-05-01.0'},
        {'delay_label': 'Incidence financi\xc3\xa8re (urgence)',
         'for_item_created_until': '',
         'group': FINANCE_GROUP_ID,
         'available_on': '',
         'delay': '5',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': '',
         'delay_left_alert': '3',
         'is_linked_to_previous_row': '1',
         'for_item_created_from': '2016/05/01',
         'available_on': 'python: item.adapted().mayChangeDelayTo(5)',
         'row_id': '2016-05-01.1'},
        {'delay_label': 'Incidence financi\xc3\xa8re (prolongation)',
         'for_item_created_until': '',
         'group': FINANCE_GROUP_ID,
         'available_on': '',
         'delay': '20',
         'gives_auto_advice_on_help_message': '',
         'gives_auto_advice_on': '',
         'delay_left_alert': '3',
         'is_linked_to_previous_row': '1',
         'for_item_created_from': '2016/05/01',
         'available_on': 'python: item.adapted().mayChangeDelayTo(20)',
         'row_id': '2016-05-01.2'},))


def _createFinancesGroup(site):
    """
       Create the finances group.
    """
    financeGroupsData = ({'id': FINANCE_GROUP_ID,
                          'title': 'Directeur financier',
                          'acronym': 'DF', },
                         )

    tool = api.portal.get_tool('portal_plonemeeting')
    for financeGroup in financeGroupsData:
        if not hasattr(tool, financeGroup['id']):
            newGroupId = tool.invokeFactory(
                'MeetingGroup',
                id=financeGroup['id'],
                title=financeGroup['title'],
                acronym=financeGroup['acronym'],
                itemAdviceStates=('meeting-config-college__state__prevalidated_waiting_advices',),
                itemAdviceEditStates=('meeting-config-college__state__prevalidated_waiting_advices',),
                itemAdviceViewStates=('meeting-config-college__state__accepted',
                                      'meeting-config-college__state__accepted_but_modified',
                                      'meeting-config-college__state__pre_accepted',
                                      'meeting-config-college__state__delayed',
                                      'meeting-config-college__state__itemfrozen',
                                      'meeting-config-college__state__prevalidated_waiting_advices',
                                      'meeting-config-college__state__presented',
                                      'meeting-config-college__state__refused',
                                      'meeting-config-college__state__validated'))
            newGroup = getattr(tool, newGroupId)
            newGroup.processForm(values={'dummy': None})


def reorderCss(context):
    """
       Make sure CSS are correctly reordered in portal_css so things
       work as expected...
    """
    if isNotMeetingCharleroiProfile(context) and \
       not isMeetingCharleroiConfigureProfile(context):
        return

    site = context.getSite()

    logStep("reorderCss", context)

    portal_css = site.portal_css
    css = ['plonemeeting.css',
           'meeting.css',
           'meetingitem.css',
           'meetingcharleroi.css',
           'imioapps.css',
           'plonemeetingskin.css',
           'imioapps_IEFixes.css',
           'ploneCustom.css']
    for resource in css:
        portal_css.moveResourceToBottom(resource)


def addCollegeDemoData(context):
    ''' '''
    if isNotMeetingCharleroiProfile(context) and \
       not isMeetingCharleroiConfigureProfile(context):
        return

    collegeMeeting, collegeExtraMeeting = _demoData(context.getSite(), 'dgen', ('dirgen', 'personnel'))
    return collegeMeeting, collegeExtraMeeting


def _demoData(site, userId, firstTwoGroupIds, dates=[], baseDate=None, templateId='template5'):
    """ """
    wfTool = api.portal.get_tool('portal_workflow')

    def _add_finance_advice(item, newItem, last_transition):
        if item['toDiscuss'] and cfg.id == 'meeting-config-college' and \
           item['category'] in ['affaires-juridiques', 'remboursement'] and \
           last_transition == 'prevalidate':
            newItem.setOptionalAdvisers(('dirfin__rowid__unique_id_003'))
            newItem.updateLocalRoles()
            wfTool.doActionFor(newItem, 'wait_advices_from_prevalidated')
            newItem.setCompleteness('completeness_complete')
            newItem.updateLocalRoles()
            with api.env.adopt_user('dfin'):
                advice = createContentInContainer(
                    newItem,
                    'meetingadvicefinances',
                    **{'advice_group': 'dirfin',
                       'advice_type': u'positive_finance',
                       'advice_comment': RichTextValue(u'Mon commentaire')})
                wfTool.doActionFor(advice, 'proposeToFinancialEditor')
                wfTool.doActionFor(advice, 'proposeToFinancialReviewer')
                wfTool.doActionFor(advice, 'proposeToFinancialManager')
                wfTool.doActionFor(advice, 'signFinancialAdvice')
            return True
        return False

    tool = api.portal.get_tool('portal_plonemeeting')
    cfg = getattr(tool, 'meeting-config-college')
    pTool = api.portal.get_tool('plone_utils')
    mTool = api.portal.get_tool('portal_membership')
    # first we need to be sure that our IPoneMeetingLayer is set correctly
    # https://dev.plone.org/ticket/11673
    from zope.event import notify
    from zope.traversing.interfaces import BeforeTraverseEvent
    notify(BeforeTraverseEvent(site, site.REQUEST))
    # we will create elements for some users, make sure their personal
    # area is correctly configured
    # first make sure the 'Members' folder exists
    members = mTool.getMembersFolder()
    if members is None:
        _createObjectByType('Folder', site, id='Members')
    # create 5 meetings : 2 passed, 1 current and 2 future
    if not dates:
        baseDate = DateTime()
        dates = [baseDate-13, baseDate-6, baseDate+1, baseDate+8, baseDate+15]
    mTool.createMemberArea(userId)
    secrFolder = tool.getPloneMeetingFolder(cfg.getId(), userId)
    for date in dates:
        meetingId = secrFolder.invokeFactory('MeetingCollege', id=date.strftime('%Y%m%d'))
        meeting = getattr(secrFolder, meetingId)
        meeting.setDate(date)
        pTool.changeOwnershipOf(meeting, userId)
        meeting.processForm()
        # -13 meeting is closed
        if date == baseDate-13:
            wfTool.doActionFor(meeting, 'freeze')
            wfTool.doActionFor(meeting, 'decide')
            wfTool.doActionFor(meeting, 'close')
        # -6 is meeting we will insert items into
        if date == baseDate-6:
            meetingForItems = meeting
        # +1 is an extraordinary meeting we will insert extralate items into
        if date == baseDate+1:
            meeting.setExtraordinarySession(True)
            meetingForExtraLateItems = meeting

    # items dict here : the key is the user we will create the item for
    # we use item templates so content is created for the demo
    items = (
        # dirgen
        {'templateId': templateId,
         'title': u'Exemple point 1',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'affaires-juridiques',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': ('meeting-config-council', ),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Exemple point 2',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Exemple point 3',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 4',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'affaires-juridiques',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': ('meeting-config-council', ),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Exemple point 5',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        # conseil arret oj
        {'templateId': templateId,
         'title': u'Conseil Communal - OJ',
         'proposingGroup': firstTwoGroupIds[0],
         'category': CC_ARRET_OJ_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        # communication
        {'templateId': templateId,
         'title': u'Communication 1',
         'proposingGroup': firstTwoGroupIds[0],
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Communication 2',
         'proposingGroup': firstTwoGroupIds[0],
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Communication 3',
         'proposingGroup': firstTwoGroupIds[0],
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        # personnel
        {'templateId': templateId,
         'title': u'Exemple point 6',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'affaires-juridiques',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Exemple point 7',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Exemple point 8',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 9',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'affaires-juridiques',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': ('meeting-config-council', ),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Exemple point 10',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        # police
        {'templateId': templateId,
         'title': u'Communication Police 1',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Communication Police 2',
         'proposingGroup': POLICE_GROUP_PREFIX + '-compta',
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Communication Police 3',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 11',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': 'affaires-juridiques',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Exemple point 12',
         'proposingGroup': POLICE_GROUP_PREFIX + '-compta',
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': ('meeting-config-council', ),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Exemple point 13',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 14',
         'proposingGroup': POLICE_GROUP_PREFIX + '-compta',
         'category': 'affaires-juridiques',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': ('meeting-config-council', ),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Exemple point 15',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Point Emergency Conseil Police',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': 'affaires-juridiques',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': ('meeting-config-council',),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Point Emergency Conseil Normal',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': ('meeting-config-council',),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
    )

    lateItems = (
        # dirgen
        {'templateId': templateId,
         'title': u'Point urgent 1',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'affaires-juridiques',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', ),
         'bourgmestreObservations': u'Observation Bourgmestre Point urgent 1'},
        {'templateId': templateId,
         'title': u'Point urgent 2',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': ('meeting-config-council', ),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        # police
        {'templateId': templateId,
         'title': u'Point urgent Police 1',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': 'affaires-juridiques',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Point urgent Police 2',
         'proposingGroup': POLICE_GROUP_PREFIX + '-compta',
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': ('meeting-config-council', ),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Point urgent Police 3',
         'proposingGroup': POLICE_GROUP_PREFIX + '-compta',
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Point urgent Police 4',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': 'affaires-juridiques',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Point urgent Police 5',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 5',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 5',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Point Complementaire Conseil Police',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': 'affaires-juridiques',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': ('meeting-config-council',),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': templateId,
         'title': u'Point Complementaire Conseil Normal',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': ('meeting-config-council',),
         'otherMeetingConfigsClonableToPrivacy': ('meeting-config-council',),
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        )

    deposeItems = (
        {'templateId': templateId,
         'title': u'Point depose en séance standard',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Point depose Police',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        )

    extraLateItems = (
        {'templateId': templateId,
         'title': u'Point urgent séance extraordinaire 1',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': ('meeting-config-council',),
         'otherMeetingConfigsClonableToPrivacy': ('meeting-config-council', ),
         'otherMeetingConfigsClonableTo': ('meeting-config-council',),
         'bourgmestreObservations': u'Observation Bourgmestre Point urgent séance extraordinaire 1'},
        {'templateId': templateId,
         'title': u'Point urgent Police séance extraordinaire 1',
         'proposingGroup': POLICE_GROUP_PREFIX,
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': ('meeting-config-council',),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ('meeting-config-council',)},
        )

    userFolder = tool.getPloneMeetingFolder(cfg.getId(), userId)

    for step in ('normal', 'late', 'depose', 'extra_late'):
        if step == 'late':
            wfTool.doActionFor(meetingForItems, 'freeze')
            items = lateItems
        elif step == 'depose':
            items = deposeItems
        elif step == 'extra_late':
            wfTool.doActionFor(meetingForExtraLateItems, 'freeze')
            items = extraLateItems

        for item in items:
            # get the template then clone it
            template = getattr(tool.getMeetingConfig(userFolder).itemtemplates, item['templateId'])
            newItem = template.clone(newOwnerId=userId,
                                     destFolder=userFolder,
                                     newPortalType=cfg.getItemTypeName())
            newItem.setOtherMeetingConfigsClonableToEmergency(item['otherMeetingConfigsClonableToEmergency'])
            newItem.setOtherMeetingConfigsClonableToPrivacy(item['otherMeetingConfigsClonableToPrivacy'])
            newItem.setTitle(item['title'])
            newItem.setProposingGroup(item['proposingGroup'])
            # manage MeetingItem.groupInCharge
            groupInCharge = newItem.getProposingGroup(theObject=True).getGroupsInCharge()[0]
            value = '{0}__groupincharge__{1}'.format(newItem.getProposingGroup(),
                                                     groupInCharge)
            newItem.setProposingGroupWithGroupInCharge(value)
            newItem.setItemAssemblyExcused('Roger Bidon')
            newItem.setItemAssemblyAbsents('Jean-Michel Jamaila')
            newItem.setCategory(item['category'])
            newItem.setToDiscuss(item['toDiscuss'])
            newItem.setOtherMeetingConfigsClonableTo(item['otherMeetingConfigsClonableTo'])
            newItem.setPreferredMeeting(meetingForItems.UID())
            newItem.reindexObject()

            if step == 'extra_late':
                site.REQUEST['PUBLISHED'] = meetingForExtraLateItems
            else:
                site.REQUEST['PUBLISHED'] = meetingForItems
            item_received_finances_advice = False
            for transition in cfg.getTransitionsForPresentingAnItem():
                if item_received_finances_advice and transition == 'validate':
                    continue
                wfTool.doActionFor(newItem, transition)
                item_received_finances_advice = _add_finance_advice(item, newItem, transition)

            if step == 'depose':
                newItem.setListType('depose')
            newItem.reindexObject(idxs=['listType'])

    return meetingForItems, meetingForExtraLateItems


def _addCouncilDemoData(collegeMeeting,
                        collegeExtraMeeting,
                        userId='dgen',
                        firstTwoGroupIds=('dirgen', 'personnel'),
                        templateId='template1'):
    '''This needs to be called after 'addCollegeDemoData'.'''

    # create 1 meeting, insert some items, then freeze it and insert other items
    portal = api.portal.get()
    tool = api.portal.get_tool('portal_plonemeeting')
    wfTool = api.portal.get_tool('portal_workflow')
    cfg2 = getattr(tool, 'meeting-config-council')
    cfg2Id = cfg2.getId()
    dgenFolder = tool.getPloneMeetingFolder(cfg2Id, userId)
    date = DateTime() + 1
    with api.env.adopt_user(userId):
        councilCategoryIds = ['designations', 'engagements', 'contentieux']
        meetingId = dgenFolder.invokeFactory('MeetingCouncil',
                                             date=date,
                                             id=date.strftime('%Y%m%d'))
        meeting = getattr(dgenFolder, meetingId)
        meeting.processForm()
        portal.REQUEST['PUBLISHED'] = meeting
        # get every items to send to council without emergency
        itemsToCouncilNoEmergency = [
            item for item in collegeMeeting.getItems(ordered=True)
            if item.getOtherMeetingConfigsClonableTo() and not item.getOtherMeetingConfigsClonableToEmergency()]
        # send to council every items
        i = 0
        for item in itemsToCouncilNoEmergency:
            councilItem = item.cloneToOtherMeetingConfig(cfg2Id)
            # 'secret' items do not have a category, define one so it can be presented
            # 'public' items are automatically presented in the onItemDuplicated event
            if councilItem.getPrivacy() == 'secret':
                councilItem.setCategory(councilCategoryIds[i])
                i = i + 1
                if i == len(councilCategoryIds):
                    i = 0
                wfTool.doActionFor(councilItem, 'present')

        # freeze the meeting and insert emergency items
        itemsToCouncilEmergency = [
            item for item in collegeMeeting.getItems(ordered=True)
            if item.getOtherMeetingConfigsClonableTo() and item.getOtherMeetingConfigsClonableToEmergency()]
        wfTool.doActionFor(meeting, 'freeze')
        for item in itemsToCouncilEmergency[1:]:
            councilItem = item.cloneToOtherMeetingConfig(cfg2Id)
            if councilItem.getPrivacy() == 'secret':
                councilItem.setCategory(councilCategoryIds[1])
                wfTool.doActionFor(councilItem, 'present')

        # present items from collegeExtraMeeting
        for item in collegeExtraMeeting.getItems():
            if item.getOtherMeetingConfigsClonableTo():
                councilItem = item.cloneToOtherMeetingConfig(cfg2Id)
                if councilItem.getPrivacy() == 'secret':
                    councilItem.setCategory(councilCategoryIds[2])
                    wfTool.doActionFor(councilItem, 'present')

        # now add some special items, aka items using categories "proposes-par-un-conseiller"
        # "interventions" and "questions-actualite"
        # more over add some items using privacy "secret_heading"
        special_items = (
            # 'secret_heading'
            {'templateId': templateId,
             'title': u'Point entête 1',
             'proposingGroup': firstTwoGroupIds[0],
             'category': councilCategoryIds[0],
             'privacy': 'secret_heading',
             'itemInitiator': (),
             'pollType': 'secret',
             'pollTypeObservations': '',
             'bourgmestreObservations': u'Observation Bourgmestre Point entête 1'},
            {'templateId': templateId,
             'title': u'Point entête 2',
             'proposingGroup': firstTwoGroupIds[0],
             'category': councilCategoryIds[1],
             'privacy': 'secret_heading',
             'itemInitiator': (),
             'pollType': 'secret',
             'pollTypeObservations': ''},
            {'templateId': templateId,
             'title': u'Point entête 3',
             'proposingGroup': firstTwoGroupIds[0],
             'category': councilCategoryIds[2],
             'privacy': 'secret_heading',
             'itemInitiator': (),
             'pollType': 'secret',
             'pollTypeObservations': '<p>Petite note vote secret</p>'},
            # items using special categories
            {'templateId': templateId,
             'title': u'Proposition de motion 1',
             'proposingGroup': firstTwoGroupIds[0],
             'category': COUNCIL_SPECIAL_CATEGORIES[0],
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': '',
             'bourgmestreObservations': u'Observation Bourgmestre Point Proposition de motion 1'},
            {'templateId': templateId,
             'title': u'Proposition de motion 2',
             'proposingGroup': firstTwoGroupIds[0],
             'category': COUNCIL_SPECIAL_CATEGORIES[0],
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': ''},
            {'templateId': templateId,
             'title': u'Point proposé par un conseiller 1',
             'proposingGroup': firstTwoGroupIds[0],
             'category': COUNCIL_SPECIAL_CATEGORIES[1],
             'privacy': 'public',
             'itemInitiator': ('DESGXA103',),
             'pollType': 'freehand',
             'pollTypeObservations': ''},
            {'templateId': templateId,
             'title': u'Point proposé par un conseiller 2',
             'proposingGroup': firstTwoGroupIds[0],
             'category': COUNCIL_SPECIAL_CATEGORIES[1],
             'privacy': 'public',
             'itemInitiator': ('DESGXA103', 'DEVIFA128'),
             'pollType': 'freehand',
             'pollTypeObservations': '',
             'bourgmestreObservations': u'Observation Bourgmestre Point proposé par un conseiller 2'},
            {'templateId': templateId,
             'title': u'Intervention 1',
             'proposingGroup': firstTwoGroupIds[0],
             'category': COUNCIL_SPECIAL_CATEGORIES[2],
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': '<p>Une autre petite note</p>'},
            {'templateId': templateId,
             'title': u'Question d\'actualité 1',
             'proposingGroup': firstTwoGroupIds[0],
             'category': COUNCIL_SPECIAL_CATEGORIES[3],
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': ''},
            {'templateId': templateId,
             'title': u'Huis clos entête 1',
             'proposingGroup': firstTwoGroupIds[0],
             'category': COUNCIL_SPECIAL_CATEGORIES[3],
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': ''},
            {'templateId': templateId,
             'title': u'Question d\'actualité 1',
             'proposingGroup': firstTwoGroupIds[0],
             'category': COUNCIL_SPECIAL_CATEGORIES[3],
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': '',
             'bourgmestreObservations': u'Observation Bourgmestre Question d\'actualité 1'},
            {'templateId': templateId,
             'title': u'Approuve le procès-verbal de la séance à huis-clos du ...',
             'proposingGroup': firstTwoGroupIds[0],
             'category': 'entetes',
             'privacy': 'secret',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': ''},
        )

        userFolder = tool.getPloneMeetingFolder(cfg2Id, userId)
        i = 1
        wfTool.doActionFor(meeting, 'backToCreated')
        for item in special_items:
            # just insert 2 first items in the 'created' meeting, others will be inserted in a frozen meeting
            if i == 3:
                wfTool.doActionFor(meeting, 'freeze')
            i = i + 1
            # get the template then clone it
            template = getattr(tool.getMeetingConfig(userFolder).itemtemplates, item['templateId'])
            newItem = template.clone(newOwnerId=userId,
                                     destFolder=userFolder,
                                     newPortalType=cfg2.getItemTypeName())
            newItem.setTitle(item['title'])
            newItem.setItemAssemblyExcused('Roger Bidon')
            newItem.setItemAssemblyAbsents('Jean-Michel Jamaila')
            newItem.setProposingGroup(item['proposingGroup'])
            # manage MeetingItem.groupInCharge
            groupInCharge = newItem.getProposingGroup(theObject=True).getGroupsInCharge()[0]
            value = '{0}__groupincharge__{1}'.format(newItem.getProposingGroup(),
                                                     groupInCharge)
            newItem.setProposingGroupWithGroupInCharge(value)
            newItem.setPreferredMeeting(meeting.UID())
            newItem.setPrivacy(item['privacy'])
            newItem.setItemInitiator(item['itemInitiator'])
            newItem.setCategory(item['category'])
            newItem.setPollType(item['pollType'])
            newItem.setPollTypeObservations(item['pollTypeObservations'], mimetype='text/html')

            if 'bourgmestreObservations' in item:
                newItem.setBourgmestreObservations(item['bourgmestreObservations'])

            newItem.reindexObject()
            wfTool.doActionFor(newItem, 'present')

    return meeting
