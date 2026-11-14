from abc import ABC, abstractmethod


class IExtractionService(ABC):
    @abstractmethod
    async def extract_text(self, file_bytes: bytes) -> str:
        """devuelve el texto plano del pdf (la etapa 1 pide solo el texto)"""
