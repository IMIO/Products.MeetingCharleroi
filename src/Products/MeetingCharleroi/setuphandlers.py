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
import datetime
from datetime import timedelta

from Products.MeetingCommunes.config import PORTAL_CATEGORIES
from collective.eeafaceted.dashboard.utils import addFacetedCriteria
from imio.helpers.catalog import addOrUpdateIndexes
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from imio.helpers.content import get_vocab
from plone.memoize.forever import _memos
from Products.CMFPlone.utils import _createObjectByType
from Products.MeetingCharleroi.config import CC_ARRET_OJ_CAT_ID, COUNCIL_DEFAULT_CLASSIFIER
from Products.MeetingCharleroi.config import COMMUNICATION_CAT_ID
from Products.MeetingCharleroi.config import COUNCIL_DEFAULT_CATEGORY
from Products.MeetingCharleroi.config import COUNCIL_DEFAULT_CLASSIFIER
from Products.MeetingCharleroi.config import COUNCIL_SPECIAL_CATEGORIES
from Products.MeetingCharleroi.config import POLICE_GROUP_PREFIX
from Products.MeetingCharleroi.config import PROJECTNAME
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.MeetingCommunes.config import PORTAL_CATEGORIES
from Products.PloneMeeting.exportimport.content import ToolInitializer
from Products.PloneMeeting.utils import org_id_to_uid

import logging
import os


logger = logging.getLogger('MeetingCharleroi: setuphandlers')


def isNotMeetingCharleroiProfile(context):
    return context.readDataFile("MeetingCharleroi_marker.txt") is None


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


def _addFacetedCriteria(context, site):
    """ """
    logStep("addFacetedCriteria", context)
    tool = api.portal.get_tool('portal_plonemeeting')
    xmlpath = os.path.join(os.path.dirname(__file__),
                           'faceted_conf/meetingcharleroi_dashboard_items_widgets.xml')
    for cfg in tool.objectValues('MeetingConfig'):
        obj = cfg.searches.searches_items
        addFacetedCriteria(obj, xmlpath)


def finalizeExampleInstance(context):
    """
       Some parameters can not be handled by the PloneMeeting installation,
       so we handle this here
    """
    if not isMeetingCharleroiConfigureProfile(context):
        return

    site = context.getSite()
    tool = site.portal_plonemeeting

    # finalizeExampleInstance will behave differently if on
    # a Commune instance or CPAS instance
    specialUserId = 'bourgmestre'
    meetingConfig1Id = tool.objectValues('MeetingConfig')[0].getId()
    meetingConfig2Id = tool.objectValues('MeetingConfig')[1].getId()

    logStep("finalizeExampleInstance", context)

    # add our own faceted criteria
    _addFacetedCriteria(context, site)

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
    mc1 = getattr(site.portal_plonemeeting, meetingConfig1Id)
    mc1.setToDoListSearches(
        [getattr(mc1.searches.searches_items, 'searchdecideditems').UID(),
         getattr(mc1.searches.searches_items, 'searchallitemsincopy').UID(),
         getattr(mc1.searches.searches_items, 'searchitemstoadvicewithdelay').UID(),
         getattr(mc1.searches.searches_items, 'searchallitemstoadvice').UID(),
         ])

    # add some topics to the portlet_todo
    mc2 = getattr(site.portal_plonemeeting, meetingConfig2Id)
    mc2.setToDoListSearches(
        [getattr(mc2.searches.searches_items, 'searchdecideditems').UID(),
         getattr(mc2.searches.searches_items, 'searchallitemsincopy').UID(),
         ])

    # finally, re-launch plonemeetingskin and MeetingCharleroi skins step
    # because PM has been installed before the import_data profile and messed up skins layers
    site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingCharleroi:default', 'skins')

    # add demo data
    collegeMeeting, collegeExtraMeeting = addCollegeDemoData(context)
    _addCouncilDemoData(collegeMeeting, collegeExtraMeeting)


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


