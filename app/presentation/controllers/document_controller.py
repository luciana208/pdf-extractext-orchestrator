from fastapi import UploadFile
from fastapi.responses import PlainTextResponse

from app.presentation.downloads import content_disposition, txt_filename
from app.presentation.dto.request.update_request import UpdateRequestDTO
from app.presentation.dto.request.upload_request import UploadRequestDTO
from app.presentation.dto.response.document_response import DocumentResponseDTO
from app.use_cases.document_queries import (
    DeleteDocumentUseCase,
    GetDocumentUseCase,
    ListDocumentsUseCase,
    RenameDocumentUseCase,
)
from app.use_cases.upload_document import UploadDocumentUseCase

DEFAULT_FILENAME = "documento.pdf"


class DocumentController:
    """traduce entre http (dtos) y los casos de uso; los errores los traduce error_handlers"""

    def __init__(
        self,
        upload: UploadDocumentUseCase,
        list_documents: ListDocumentsUseCase,
        get_document: GetDocumentUseCase,
        rename_document: RenameDocumentUseCase,
        delete_document: DeleteDocumentUseCase,
    ) -> None:
        self._upload = upload
        self._list_documents = list_documents
        self._get_document = get_document
        self._rename_document = rename_document
        self._delete_document = delete_document

    async def upload_document(self, file: UploadFile, dto: UploadRequestDTO) -> DocumentResponseDTO:
        file_bytes = await file.read()
        filename = dto.custom_name or file.filename or DEFAULT_FILENAME
        document = await self._upload.execute(file_bytes, filename)
        return DocumentResponseDTO.from_entity(document)

    async def get_all_documents(self, skip: int, limit: int) -> list[DocumentResponseDTO]:
        documents = await self._list_documents.execute(skip, limit)
        return [DocumentResponseDTO.from_entity(document) for document in documents]

    async def get_document_by_id(self, document_id: str) -> DocumentResponseDTO:
        return DocumentResponseDTO.from_entity(await self._get_document.execute(document_id))

    async def update_document(self, document_id: str, dto: UpdateRequestDTO) -> DocumentResponseDTO:
        return DocumentResponseDTO.from_entity(await self._rename_document.execute(document_id, dto.custom_name))

    async def delete_document(self, document_id: str) -> dict[str, str]:
        return {"message": await self._delete_document.execute(document_id)}

    async def download_document_text(self, document_id: str) -> PlainTextResponse:
        document = await self._get_document.execute(document_id)
        filename = txt_filename(document.filename or document_id)
        return PlainTextResponse(
            document.extracted_text,
            headers={"Content-Disposition": content_disposition(filename)},
        )
