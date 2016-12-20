# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from plone import api
from Products.MeetingCommunes.browser.overrides import MCItemDocumentGenerationHelperView
from Products.MeetingCommunes.browser.overrides import MCMeetingDocumentGenerationHelperView
from Products.PloneMeeting.browser.views import MeetingBeforeFacetedInfosView
from Products.PloneMeeting.utils import getLastEvent

FIN_ADVICE_LINE1 = "<p>Considérant la communication du dossier au Directeur financier faite en date du {0}, " \
                   "conformément à l'article L1124-40 §1er, 3° et 4° du " \
                   "Code de la Démocratie locale et de la Décentralisation ;</p>"
FIN_ADVICE_LINE2 = "<p>Considérant son avis {0} du {1} joint en annexe ;</p>"

FIN_ADVICE_ITEM = "<p><strong>Avis du Directeur financier :</strong></p><p>Type d'avis : {0}</p><p>Demandé le : {1}</p><p>Émis le : {2}</p>"


class MCHMeetingBeforeFacetedInfosView(MeetingBeforeFacetedInfosView):
    """ """


class MCHItemDocumentGenerationHelperView(MCItemDocumentGenerationHelperView):
    """Specific printing methods used for item."""

    def _showFinancesAdvice(self):
        """Finances advice is only shown :
           - if given (at worst it will be 'not_given_finance');
           - if item is 'validated' to everybody;
           - if it is 'prevalidated_waiting_advices', to finances advisers."""
        financeAdviceId = self.context.adapted().getFinanceAdviceId()
        if not financeAdviceId:
            return False
        adviceObj = self.context.getAdviceObj(financeAdviceId)
        if not adviceObj:
            return False
        item_state = self.context.queryState()
        tool = api.portal.get_tool('portal_plonemeeting')
        financeAdviceGroup = getattr(tool, financeAdviceId)
        if item_state == 'validated' or \
                self.context.hasMeeting() or \
                (item_state == 'prevalidated_waiting_advices' and financeAdviceGroup.userPloneGroups(
                    suffixes=['advisers'])):
            return True

    def _financeAdviceData(self):
        """ """
        adviceData = self.context.getAdviceDataFor(self.context.context, self.context.adapted().getFinanceAdviceId())
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

    def printDelibeContentForCollege(self):
        """Printed on a College item, get the whole body of the delibe in one shot."""
        body = self.context.getMotivation() and self.context.getMotivation() + '<p></p>' or ''
        finAdvice = self.printFinancesAdvice()
        if finAdvice:
            body += finAdvice + '<p></p>'
        body += "<p><strong>Décide:</strong> <br/></p>"
        body += self.context.getDecision() + '<p></p>'
        if self.context.getSendToAuthority():
            body += "<p>Conformément aux prescrits des articles L3111-1 et suivants " \
                    "du Code de la démocratie locale et de la décentralisation relatifs " \
                    "à la Tutelle, la présente décision et ses pièces justificatives sont " \
                    "transmises aux Autorités de Tutelle.</p>"
        return body

    def printDelibeContentForCouncil(self):
        """Printed on a Council item, get the whole body of the delibe in one shot."""
        body = self.context.getMotivation() and self.context.getMotivation() + '<p></p>' or ''
        finAdvice = self.printFinancesAdvice()
        if finAdvice:
            body += finAdvice + '<p></p>'
        # body += self.printCollegeProposalInfos().encode("utf-8")
        body += self.context.getDecision() + '<p></p>'
        if self.context.getSendToAuthority():
            body += "<p>Conformément aux prescrits des articles L3111-1 et suivants " \
                    "du Code de la démocratie locale et de la décentralisation relatifs " \
                    "à la Tutelle, la présente décision et ses pièces justificatives sont " \
                    "transmises aux Autorités de Tutelle.<br/></p>"
        body += self.context.getObservations() and self.context.getObservations() or ''
        return body

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
            return {'author': mTool.getMemberById(str(lastEvent['actor'])).getProperty('fullname'),
                    'date': lastEvent['time'].strftime('%d/%m/%Y %H:%M')}
        return ''

    def printHistoryForFinancesAdvice(self, advice):
        printable_history = []
        if advice and advice.getHistory():
            m_tool = api.portal.get_tool('portal_membership')
            for changeHistory in advice.getHistory():
                printable_history_item = {'author': m_tool.getMemberById(changeHistory['actor']).getProperty('fullname'),
                                          'date': changeHistory['time'].strftime('%d/%m/%Y %H:%M'),
                                          'review_state_translated': self.translate(changeHistory['review_state'])}

                if changeHistory['comments'] == 'wf_transition_triggered_by_application':
                    printable_history_item['comments'] = self.translate(changeHistory['comments'])
                else:
                    printable_history_item['comments'] = changeHistory['comments']

                printable_history.append(printable_history_item)

        return printable_history


class MCHMeetingDocumentGenerationHelperView(MCMeetingDocumentGenerationHelperView):
    """Specific printing methods used for meeting."""

    def printItemDelibeContentForCollege(self, item):
        """
        """
        view = item.restrictedTraverse("@@document-generation")
        helper = view.get_generation_context_helper()
        return helper.printDelibeContentForCollege()

    def printItemDelibeContentForCouncil(self, item):
        """
        """
        view = item.restrictedTraverse("@@document-generation")
        helper = view.get_generation_context_helper()
        return helper.printDelibeContentForCouncil()

    def printItemContentForCollegePV(self, item):
        """
        """
        view = item.restrictedTraverse("@@document-generation")
        helper = view.get_generation_context_helper()
        return helper.printDelibeContentForCollege()

    def printItemPresentation(self, item):
        """
        """
        body = item.Description() and item.Description() + '<p></p>' or ''
        # insert finances advice
        view = item.restrictedTraverse("@@document-generation")
        helper = view.get_generation_context_helper()
        finAdvice = ''
        if helper._showFinancesAdvice():
            adviceData = helper._financeAdviceData()
            adviceTypeTranslated = adviceData['advice_type_translated']
            delayStartedOnLocalized = adviceData['delay_infos']['delay_started_on_localized']
            adviceGivenOnLocalized = adviceData['advice_given_on_localized']
            finAdvice = FIN_ADVICE_ITEM.format(adviceTypeTranslated,
                                               delayStartedOnLocalized,
                                               adviceGivenOnLocalized)
        if finAdvice:
            body += finAdvice + '<p></p>'
        return body
