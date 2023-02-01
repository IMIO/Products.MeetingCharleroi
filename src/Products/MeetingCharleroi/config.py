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

from collections import OrderedDict
from Products.CMFCore.permissions import setDefaultRoles
from Products.PloneMeeting import config as PMconfig

PROJECTNAME = "MeetingCharleroi"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Contributor'))

product_globals = globals()

CHARLEROI_COLLEGE_ITEM_WF_VALIDATION_LEVELS = (
    {'state': 'itemcreated',
     'state_title': 'itemcreated',
     'leading_transition': '-',
     'leading_transition_title': '-',
     'back_transition': 'backToItemCreated',
     'back_transition_title': 'backToItemCreated',
     'suffix': 'creators',
     'extra_suffixes': [],
     'enabled': '1',
     },
    {'state': 'proposed',
     'state_title': 'proposed',
     'leading_transition': 'propose',
     'leading_transition_title': 'propose',
     'back_transition': 'backToProposed',
     'back_transition_title': 'backToProposed',
     'suffix': 'serviceheads',
     'extra_suffixes': [],
     'enabled': '1',
     },
    {'state': 'proposed_to_refadmin',
     'state_title': 'proposed_to_refadmin',
     'leading_transition': 'proposeToRefAdmin',
     'leading_transition_title': 'proposeToRefAdmin',
     'back_transition': 'backToProposedToRefAdmin',
     'back_transition_title': 'backToProposedToRefAdmin',
     'suffix': 'prereviewers',
     'extra_suffixes': [],
     'enabled': '1',
     },
    {'state': 'prevalidated',
     'state_title': 'prevalidated',
     'leading_transition': 'prevalidate',
     'leading_transition_title': 'prevalidate',
     'back_transition': 'backToPrevalidated',
     'back_transition_title': 'backToPrevalidated',
     'suffix': 'reviewers',
     'extra_suffixes': [],
     'enabled': '1',
     },
)
CHARLEROI_COUNCIL_ITEM_WF_VALIDATION_LEVELS = (
    {'state': 'itemcreated',
     'state_title': 'itemcreated',
     'leading_transition': '-',
     'leading_transition_title': '-',
     'back_transition': 'backToItemCreated',
     'back_transition_title': 'backToItemCreated',
     'suffix': 'creators',
     'extra_suffixes': [],
     'enabled': '0',
     },
    {'state': 'proposed',
     'state_title': 'proposed',
     'leading_transition': 'propose',
     'leading_transition_title': 'propose',
     'back_transition': 'backToProposed',
     'back_transition_title': 'backToProposed',
     'suffix': 'serviceheads',
     'extra_suffixes': [],
     'enabled': '0',
     },
    {'state': 'prevalidated',
     'state_title': 'prevalidated',
     'leading_transition': 'prevalidate',
     'leading_transition_title': 'prevalidate',
     'back_transition': 'backToPrevalidated',
     'back_transition_title': 'backToPrevalidated',
     'suffix': 'reviewers',
     'extra_suffixes': [],
     'enabled': '0',
     },
)


# text about FD advice used in templates
FINANCE_ADVICE_LEGAL_TEXT_PRE = "<p>Attendu la demande d'avis adressée sur " \
                                "base d'un dossier complet au Directeur financier en date du {0}.<br/></p>"

FINANCE_ADVICE_LEGAL_TEXT = "<p>Attendu l'avis {0} du Directeur financier " \
                            "rendu en date du {1} conformément à l'article L1124-40 du Code de la " \
                            "démocratie locale et de la décentralisation,</p>"

FINANCE_ADVICE_LEGAL_TEXT_NOT_GIVEN = "<p>Attendu l'absence d'avis du " \
                                      "Directeur financier rendu dans le délai prescrit à l'article L1124-40 " \
                                      "du Code de la démocratie locale et de la décentralisation,</p>"

FINANCE_GROUP_ID = u'dirfin'

POLICE_GROUP_PREFIX = u'zone-de-police'

CC_ARRET_OJ_CAT_ID = 'conseil-communal-arret-de-lordre-du-jour'
COMMUNICATION_CAT_ID = 'communication'

CHARLEROI_ADVICE_STATES_ALIVE = ('advice_under_edit',
                                 'proposed_to_financial_controller',
                                 'proposed_to_financial_editor',
                                 'proposed_to_financial_reviewer',
                                 'proposed_to_financial_manager',
                                 'financial_advice_signed',)
PMconfig.ADVICE_STATES_ALIVE = CHARLEROI_ADVICE_STATES_ALIVE

# decision displayed for College item sent to Council
DECISION_ITEM_SENT_TO_COUNCIL = "<p>Ce point est à inscrire à l'ordre du jour du Conseil.</p>"

# comment used when a finance advice has been signed and so historized
FINANCE_ADVICE_HISTORIZE_COMMENTS = 'financial_advice_signed_historized_comments'

# copy/pasted from MeetingCommunes because importing from MeetingCommunes break
# the constant monkey patches...

# group suffixes
PMconfig.EXTRA_GROUP_SUFFIXES = [
    {'fct_title': u'serviceheads', 'fct_id': u'serviceheads', 'fct_orgs': [], "fct_management": False, 'enabled': True},
    {'fct_title': u'financialcontrollers', 'fct_id': u'financialcontrollers', 'fct_orgs': [FINANCE_GROUP_ID],
     "fct_management": False, 'enabled': True},
    {'fct_title': u'financialeditors', 'fct_id': u'financialeditors', 'fct_orgs': [FINANCE_GROUP_ID],
     "fct_management": False, 'enabled': True},
    {'fct_title': u'financialreviewers', 'fct_id': u'financialreviewers', 'fct_orgs': [FINANCE_GROUP_ID],
     "fct_management": False,
     'enabled': True},
    {'fct_title': u'financialmanagers', 'fct_id': u'financialmanagers', 'fct_orgs': [FINANCE_GROUP_ID],
     "fct_management": False, 'enabled': True},
]

# Council special categories, items added manually to Council and never considered 'late'
COUNCIL_SPECIAL_CATEGORIES = ['proposition-de-motion',
                              'proposes-par-un-conseiller',
                              'interventions',
                              'questions-actualite']

COUNCIL_DEFAULT_CATEGORY = 'indeterminee'
COUNCIL_DEFAULT_CLASSIFIER = 'non-publiable'

# items using these categories will always be inserted as normal items in the meeting
NEVER_LATE_CATEGORIES = {
    'meeting-config-college': ['communication'],
    'meeting-config-council': ['entetes'] + COUNCIL_SPECIAL_CATEGORIES, }

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
    ('taxes-et-redevances', '14. Taxes et redevances'),)

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
     u'I. Autres'),)

# import at the bottom so monkeypatches are done because PMconfig is imported in MCconfig
from Products.MeetingCommunes import config as MCconfig

# in those states, finance advice can still be given
MCconfig.FINANCE_WAITING_ADVICES_STATES = ('prevalidated_waiting_advices',)
