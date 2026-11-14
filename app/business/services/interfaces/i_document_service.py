from abc import ABC, abstractmethod

from app.business.entities.document import Document, Reservation


class IDocumentService(ABC):
    """puerto hacia el servicio de persistencia; el repositorio del orquestador es un cliente http"""

    @abstractmethod
    async def reserve(self, saga_id: str, checksum: str, filename: str) -> Reservation:
        """aparta el checksum; lanza DuplicateDocumentError si ya existe"""

    @abstractmethod
    async def confirm(self, reservation_id: str, saga_id: str, extracted_text: str) -> Document:
        """completa la reserva con el texto"""

    @abstractmethod
    async def release(self, reservation_id: str, saga_id: str) -> None:
        """compensacion: libera la reserva (idempotente)"""

    @abstractmethod
    async def list(self, skip: int, limit: int) -> list[Document]: ...

    @abstractmethod
    async def get(self, document_id: str) -> Document: ...

    @abstractmethod
    async def rename(self, document_id: str, custom_name: str | None) -> Document: ...

    @abstractmethod
    async def delete(self, document_id: str) -> str: ...
