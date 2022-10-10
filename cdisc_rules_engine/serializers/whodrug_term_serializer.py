from abc import ABC

from cdisc_rules_engine.models.dictionaries.whodrug import (
    AtcText,
    WhodrugRecordTypes,
    AtcClassification,
    DrugDictionary,
)
from cdisc_rules_engine.models.dictionaries.whodrug.base_whodrug_term import (
    BaseWhoDrugTerm,
)
from cdisc_rules_engine.serializers import BaseSerializer


class BaseWhoDrugTermSerializer(BaseSerializer, ABC):
    def __init__(self, term: BaseWhoDrugTerm):
        self.__term = term

    @property
    def data(self) -> dict:
        return {"code": self.__term.code, "type": self.__term.type}


class AtcTextSerializer(BaseWhoDrugTermSerializer):
    def __init__(self, term: AtcText):
        self.__term = term
        super(AtcTextSerializer, self).__init__(term)

    @property
    def data(self) -> dict:
        return {
            **super(AtcTextSerializer, self).data,
            "parentCode": self.__term.parentCode,
            "level": self.__term.level,
            "text": self.__term.text,
        }

    @property
    def is_valid(self) -> bool:
        return (
            isinstance(self.__term.parentCode, str)
            and len(self.__term.parentCode) <= 7
            and isinstance(self.__term.level, int)
            and self.__term.level in range(1, 5)
            and len(str(self.__term.level)) == 1
            and isinstance(self.__term.text, str)
            and len(self.__term.text) <= 110
            and self.__term.type == WhodrugRecordTypes.ATC_TEXT.value
        )


class AtcClassificationSerializer(BaseWhoDrugTermSerializer):
    def __init__(self, term: AtcClassification):
        self.__term = term
        super().__init__(term)

    @property
    def data(self) -> dict:
        return {
            **super(AtcClassificationSerializer, self).data,
            "parentCode": self.__term.parentCode,
        }

    @property
    def is_valid(self) -> bool:
        return (
            isinstance(self.__term.parentCode, str)
            and len(self.__term.parentCode) <= 6
            and isinstance(self.__term.code, str)
            and len(self.__term.code) <= 7
            and self.__term.type == WhodrugRecordTypes.ATC_CLASSIFICATION.value
        )


class DrugDictionarySerializer(BaseWhoDrugTermSerializer):
    def __init__(self, term: DrugDictionary):
        self.__term = term
        super().__init__(term)

    @property
    def data(self) -> dict:
        return {
            **super(DrugDictionarySerializer, self).data,
            "drugName": self.__term.drugName,
        }

    @property
    def is_valid(self) -> bool:
        return (
            isinstance(self.__term.code, str)
            and len(self.__term.code) <= 6
            and isinstance(self.__term.drugName, str)
            and len(self.__term.drugName) <= 1500
            and self.__term.type == WhodrugRecordTypes.DRUG_DICT.value
        )