def _demoData(site, userId, firstTwoGroupIds, dates=[], templateId='template5'):
    """ """
    wfTool = api.portal.get_tool('portal_workflow')
    tool = api.portal.get_tool('portal_plonemeeting')
    cfg1 = tool.objectValues('MeetingConfig')[0]
    cfg1_id = cfg1.getId()
    cfg2 = tool.objectValues('MeetingConfig')[1]
    cfg2_id = cfg2.getId()

    def _add_finance_advice(item, newItem, last_transition):
        if item['toDiscuss'] and \
                item['category'] in ['affaires-juridiques', 'remboursement'] and \
                last_transition == 'prevalidate':
            finance_group = finance_group_uid()
            if finance_group:
                finance_advice_id = '{0}__rowid__unique_id_002'.format(finance_group)
                optional_advisers = get_vocab(
                    newItem, 'Products.PloneMeeting.vocabularies.itemoptionaladvicesvocabulary')
                if finance_advice_id not in optional_advisers:
                    _memos.clear()
                    finance_group = finance_group_uid()
                    finance_advice_id = '{0}__rowid__unique_id_002'.format(finance_group)
                newItem.setOptionalAdvisers((finance_advice_id, ))
                newItem.update_local_roles()
                wfTool.doActionFor(newItem, 'wait_advices_from_prevalidated')
                newItem.setCompleteness('completeness_complete')
                newItem.update_local_roles()
                with api.env.adopt_user('dfin'):
                    advice = createContentInContainer(
                        newItem,
                        'meetingadvicefinances',
                        **{'advice_group': finance_group,
                           'advice_type': u'positive_finance',
                           'advice_comment': RichTextValue(u'Mon commentaire')})
                    wfTool.doActionFor(advice, 'proposeToFinancialEditor')
                    wfTool.doActionFor(advice, 'proposeToFinancialReviewer')
                    wfTool.doActionFor(advice, 'proposeToFinancialManager')
                    wfTool.doActionFor(advice, 'signFinancialAdvice')
                return True
        return False

    tool = api.portal.get_tool('portal_plonemeeting')
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
    today = datetime.datetime.now()
    if not dates:
        dates = [today - timedelta(days=13),
                 today - timedelta(days=6),
                 today + timedelta(days=1),
                 today + timedelta(days=8),
                 today + timedelta(days=15)]
    mTool.createMemberArea(userId)
    secrFolder = tool.getPloneMeetingFolder(cfg1_id, userId)
    for date in dates:
        meetingId = secrFolder.invokeFactory(
            cfg1.getMeetingTypeName(),
            id=date.strftime('%Y%m%d'),
            date=date)
        meeting = getattr(secrFolder, meetingId)
        meeting.date = date
        pTool.changeOwnershipOf(meeting, userId)
        meeting.processForm()
        # -13 meeting is closed
        if date == today - timedelta(days=13):
            wfTool.doActionFor(meeting, 'freeze')
            wfTool.doActionFor(meeting, 'decide')
            wfTool.doActionFor(meeting, 'close')
        # -6 meeting is frozen
        if date == today - timedelta(days=6):
            meetingForItems = meeting
        # +1 is an extraordinary meeting we will insert extralate items into
        if date == today + timedelta(days=1):
            meeting.extraordinary_session = True
            meetingForExtraLateItems = meeting

    # items dict here : the key is the user we will create the item for
    # we use item templates so content is created for the demo
    items = (
        # dirgen
        {'templateId': templateId,
         'title': u'Exemple point 1',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (cfg2_id, ),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Exemple point 2',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Exemple point 3',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 4',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (cfg2_id, ),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Exemple point 5',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        # conseil arret oj
        {'templateId': templateId,
         'title': u'Conseil Communal - OJ',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': CC_ARRET_OJ_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        # communication
        {'templateId': templateId,
         'title': u'Communication 1',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Communication 2',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Communication 3',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        # personnel
        {'templateId': templateId,
         'title': u'Exemple point 6',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[1]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Exemple point 7',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[1]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Exemple point 8',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[1]),
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 9',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[1]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (cfg2_id, ),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Exemple point 10',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[1]),
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        # police
        {'templateId': templateId,
         'title': u'Communication Police 1',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Communication Police 2',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX + '-compta'),
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Communication Police 3',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': COMMUNICATION_CAT_ID,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 11',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Exemple point 12',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX + '-compta'),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (cfg2_id, ),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Exemple point 13',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 14',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX + '-compta'),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (cfg2_id, ),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Exemple point 15',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Point Emergency Conseil Police',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (cfg2_id,),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Point Emergency Conseil Normal',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (cfg2_id,),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
    )

    lateItems = (
        # dirgen
        {'templateId': templateId,
         'title': u'Point urgent 1',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id, ),
         'bourgmestreObservations': u'Observation Bourgmestre Point urgent 1'},
        {'templateId': templateId,
         'title': u'Point urgent 2',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (cfg2_id, ),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        # police
        {'templateId': templateId,
         'title': u'Point urgent Police 1',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Point urgent Police 2',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX + '-compta'),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (cfg2_id, ),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Point urgent Police 3',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX + '-compta'),
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Point urgent Police 4',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Point urgent Police 5',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 5',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[1]),
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Exemple point 5',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[1]),
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Point Complementaire Conseil Police',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (cfg2_id,),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id, )},
        {'templateId': templateId,
         'title': u'Point Complementaire Conseil Normal',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (cfg2_id,),
         'otherMeetingConfigsClonableToPrivacy': (cfg2_id,),
         'otherMeetingConfigsClonableTo': (cfg2_id, )}, )

    deposeItems = (
        {'templateId': templateId,
         'title': u'Point depose en séance standard',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[1]),
         'category': 'remboursement',
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()},
        {'templateId': templateId,
         'title': u'Point depose Police',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': 'remboursement',
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': ()}, )

    extraLateItems = (
        {'templateId': templateId,
         'title': u'Point urgent séance extraordinaire 1',
         'proposingGroup': org_id_to_uid(firstTwoGroupIds[1]),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': False,
         'otherMeetingConfigsClonableToEmergency': (cfg2_id,),
         'otherMeetingConfigsClonableToPrivacy': (cfg2_id, ),
         'otherMeetingConfigsClonableTo': (cfg2_id,),
         'bourgmestreObservations': u'Observation Bourgmestre Point urgent séance extraordinaire 1'},
        {'templateId': templateId,
         'title': u'Point urgent Police séance extraordinaire 1',
         'proposingGroup': org_id_to_uid(POLICE_GROUP_PREFIX),
         'category': COUNCIL_DEFAULT_CATEGORY,
         'toDiscuss': True,
         'otherMeetingConfigsClonableToEmergency': (cfg2_id,),
         'otherMeetingConfigsClonableToPrivacy': (),
         'otherMeetingConfigsClonableTo': (cfg2_id,)}, )

    userFolder = tool.getPloneMeetingFolder(cfg1_id, userId)

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
            with api.env.adopt_user(username=userId):
                tool.invalidateAllCache()
                newItem = template.clone(newOwnerId=userId,
                                         destFolder=userFolder,
                                         newPortalType=cfg1.getItemTypeName())
                newItem.setOtherMeetingConfigsClonableToEmergency(item['otherMeetingConfigsClonableToEmergency'])
                newItem.setOtherMeetingConfigsClonableToPrivacy(item['otherMeetingConfigsClonableToPrivacy'])
                newItem.setTitle(item['title'])
                newItem.setProposingGroup(item['proposingGroup'])
                # manage MeetingItem.groupInCharge
                groupInCharge = newItem.getProposingGroup(theObject=True).get_groups_in_charge()[0]
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
                for transition in cfg1.getTransitionsForPresentingAnItem():
                    if item_received_finances_advice and transition == 'validate':
                        continue
                    try:  # Try them all
                        wfTool.doActionFor(newItem, transition)
                    except:
                        continue
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
    tool = api.portal.get_tool('portal_plonemeeting')
    cfg2 = tool.objectValues('MeetingConfig')[1]
    cfg2Id = cfg2.getId()
    dgenFolder = tool.getPloneMeetingFolder(cfg2Id, userId)
    date = (datetime.datetime.today() + timedelta(1))
    with api.env.adopt_user(userId):
        councilCategoryIds = ['designations', 'engagements', 'contentieux']
        meetingId = dgenFolder.invokeFactory(
                cfg2.getMeetingTypeName(),
                id=date.strftime('%Y%m%d'),
                date=date)
        meeting = getattr(dgenFolder, meetingId)
        meeting.processForm()
        portal.REQUEST['PUBLISHED'] = meeting
        # get every items to send to council without emergency
        itemsToCouncilNoEmergency = [
            item for item in collegeMeeting.get_items(ordered=True)
            if item.getOtherMeetingConfigsClonableTo() and
            not item.getOtherMeetingConfigsClonableToEmergency()]
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
                councilItem.reindexObject()

        # freeze the meeting and insert emergency items
        itemsToCouncilEmergency = [
            item for item in collegeMeeting.get_items(ordered=True)
            if item.getOtherMeetingConfigsClonableTo() and item.getOtherMeetingConfigsClonableToEmergency()]
        wfTool.doActionFor(meeting, 'freeze')
        for item in itemsToCouncilEmergency[1:]:
            councilItem = item.cloneToOtherMeetingConfig(cfg2Id)
            if councilItem.getPrivacy() == 'secret':
                councilItem.setCategory(councilCategoryIds[1])
                wfTool.doActionFor(councilItem, 'present')
                councilItem.reindexObject()

        # present items from collegeExtraMeeting
        for item in collegeExtraMeeting.get_items():
            if item.getOtherMeetingConfigsClonableTo():
                councilItem = item.cloneToOtherMeetingConfig(cfg2Id)
                if councilItem.getPrivacy() == 'secret':
                    councilItem.setCategory(councilCategoryIds[2])
                    wfTool.doActionFor(councilItem, 'present')
                    councilItem.reindexObject()

        # now add some special items, aka items using categories "proposes-par-un-conseiller"
        # "interventions" and "questions-actualite"
        # more over add some items using privacy "secret_heading"
        special_items = (
            # 'secret_heading'
            {'templateId': templateId,
             'title': u'Point entête 1',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': councilCategoryIds[0],
             'classifier': COUNCIL_DEFAULT_CLASSIFIER,
             'privacy': 'secret_heading',
             'itemInitiator': (),
             'pollType': 'secret',
             'pollTypeObservations': '',
             'bourgmestreObservations': u'Observation Bourgmestre Point entête 1'},
            {'templateId': templateId,
             'title': u'Point entête 2',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': councilCategoryIds[1],
             'classifier': COUNCIL_DEFAULT_CLASSIFIER,
             'privacy': 'secret_heading',
             'itemInitiator': (),
             'pollType': 'secret',
             'pollTypeObservations': ''},
            {'templateId': templateId,
             'title': u'Point entête 3',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': councilCategoryIds[2],
             'classifier': COUNCIL_DEFAULT_CLASSIFIER,
             'privacy': 'secret_heading',
             'itemInitiator': (),
             'pollType': 'secret',
             'pollTypeObservations': '<p>Petite note vote secret</p>'},
            # items using special categories
            {'templateId': templateId,
             'title': u'Proposition de motion 1',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': COUNCIL_SPECIAL_CATEGORIES[0],
             'classifier': PORTAL_CATEGORIES[0].id,
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': '',
             'bourgmestreObservations': u'Observation Bourgmestre Point Proposition de motion 1'},
            {'templateId': templateId,
             'title': u'Proposition de motion 2',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': COUNCIL_SPECIAL_CATEGORIES[0],
             'classifier': PORTAL_CATEGORIES[1].id,
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': ''},
            {'templateId': templateId,
             'title': u'Point proposé par un conseiller 1',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': COUNCIL_SPECIAL_CATEGORIES[1],
             'classifier': PORTAL_CATEGORIES[2].id,
             'privacy': 'public',
             'itemInitiator': ('DESGXA103',),
             'pollType': 'freehand',
             'pollTypeObservations': ''},
            {'templateId': templateId,
             'title': u'Point proposé par un conseiller 2',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': COUNCIL_SPECIAL_CATEGORIES[1],
             'classifier': PORTAL_CATEGORIES[3].id,
             'privacy': 'public',
             'itemInitiator': ('DESGXA103', 'DEVIFA128'),
             'pollType': 'freehand',
             'pollTypeObservations': '',
             'bourgmestreObservations': u'Observation Bourgmestre Point proposé par un conseiller 2'},
            {'templateId': templateId,
             'title': u'Intervention 1',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': COUNCIL_SPECIAL_CATEGORIES[2],
             'classifier': PORTAL_CATEGORIES[4].id,
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': '<p>Une autre petite note</p>'},
            {'templateId': templateId,
             'title': u'Question d\'actualité 1',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': COUNCIL_SPECIAL_CATEGORIES[3],
             'classifier': PORTAL_CATEGORIES[5].id,
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': ''},
            {'templateId': templateId,
             'title': u'Huis clos entête 1',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': COUNCIL_SPECIAL_CATEGORIES[3],
             'classifier': PORTAL_CATEGORIES[6].id,
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': ''},
            {'templateId': templateId,
             'title': u'Question d\'actualité 1',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': COUNCIL_SPECIAL_CATEGORIES[3],
             'classifier': PORTAL_CATEGORIES[7].id,
             'privacy': 'public',
             'itemInitiator': (),
             'pollType': 'freehand',
             'pollTypeObservations': '',
             'bourgmestreObservations': u'Observation Bourgmestre Question d\'actualité 1'},
            {'templateId': templateId,
             'title': u'Approuve le procès-verbal de la séance à huis-clos du ...',
             'proposingGroup': org_id_to_uid(firstTwoGroupIds[0]),
             'category': 'entetes',
             'classifier': PORTAL_CATEGORIES[8].id,
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
            groupInCharge = newItem.getProposingGroup(theObject=True).get_groups_in_charge()[0]
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

            newItem.at_post_create_script()
            newItem.reindexObject()
            wfTool.doActionFor(newItem, 'present')

    return meeting
