"""dobles de los servicios internos que registran el orden de las llamadas"""

from datetime import datetime, timezone

from app.business.entities.document import Document, Reservation, ValidatedPDF
from app.business.services.interfaces.i_document_service import IDocumentService
from app.business.services.interfaces.i_extraction_service import IExtractionService
from app.business.services.interfaces.i_validation_service import IValidationService

NOW = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
CHECKSUM = "e" * 64


class FakeValidation(IValidationService):
    def __init__(self, calls: list, error: Exception | None = None) -> None:
        self.calls = calls
        self.error = error

    async def validate(self, file_bytes: bytes) -> ValidatedPDF:
        self.calls.append("validate")
        if self.error:
            raise self.error
        return ValidatedPDF(checksum=CHECKSUM, size_bytes=len(file_bytes), page_count=1)


class FakeExtraction(IExtractionService):
    def __init__(self, calls: list, error: Exception | None = None) -> None:
        self.calls = calls
        self.error = error

    async def extract_text(self, file_bytes: bytes) -> str:
        self.calls.append("extract")
        if self.error:
            raise self.error
        return "texto extraido"


class FakeDocuments(IDocumentService):
    def __init__(self, calls: list, reserve_error: Exception | None = None, confirm_error: Exception | None = None) -> None:
        self.calls = calls
        self.reserve_error = reserve_error
        self.confirm_error = confirm_error
        self.saga_ids: list[str] = []

    async def reserve(self, saga_id: str, checksum: str, filename: str) -> Reservation:
        self.calls.append("reserve")
        self.saga_ids.append(saga_id)
        if self.reserve_error:
            raise self.reserve_error
        return Reservation(id="r1", expires_at=NOW)

    async def confirm(self, reservation_id: str, saga_id: str, extracted_text: str) -> Document:
        self.calls.append("confirm")
        self.saga_ids.append(saga_id)
        if self.confirm_error:
            raise self.confirm_error
        return Document(reservation_id, "a.pdf", CHECKSUM, extracted_text, NOW, NOW)

    async def release(self, reservation_id: str, saga_id: str) -> None:
        self.calls.append("release")
        self.saga_ids.append(saga_id)

    async def list(self, skip: int, limit: int) -> list[Document]:
        return []

    async def get(self, document_id: str) -> Document:
        return Document(document_id, "a.pdf", CHECKSUM, "", NOW, NOW)

    async def rename(self, document_id: str, custom_name: str | None) -> Document:
        return Document(document_id, custom_name or "a.pdf", CHECKSUM, "", NOW, NOW)

    async def delete(self, document_id: str) -> str:
        return "eliminado"
