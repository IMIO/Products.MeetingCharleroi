# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from Products.PloneMeeting.browser.views import ItemDocumentGenerationHelperView
from Products.PloneMeeting.browser.views import FolderDocumentGenerationHelperView


class MCHItemDocumentGenerationHelperView(ItemDocumentGenerationHelperView):
    """Specific printing methods used for item."""

    def printDelibeContentForCollege(self):
        """Printed on a College item, get the whole body of the delibe in one shot."""
        body = self.context.getMotivation() and self.context.getMotivation() + '<p></p>' or ''
        if self.context.adapted().getLegalTextForFDAdvice():
            body += self.context.adapted().getLegalTextForFDAdvice() + '<p></p>'
        body += "<p><strong>Décide:</strong> <br/></p>"
        body += self.context.getDecision() + '<p></p>'
        if self.context.getSendToAuthority():
            body += "<p>Conformément aux prescrits des articles L3111-1 et suivants " \
                    "du Code de la démocratie locale et de la décentralisation relatifs "\
                    "à la Tutelle, la présente décision et ses pièces justificatives sont "\
                    "transmises aux Autorités de Tutelle.</p>"
        return body

    def printDelibeContentForCouncil(self):
        """Printed on a Council item, get the whole body of the delibe in one shot."""
        body = self.context.getMotivation() and self.context.getMotivation() + '<p></p>' or ''
        if self.context.adapted().getLegalTextForFDAdvice():
            body += self.context.adapted().getLegalTextForFDAdvice() + '<p></p>'
        #body += self.printCollegeProposalInfos().encode("utf-8")
        body += self.context.getDecision() + '<p></p>'
        if self.context.getSendToAuthority():
            body += "<p>Conformément aux prescrits des articles L3111-1 et suivants " \
                    "du Code de la démocratie locale et de la décentralisation relatifs "\
                    "à la Tutelle, la présente décision et ses pièces justificatives sont "\
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


class MCHMeetingDocumentGenerationHelperView(FolderDocumentGenerationHelperView):
    """Specific printing methods used for meeting."""

    def printItemDelibeContentForCollege(self, item):
        """
        Printed on a College Item in a College Meeting, get the whole body
        of the delibe in one shot.
        """
        view = item.restrictedTraverse("@@document-generation")
        helper = view.get_generation_context_helper()
        return helper.printDelibeContentForCollege()

    def printItemDelibeContentForCouncil(self, item):
        """
        Printed on a Council Item in a Council Meeting, get the whole body
        of the delibe in one shot.
        """
        view = item.restrictedTraverse("@@document-generation")
        helper = view.get_generation_context_helper()
        return helper.printDelibeContentForCouncil()
