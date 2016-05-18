# -*- coding: utf-8 -*-
#
# File: config.py
#
# Copyright (c) 2016 by Imio.be
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Gauthier Bastien <g.bastien@imio.be>, Andre NUYENS <a.nuyens@imio.be>"""
__docformat__ = 'plaintext'


# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from collections import OrderedDict
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = "MeetingCharleroi"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Contributor'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here
from Products.PloneMeeting import config as PMconfig
CHARLEROIROLES = {}
CHARLEROIROLES['serviceheads'] = 'MeetingServiceHead'
PMconfig.MEETINGROLES.update(CHARLEROIROLES)
PMconfig.MEETING_GROUP_SUFFIXES = PMconfig.MEETINGROLES.keys()

CHARLEROIMEETINGREVIEWERS = OrderedDict([('reviewers', 'prevalidated'),
                                         ('prereviewers', 'proposed_to_refadmin'),
                                         ('serviceheads', 'proposed'), ])
PMconfig.MEETINGREVIEWERS = CHARLEROIMEETINGREVIEWERS

# Define PloneMeeting-specific permissions
AddAnnex = 'PloneMeeting: Add annex'
setDefaultRoles(AddAnnex, ('Manager', 'Owner'))
# We need 'AddAnnex', which is a more specific permission than
# 'PloneMeeting: Add MeetingFile', because decision-related annexes, which are
# also MeetingFile instances, must be secured differently.
# There is no permission linked to annex deletion. Deletion of annexes is allowed
# if one has the permission 'Modify portal content' on the corresponding item.
ReadDecision = 'PloneMeeting: Read decision'
WriteDecision = 'PloneMeeting: Write decision'
setDefaultRoles(ReadDecision, ('Manager',))
setDefaultRoles(WriteDecision, ('Manager',))

STYLESHEETS = [{'id': 'meetingcharleroi.css',
                'title': 'MeetingCharleroi CSS styles'}]

# text about FD advice used in templates
FINANCE_ADVICE_LEGAL_TEXT_PRE = "<p>Attendu la demande d'avis adressée sur "\
    "base d'un dossier complet au Directeur financier en date du {0}.<br/></p>"

FINANCE_ADVICE_LEGAL_TEXT = "<p>Attendu l'avis {0} du Directeur financier "\
    "rendu en date du {1} conformément à l'article L1124-40 du Code de la "\
    "démocratie locale et de la décentralisation,</p>"

FINANCE_ADVICE_LEGAL_TEXT_NOT_GIVEN = "<p>Attendu l'absence d'avis du "\
    "Directeur financier rendu dans le délai prescrit à l'article L1124-40 "\
    "du Code de la démocratie locale et de la décentralisation,</p>"

FINANCE_GROUP_ID = "dirfin"

CHARLEROI_ADVICE_STATES_ALIVE = ('advice_under_edit',
                                 'proposed_to_financial_controller',
                                 'proposed_to_financial_reviewer',
                                 'proposed_to_financial_manager',
                                 'financial_advice_signed', )
CHARLEROI_ADVICE_STATES_ENDED = ('advice_given', )
PMconfig.ADVICE_STATES_ALIVE = CHARLEROI_ADVICE_STATES_ALIVE
PMconfig.ADVICE_STATES_ENDED = CHARLEROI_ADVICE_STATES_ENDED

# in those states, finance advice can still be given
FINANCE_GIVEABLE_ADVICE_STATES = ('prevalidated_waiting_advices', )

# comment used when a finance advice has been signed and so historized
FINANCE_ADVICE_HISTORIZE_COMMENTS = 'financial_advice_signed_historized_comments'

# copy/pasted from MeetingCommunes because importing from MeetingCommunes break
# the constant monkey patches...
FINANCE_GROUP_SUFFIXES = ('financialcontrollers',
                          'financialreviewers',
                          'financialmanagers')
CHARLEROI_EXTRA_ADVICE_SUFFIXES = {FINANCE_GROUP_ID: list(FINANCE_GROUP_SUFFIXES)}
PMconfig.EXTRA_ADVICE_SUFFIXES = CHARLEROI_EXTRA_ADVICE_SUFFIXES

# advice categories
ADVICE_CATEGORIES = (
    ('acquisitions', u'1. Acquisitions'),
    ('attributions', u'2. Attributions'),
    ('autres', u'3. Autres'),
    ('avenants', u'4. Avenants'),
    ('entites-consolidees', u'5. Entités consolidées'),
    ('conventions', u'6. Conventions'),
    ('dossiers-budgetaires', u'7. Dossiers budgétaires'),
    ('etats-d-avancement-decomptes-factures', u'8. États d’avancement, décomptes, factures'),
    ('jugements-transactions', '9. Jugements, transactions'),
    ('modes-et-conditions', '10. Modes et conditions'),
    ('non-valeurs', '11. Non-valeurs'),
    ('octrois-de-subsides', '12. Octrois de subsides'),
    ('recrutements-demissions-fins-de-contrats', '13. Recrutements, démissions, fins de contrats'),
    ('taxes-et-redevances', '14. Taxes et redevances'), )

# advice motivation categories
ADVICE_MOTIVATION_CATEGORIES = (
    ('pieces-annexes-absentes-incompletes-ou-inappropriees',
     u'A. Pièces annexes absentes, incomplètes ou inappropriées'),
    ('problemes-de-definition-du-cadre-legal-et-reglementaire-ou-de-respect-de-celui-ci',
     u'B. Problèmes de définition du cadre légal et réglementaire ou de respect de celui-ci'),
    ('problemes-de-redaction-du-projet-de-deliberation',
     u'C. Problèmes de rédaction du projet de délibération'),
    ('erreurs-sur-les-montants',
     u'D. Erreurs sur les montants'),
    ('non-conformite-avec-la-loi-sur-les-marches',
     u'E. Non-conformité avec la loi sur les marchés'),
    ('probleme-de-disponibilite-budgetaire-ou-de-reference-correcte-aux-articles-du-budget',
     u'F. Problème de disponibilité budgétaire ou de référence correcte aux articles du budget'),
    ('motivation-insuffisante-ou-inappropriee',
     u'G. Motivation insuffisante ou inappropriée'),
    ('competence-du-college-ou-du-conseil-communal',
     u'H. Compétence du Collège ou du conseil communal'),
    ('autres',
     u'I. Autres'), )
