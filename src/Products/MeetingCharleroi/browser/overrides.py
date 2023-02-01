# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2017 by Imio.be
#
# GNU General Public License (GPL)
#

from Products.CMFPlone.utils import safe_unicode
from Products.MeetingCharleroi.config import POLICE_GROUP_PREFIX
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.MeetingCommunes.browser.overrides import MCItemDocumentGenerationHelperView, \
    MCMeetingDocumentGenerationHelperView
from collective.contact.plonegroup.utils import get_organizations
from imio.history.utils import getLastWFAction
from plone import api

FIN_ADVICE_LINE1 = u"<p>Considérant la communication du dossier au Directeur financier faite en date du {0}, " \
                   u"conformément à l'article L1124-40 §1er, 3° et 4° du " \
                   u"Code de la Démocratie locale et de la Décentralisation ;</p>"
FIN_ADVICE_LINE2 = u"<p>Considérant son avis {0} du {1} joint en annexe ;</p>"

FIN_ADVICE_ITEM = u"<p><strong>Avis du Directeur financier :</strong></p><p>Type d'avis : {0}</p>" \
                  u"<p>Demandé le : {1}</p><p>Émis le : {2}</p>"

POLL_TYPE_ITEM = u"<p><strong>Mode de scrutin :</strong> {0}</p>"

COMMISSION_TYPE_ITEM = "<p><strong>Commission :</strong> {0}</p>"


class MCBaseDocumentGenerationHelperView(object):
    def getPoliceGroups(self):
        orgs = get_organizations()
        res = []
        for org in orgs:
            if org.getId().startswith(POLICE_GROUP_PREFIX):
                res.append(org.getId())

        return res


class MCHItemDocumentGenerationHelperView(MCBaseDocumentGenerationHelperView, MCItemDocumentGenerationHelperView):
    """Specific printing methods used for item."""

    def showFinancesAdvice(self, advice_data=None):
        """Finances advice is only shown :
           - if given (at worst it will be 'not_given_finance');
           - if advice_type is not not_required_finance;
           - in any case if item is in Council;
           - if item is 'validated' to everybody;
           - if it is 'prevalidated_waiting_advices', to finances advisers."""
        adviceHolder = self._advice_holder(advice_data)
        adviceObj = adviceHolder.getAdviceObj(finance_group_uid())
        # check advice state
        if not adviceObj or adviceObj.advice_type == 'not_required_finance':
            return False
        # check item state
        item_state = self.real_context.query_state()
        if item_state == 'validated' or adviceHolder.hasMeeting():
            return True
        # check user access (administrators and advisers from finance director service)
        tool = api.portal.get_tool('portal_plonemeeting')
        if tool.isManager(realManagers=True) \
                or (item_state == 'prevalidated_waiting_advices' and
                    tool.get_orgs_for_user(suffixes=['advisers'],
                                           using_groups=[finance_group_uid()],
                                           the_objects=False)):
            return True
        return False

    def _advice_holder(self, advice_data=None):
        if not advice_data:
            advice_data = self.real_context.getAdviceDataFor(self.real_context, finance_group_uid())
        return advice_data.get('adviceHolder', self.real_context)

    def _financeAdviceData(self, advice_data=None):
        """ """
        # if item is in Council, get the adviceData from it's predecessor
        if not advice_data:
            advice_data = self.real_context.getAdviceDataFor(self.real_context, finance_group_uid())

        adviceTypeTranslated = advice_data['type_translated'].replace('Avis finances ', '')
        advice_data['advice_type_translated'] = adviceTypeTranslated

        return advice_data

    def printFinancesAdvice(self):
        """Print the legal text regarding Finances advice."""
        advice_data = self.real_context.getAdviceDataFor(self.real_context, finance_group_uid())
        if not self.showFinancesAdvice(advice_data=advice_data):
            return ''
        adviceData = self._financeAdviceData(advice_data=advice_data)
        delayStartedOnLocalized = adviceData['delay_infos']['delay_started_on_localized']
        adviceGivenOnLocalized = adviceData['advice_given_on_localized']
        adviceTypeTranslated = safe_unicode(adviceData['advice_type_translated'])
        return FIN_ADVICE_LINE1.format(delayStartedOnLocalized) + \
            FIN_ADVICE_LINE2.format(adviceTypeTranslated, adviceGivenOnLocalized)

    def print_motivation(self):
        body = self.context.getMotivation() and (safe_unicode(self.context.getMotivation()) + u'<p></p>') or ''

        finAdvice = self.printFinancesAdvice()
        if finAdvice:
            body += finAdvice + u'<p></p>'

        return body

    def print_autority(self):
        if self.context.getSendToAuthority():
            return u"<p>Conformément aux prescrits des articles L3111-1 et suivants " \
                u"du Code de la démocratie locale et de la décentralisation relatifs " \
                u"à la Tutelle, la présente décision et ses pièces justificatives sont " \
                u"transmises aux Autorités de Tutelle.</p>"
        else:
            return u''

    def print_decision(self):
        body = u''
        if self.context.getDecision():
            body += u"<p><strong>Décide:</strong></p><p></p>"
            body += safe_unicode(self.context.getDecision()) + u'<p></p>'
        return body

    def print_observation_and_poll(self):
        if self.context.getObservations():
            return safe_unicode(self.context.getObservations()) + u'<p></p>'
        else:
            return u''

    def printDelibeContent(self):
        """Printed on a College item, get the whole body of the delibe in one shot."""
        return self.print_motivation() + \
            self.print_decision() + \
            self.print_autority()

    def printDelibeContentCouncil(self):
        """Printed on a Council item, get the whole body of the delibe in one shot."""
        return self.print_motivation() + \
            self.print_observation_and_poll() + \
            self.print_decision() + \
            self.print_autority()

    def printFormatedItemType(self):
        """print type of item : NORMATIF - CONSEIL - COMMUNICATION - ENVOI TUTELLE"""
        item = self.context
        body = '<p style="text-align: center;">'
        if item.getOtherMeetingConfigsClonableTo():
            body += '<s>NORMATIF</s> - CONSEIL'
        else:
            body += 'NORMATIF - <s>CONSEIL</s>'
        if item.getCategory() == 'communication':
            body += ' - COMMUNICATION'
        else:
            body += ' - <s>COMMUNICATION</s>'
        if item.getSendToAuthority():
            body += ' - ENVOI TUTELLE'
        else:
            body += ' - <s>ENVOI TUTELLE</s>'
        body += '</p>'
        return body

    def printLastEventFor(self, transition):
        """print user who have the last action for this item"""
        lastEvent = getLastWFAction(self.context, transition=transition)
        if lastEvent:
            mTool = api.portal.get_tool('portal_membership')
            author_id = str(lastEvent['actor'])
            author = mTool.getMemberById(author_id)
            return {'author': author and author.getProperty('fullname') or author_id,
                    'date': lastEvent['time'].strftime('%d/%m/%Y %H:%M')}
        return ''


