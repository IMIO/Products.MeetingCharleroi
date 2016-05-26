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

__author__ = """Gauthier Bastien <g.bastien@imio.be>, Andre NUYENS <a.nuyens@imio.be>"""
__docformat__ = 'plaintext'


import os
import logging
logger = logging.getLogger('MeetingCharleroi: setuphandlers')
from DateTime import DateTime
from plone import api
from Products.CMFPlone.utils import _createObjectByType
from imio.helpers.catalog import addOrUpdateIndexes
from Products.PloneMeeting.exportimport.content import ToolInitializer
from Products.PloneMeeting.model.adaptations import performWorkflowAdaptations
from Products.MeetingCharleroi.config import FINANCE_GROUP_ID
from Products.MeetingCharleroi.config import POLICE_GROUP_ID
from Products.MeetingCharleroi.config import PROJECTNAME


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
    #need to reinstall PloneMeeting after reinstalling MC workflows to re-apply wfAdaptations
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
    #PloneMeeting is no more a dependency to avoid
    #magic between quickinstaller and portal_setup
    #so install it manually
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
    # define default workflowAdaptations for council
    # due to some weird problems, the wfAdaptations can not be defined
    # thru the import_data...
    mc_council_or_cas.setWorkflowAdaptations(['no_global_observation', 'no_publication'])
    performWorkflowAdaptations(mc_council_or_cas, logger)
    if not context.readDataFile("MeetingCharleroi_testing_marker.txt"):
        logStep("_createFinanceGroups", context)
        _createFinancesGroup(site)

    # add demo data
    addDemoData(context)


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


def addDemoData(context):
    ''' '''
    if isNotMeetingCharleroiProfile(context) and \
       not isMeetingCharleroiConfigureProfile(context):
        return

    _demoData(context.getSite(), 'dgen', ('dirgen', 'personnel'))


def _demoData(site, userId, firstTwoGroupIds):
    """ """
    tool = api.portal.get_tool('portal_plonemeeting')
    cfg = getattr(tool, 'meeting-config-college')
    wfTool = api.portal.get_tool('portal_workflow')
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
    today = DateTime()
    dates = [today-13, today-6, today+1, today+8, today+15]
    mTool.createMemberArea(userId)
    secrFolder = tool.getPloneMeetingFolder(cfg.getId(), userId)
    for date in dates:
        meetingId = secrFolder.invokeFactory('MeetingCollege', id=date.strftime('%Y%m%d'))
        meeting = getattr(secrFolder, meetingId)
        meeting.setDate(date)
        pTool.changeOwnershipOf(meeting, userId)
        meeting.processForm()
        # -13 meeting is closed
        if date == today-13:
            wfTool.doActionFor(meeting, 'freeze')
            wfTool.doActionFor(meeting, 'decide')
            wfTool.doActionFor(meeting, 'close')
        # -6 meeting is frozen
        if date == today-6:
            wfTool.doActionFor(meeting, 'freeze')
            wfTool.doActionFor(meeting, 'decide')
        # +1 is meeting we will insert items into
        if date == today+1:
            meetingForItems = meeting

    # items dict here : the key is the user we will create the item for
    # we use item templates so content is created for the demo
    items = (
        # dirgen
        {'templateId': 'template5',
         'title': u'Exemple point 1',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'affaires-juridiques',
         'toDiscuss': True,
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': 'template5',
         'title': u'Exemple point 2',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': 'template5',
         'title': u'Exemple point 3',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': 'template5',
         'title': u'Exemple point 4',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'affaires-juridiques',
         'toDiscuss': False,
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': 'template5',
         'title': u'Exemple point 5',
         'proposingGroup': firstTwoGroupIds[0],
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableTo': ()},
        # personnel
        {'templateId': 'template5',
         'title': u'Exemple point 6',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'affaires-juridiques',
         'toDiscuss': True,
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': 'template5',
         'title': u'Exemple point 7',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': 'template5',
         'title': u'Exemple point 8',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': 'template5',
         'title': u'Exemple point 9',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'affaires-juridiques',
         'toDiscuss': False,
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': 'template5',
         'title': u'Exemple point 10',
         'proposingGroup': firstTwoGroupIds[1],
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableTo': ()},
        # police
        {'templateId': 'template5',
         'title': u'Exemple point 11',
         'proposingGroup': POLICE_GROUP_ID,
         'category': 'affaires-juridiques',
         'toDiscuss': True,
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': 'template5',
         'title': u'Exemple point 12',
         'proposingGroup': POLICE_GROUP_ID,
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': 'template5',
         'title': u'Exemple point 13',
         'proposingGroup': POLICE_GROUP_ID,
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': 'template5',
         'title': u'Exemple point 14',
         'proposingGroup': POLICE_GROUP_ID,
         'category': 'affaires-juridiques',
         'toDiscuss': False,
         'otherMeetingConfigsClonableTo': ('meeting-config-council', )},
        {'templateId': 'template5',
         'title': u'Exemple point 15',
         'proposingGroup': POLICE_GROUP_ID,
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableTo': ()},
        )

    userFolder = tool.getPloneMeetingFolder(cfg.getId(), userId)
    wfTool = api.portal.get_tool('portal_workflow')
    for item in items:
        # get the template then clone it
        template = getattr(tool.getMeetingConfig(userFolder).itemtemplates, item['templateId'])
        newItem = template.clone(newOwnerId=userId,
                                 destFolder=userFolder,
                                 newPortalType=cfg.getItemTypeName())
        newItem.setTitle(item['title'])
        newItem.setProposingGroup(item['proposingGroup'])
        newItem.setCategory(item['category'])
        newItem.setToDiscuss(item['toDiscuss'])
        newItem.setOtherMeetingConfigsClonableTo(item['otherMeetingConfigsClonableTo'])
        newItem.setPreferredMeeting(meetingForItems.UID())
        newItem.reindexObject()
        site.REQUEST['PUBLISHED'] = meetingForItems
        for transition in cfg.getTransitionsForPresentingAnItem():
            wfTool.doActionFor(newItem, transition)
