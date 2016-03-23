# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneWithPackageLayer
import Products.MeetingCharleroi


MC_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                          package=Products.MeetingCharleroi,
                          name='ML_ZCML')

MC_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MC_ZCML),
                              name='MC_Z2')

MC_TESTING_PROFILE = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingCharleroi,
    additional_z2_products=('imio.dashboard',
                            'Products.MeetingCharleroi',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow',
                            'Products.PasswordStrength'),
    gs_profile_id='Products.MeetingCharleroi:testing',
    name="MC_TESTING_PROFILE")

MC_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MC_TESTING_PROFILE,), name="MC_TESTING_PROFILE_FUNCTIONAL")
