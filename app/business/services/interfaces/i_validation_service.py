from abc import ABC, abstractmethod

from app.business.entities.document import ValidatedPDF


class IValidationService(ABC):
    @abstractmethod
    async def validate(self, file_bytes: bytes) -> ValidatedPDF:
        """valida el pdf; lanza InvalidPDFError o PDFTooLargeError"""
