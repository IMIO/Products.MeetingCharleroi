# -*- coding: utf-8 -*-
from plone.app.testing import FunctionalTesting
from plone.testing import z2
from plone.testing import zca
from Products.MeetingCommunes.testing import MCLayer

import Products.MeetingCharleroi


MCH_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                           package=Products.MeetingCharleroi,
                           name='MCH_ZCML')

MCH_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MCH_ZCML),
                               name='MCH_Z2')

MCH_TESTING_PROFILE = MCLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingCharleroi,
    additional_z2_products=('imio.dashboard',
                            'Products.MeetingCharleroi',
                            'Products.MeetingCommunes',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow',
                            'Products.PasswordStrength'),
    gs_profile_id='Products.MeetingCharleroi:testing',
    name="MCH_TESTING_PROFILE")

MCH_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MCH_TESTING_PROFILE,), name="MCH_TESTING_PROFILE_FUNCTIONAL")
