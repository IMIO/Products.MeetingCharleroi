# encoding: utf-8

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.MeetingCharleroi.config import ADVICE_CATEGORIES
from Products.MeetingCharleroi.config import ADVICE_MOTIVATION_CATEGORIES


class AdviceCategoriesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """ """
        res = []
        for category_id, category_title in ADVICE_CATEGORIES:
            res.append(SimpleTerm(category_id,
                                  category_id,
                                  category_title))
        return SimpleVocabulary(res)

AdviceCategoriesVocabularyFactory = AdviceCategoriesVocabulary()


class AdviceMotivationCategoriesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """ """
        res = []
        for category_id, category_title in ADVICE_MOTIVATION_CATEGORIES:
            res.append(SimpleTerm(category_id,
                                  category_id,
                                  category_title))
        return SimpleVocabulary(res)

AdviceMotivationCategoriesVocabularyFactory = AdviceMotivationCategoriesVocabulary()
