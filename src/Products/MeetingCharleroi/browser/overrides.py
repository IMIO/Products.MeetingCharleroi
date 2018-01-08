# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2017 by Imio.be
#
# GNU General Public License (GPL)
#

from plone import api
from Products.MeetingCommunes.browser.overrides import MCItemDocumentGenerationHelperView
from Products.MeetingCommunes.browser.overrides import MCMeetingDocumentGenerationHelperView
from Products.MeetingCharleroi.config import FINANCE_GROUP_ID
from Products.PloneMeeting.browser.views import MeetingBeforeFacetedInfosView
from Products.PloneMeeting.utils import getLastEvent
from Products.MeetingCharleroi.config import POLICE_GROUP_PREFIX


FIN_ADVICE_LINE1 = "<p>Considérant la communication du dossier au Directeur financier faite en date du {0}, " \
                   "conformément à l'article L1124-40 §1er, 3° et 4° du " \
                   "Code de la Démocratie locale et de la Décentralisation ;</p>"
FIN_ADVICE_LINE2 = "<p>Considérant son avis {0} du {1} joint en annexe ;</p>"

FIN_ADVICE_ITEM = "<p><strong>Avis du Directeur financier :</strong></p><p>Type d'avis : {0}</p>" \
                  "<p>Demandé le : {1}</p><p>Émis le : {2}</p>"

POLL_TYPE_ITEM = u"<p><strong>Mode de scrutin :</strong> {0}</p>"

COMMISSION_TYPE_ITEM = "<p><strong>Commission :</strong> {0}</p>"


class MCHMeetingBeforeFacetedInfosView(MeetingBeforeFacetedInfosView):
    """ """


class MCBaseDocumentGenerationHelperView(object):
    def getPoliceGroups(self):
        tool = api.portal.get_tool('portal_plonemeeting')
        groups = tool.getMeetingGroups()
        res = []
        for group in groups:
            if group.getId().startswith(POLICE_GROUP_PREFIX):
                res.append(group.getId())

        return res


