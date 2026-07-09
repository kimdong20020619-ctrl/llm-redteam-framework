import logging
from abc import ABC, abstractmethod

import yaml

from redteam.models import Payload

logger = logging.getLogger(__name__)


class PayloadSource(ABC):
    @abstractmethod
    def load(self) -> list[Payload]:
        ...


class YamlPayloadSource(PayloadSource):
    def __init__(self, path: str):
        self.path = path

    def load(self) -> list[Payload]:
        with open(self.path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        payloads = []
        for category, texts in data.items():
            if not isinstance(texts, list):
                logger.warning(
                    "카테고리 '%s'의 페이로드 형식이 리스트가 아니라 건너뜁니다: %r", category, texts
                )
                continue
            for text in texts:
                payloads.append(Payload(category=category, text=text))
        return payloads
