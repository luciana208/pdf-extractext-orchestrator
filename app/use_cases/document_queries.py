"""casos de uso del crud: delegan en el servicio de persistencia"""

from app.business.entities.document import Document
from app.business.services.interfaces.i_document_service import IDocumentService


class ListDocumentsUseCase:
    def __init__(self, documents: IDocumentService) -> None:
        self._documents = documents

    async def execute(self, skip: int, limit: int) -> list[Document]:
        return await self._documents.list(skip, limit)


class GetDocumentUseCase:
    def __init__(self, documents: IDocumentService) -> None:
        self._documents = documents

    async def execute(self, document_id: str) -> Document:
        return await self._documents.get(document_id)


class RenameDocumentUseCase:
    def __init__(self, documents: IDocumentService) -> None:
        self._documents = documents

    async def execute(self, document_id: str, custom_name: str | None) -> Document:
        return await self._documents.rename(document_id, custom_name)


class DeleteDocumentUseCase:
    def __init__(self, documents: IDocumentService) -> None:
        self._documents = documents

    async def execute(self, document_id: str) -> str:
        return await self._documents.delete(document_id)