class MCHMeetingDocumentGenerationHelperView(MCBaseDocumentGenerationHelperView, MCMeetingDocumentGenerationHelperView):
    """Specific printing methods used for meeting."""

    def printItemDelibeContent(self, item):
        """
        """
        view = item.restrictedTraverse("@@document-generation")
        helper = view.get_generation_context_helper()
        return helper.printDelibeContent()

    def printItemDelibeContentForCouncil(self, item):
        """
        """
        view = item.restrictedTraverse("@@document-generation")
        helper = view.get_generation_context_helper()
        return helper.printDelibeContentCouncil()

    def printItemPresentation(self, item):
        """
        """
        body = item.Description() and safe_unicode(item.Description()) + u'<p></p>' or u''
        # insert finances advice

        fin_advice = self.format_finance_advice(item)
        if fin_advice:
            body += fin_advice + u'<p></p>'
        return body

    def format_finance_advice(self, item):
        helper = self.getDGHV(item)
        if helper.showFinancesAdvice():
            advice_data = helper._financeAdviceData()
            advice_type_translated = safe_unicode(advice_data['advice_type_translated'])
            delay_started_on_localized = advice_data['delay_infos']['delay_started_on_localized']
            advice_given_on_localized = advice_data['advice_given_on_localized']
            return FIN_ADVICE_ITEM.format(advice_type_translated, delay_started_on_localized, advice_given_on_localized)

        return None

    def format_poll_type(self, item):
        if item.getPollType():
            return POLL_TYPE_ITEM.format(self.translate('polltype_' + item.getPollType(), domain='PloneMeeting'))
        return None

    def format_commission(self, item):
        group_in_charge = item.getGroupsInCharge(theObjects=True, first=True)
        group_descr = group_in_charge and group_in_charge.Description() or ''
        return COMMISSION_TYPE_ITEM.format(group_descr)