class MCHItemDocumentGenerationHelperView(MCBaseDocumentGenerationHelperView, MCItemDocumentGenerationHelperView):
    """Specific printing methods used for item."""

    def _showFinancesAdvice(self):
        """Finances advice is only shown :
           - if given (at worst it will be 'not_given_finance');
           - if advice_type is not not_required_finance;
           - in any case if item is in Council;
           - if item is 'validated' to everybody;
           - if it is 'prevalidated_waiting_advices', to finances advisers."""
        adviceHolder = self._advice_holder()
        adviceObj = adviceHolder.getAdviceObj(FINANCE_GROUP_ID)
        if not adviceObj or adviceObj.advice_type == 'not_required_finance':
            return False
        item_state = self.context.queryState()
        tool = api.portal.get_tool('portal_plonemeeting')
        financeAdviceGroup = getattr(tool, FINANCE_GROUP_ID)
        if item_state == 'validated' or \
                adviceHolder.hasMeeting() or \
                (item_state == 'prevalidated_waiting_advices' and financeAdviceGroup.userPloneGroups(
                    suffixes=['advisers'])):
            return True

    def _advice_holder(self):
        adviceInfo = self.real_context.getAdviceDataFor(self.real_context, FINANCE_GROUP_ID)
        return adviceInfo.get('adviceHolder', self.real_context)

    def _financeAdviceData(self):
        """ """
        # if item is in Council, get the adviceData from it's predecessor
        adviceData = self.real_context.getAdviceDataFor(self.real_context, FINANCE_GROUP_ID)
        adviceTypeTranslated = ''
        if adviceData['type'] in ('positive_finance', 'positive_with_remarks_finance'):
            adviceTypeTranslated = 'favorable'
        elif adviceData['type'] == 'negative_finance':
            adviceTypeTranslated = 'défavorable'
        elif adviceData['type'] == 'cautious_finance':
            adviceTypeTranslated = 'réservé'
        elif adviceData['type'] == 'not_given_finance':
            adviceTypeTranslated = 'non remis'
        adviceData['advice_type_translated'] = adviceTypeTranslated

        for dealayChange in adviceData['delay_changes_history']:
            """Get the new value of the latest delay change into history. """
            newDelay = int(dealayChange['action'][1])
            oldDelay = int(dealayChange['action'][0])
            dealayChange['delayDiff'] = str(newDelay - oldDelay)

        adviceData['printableHistory'] = self.printHistoryForFinancesAdvice(adviceData['given_advice'])

        return adviceData

    def printFinancesAdvice(self):
        """Print the legal text regarding Finances advice."""
        if not self._showFinancesAdvice():
            return ''
        adviceData = self._financeAdviceData()
        delayStartedOnLocalized = adviceData['delay_infos']['delay_started_on_localized']
        adviceGivenOnLocalized = adviceData['advice_given_on_localized']
        adviceTypeTranslated = adviceData['advice_type_translated']
        return FIN_ADVICE_LINE1.format(delayStartedOnLocalized) + \
            FIN_ADVICE_LINE2.format(adviceTypeTranslated, adviceGivenOnLocalized)

    def print_motivation(self):
        body = self.context.getMotivation() and (self.context.getMotivation() + '<p></p>') or ''

        finAdvice = self.printFinancesAdvice()
        if finAdvice:
            body += finAdvice + '<p></p>'

        return body

    def print_autority(self):
        if self.context.getSendToAuthority():
            return "<p>Conformément aux prescrits des articles L3111-1 et suivants " \
                "du Code de la démocratie locale et de la décentralisation relatifs " \
                "à la Tutelle, la présente décision et ses pièces justificatives sont " \
                "transmises aux Autorités de Tutelle.</p>"
        else:
            return ''

    def print_decision(self):
        body = ''
        if self.context.getDecision():
            body += "<p><strong>Décide:</strong></p><p></p>"
            body += self.context.getDecision() + '<p></p>'
        return body

    def print_observation_and_poll(self):
        if self.context.getObservations():
            return self.context.getObservations() + '<p></p>'
        else:
            return ''

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
        lastEvent = getLastEvent(self.context, transition=transition)
        if lastEvent:
            mTool = api.portal.get_tool('portal_membership')
            author_id = str(lastEvent['actor'])
            author = mTool.getMemberById(author_id)
            return {'author': author and author.getProperty('fullname') or author_id,
                    'date': lastEvent['time'].strftime('%d/%m/%Y %H:%M')}
        return ''

    def printHistoryForFinancesAdvice(self, advice):
        printable_history = []
        if advice and advice.getHistory():
            m_tool = api.portal.get_tool('portal_membership')
            for changeHistory in advice.getHistory():
                author_id = changeHistory['actor']
                author = m_tool.getMemberById(author_id)
                printable_history_item = {
                    'author': author and author.getProperty('fullname') or author_id,
                    'date': changeHistory['time'].strftime('%d/%m/%Y %H:%M'),
                    'review_state_translated': self.translate(changeHistory['review_state'])}

                if changeHistory['comments'] == 'wf_transition_triggered_by_application':
                    printable_history_item['comments'] = self.translate(changeHistory['comments'])
                else:
                    printable_history_item['comments'] = changeHistory['comments']

                printable_history.append(printable_history_item)

        return printable_history


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
        body = item.Description() and item.Description() + '<p></p>' or ''
        # insert finances advice

        fin_advice = self.format_finance_advice(item)
        if fin_advice:
            body += fin_advice + '<p></p>'
        return body

    def format_finance_advice(self, item):
        helper = self.getDGHV(item)
        if helper._showFinancesAdvice():
            advice_data = helper._financeAdviceData()
            advice_type_translated = advice_data['advice_type_translated']
            delay_started_on_localized = advice_data['delay_infos']['delay_started_on_localized']
            advice_given_on_localized = advice_data['advice_given_on_localized']
            return FIN_ADVICE_ITEM.format(advice_type_translated, delay_started_on_localized, advice_given_on_localized)

        return None

    def format_poll_type(self, item):
        if item.getPollType():
            return POLL_TYPE_ITEM.format(self.translate('polltype_' + item.getPollType(), domain='PloneMeeting'))
        return None

    def format_commission(self, item):
        group_in_charge = item.getGroupInCharge(theObject=True)
        group_descr = group_in_charge and group_in_charge.Description() or ''
        return COMMISSION_TYPE_ITEM.format(group_descr)
