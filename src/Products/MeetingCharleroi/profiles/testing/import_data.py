# -*- coding: utf-8 -*-

from copy import deepcopy
from Products.PloneMeeting.profiles.testing import import_data as pm_import_data
from Products.MeetingCommunes.profiles.testing import import_data as mc_import_data
from Products.PloneMeeting.config import MEETINGREVIEWERS
from Products.PloneMeeting.profiles import UserDescriptor

data = deepcopy(mc_import_data.data)

# Users
pmFinController = UserDescriptor('pmFinController', [])
pmFinEditor = UserDescriptor('pmFinEditor', [])
pmFinReviewer = UserDescriptor('pmFinReviewer', [])
pmFinManager = UserDescriptor('pmFinManager', [])
dfin = UserDescriptor('dfin', [])
pmServiceHead1 = UserDescriptor('pmServiceHead1', [])
pmRefAdmin1 = UserDescriptor('pmRefAdmin1', [])
# Inherited users
pmReviewer1 = deepcopy(pm_import_data.pmReviewer1)
pmReviewer2 = deepcopy(pm_import_data.pmReviewer2)
pmReviewerLevel1 = deepcopy(pm_import_data.pmReviewerLevel1)
pmReviewerLevel2 = deepcopy(pm_import_data.pmReviewerLevel2)
pmManager = deepcopy(pm_import_data.pmManager)

# Groups
developers = data.orgs[0]
developers.serviceheads.append(pmServiceHead1)
developers.serviceheads.append(pmRefAdmin1)
developers.serviceheads.append(pmReviewer1)
developers.serviceheads.append(pmManager)
developers.prereviewers.append(pmRefAdmin1)
developers.prereviewers.append(pmReviewer1)
developers.prereviewers.append(pmManager)
# move pmReviewerLevel1 from prereviewers (that is second reviewer level)
# to serviceheads that is first reviewer level
developers.prereviewers = [descr for descr in developers.prereviewers if descr.id != 'pmReviewerLevel1']
getattr(developers, MEETINGREVIEWERS['meetingitemcommunes_workflow'].keys()[-1]).append(pmReviewerLevel1)

vendors = data.orgs[1]
vendors.serviceheads.append(pmReviewer2)
vendors.prereviewers.append(pmReviewer2)

# College
collegeMeeting = deepcopy(mc_import_data.collegeMeeting)
collegeMeeting.itemConditionsInterface = \
    'Products.MeetingCharleroi.interfaces.IMeetingItemCharleroiCollegeWorkflowConditions'
collegeMeeting.itemActionsInterface = \
    'Products.MeetingCharleroi.interfaces.IMeetingItemCharleroiCollegeWorkflowActions'
collegeMeeting.meetingConditionsInterface = \
    'Products.MeetingCharleroi.interfaces.IMeetingCharleroiCollegeWorkflowConditions'
collegeMeeting.meetingActionsInterface = \
    'Products.MeetingCharleroi.interfaces.IMeetingCharleroiCollegeWorkflowActions'
collegeMeeting.transitionsToConfirm = []
collegeMeeting.transitionsForPresentingAnItem = ['propose', 'proposeToRefAdmin',
                                                 'prevalidate', 'validate', 'present', ]
collegeMeeting.itemAdviceStates = ['prevalidated', ]
collegeMeeting.itemAdviceEditStates = ['prevalidated', 'validated']
collegeMeeting.workflowAdaptations = ['no_publication', 'no_global_observation',
                                      'pre_validation', 'charleroi_add_refadmin',
                                      'charleroi_return_to_any_state_when_prevalidated',
                                      'waiting_advices']

# Council
councilMeeting = deepcopy(mc_import_data.councilMeeting)
councilMeeting.itemConditionsInterface = \
    'Products.MeetingCharleroi.interfaces.IMeetingItemCharleroiCouncilWorkflowConditions'
councilMeeting.itemActionsInterface = \
    'Products.MeetingCharleroi.interfaces.IMeetingItemCharleroiCouncilWorkflowActions'
councilMeeting.meetingConditionsInterface = \
    'Products.MeetingCharleroi.interfaces.IMeetingCharleroiCouncilWorkflowConditions'
councilMeeting.meetingActionsInterface = \
    'Products.MeetingCharleroi.interfaces.IMeetingCharleroiCouncilWorkflowActions'

data.meetingConfigs = (collegeMeeting, councilMeeting)
data.usersOutsideGroups += [pmFinController, pmFinEditor, pmFinReviewer, pmFinManager, dfin]
