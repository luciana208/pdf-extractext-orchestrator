"""composicion: unico lugar que elige las implementaciones concretas"""

from fastapi import Request

from app.data.clients.documents_client import DocumentsClient
from app.data.clients.extraction_client import ExtractionClient
from app.data.clients.validation_client import ValidationClient
from app.presentation.controllers.document_controller import DocumentController
from app.use_cases.document_queries import (
    DeleteDocumentUseCase,
    GetDocumentUseCase,
    ListDocumentsUseCase,
    RenameDocumentUseCase,
)
from app.use_cases.upload_document import UploadDocumentUseCase


def get_document_controller(request: Request) -> DocumentController:
    # los clientes http se crean una vez en el lifespan y se reusan (pool de conexiones)
    clients = request.app.state.http_clients
    documents = DocumentsClient("pdf-extractext", clients.documents)
    return DocumentController(
        upload=UploadDocumentUseCase(
            ValidationClient("pdf-validation-service", clients.validation),
            ExtractionClient("pdf-extract-service", clients.extraction),
            documents,
        ),
        list_documents=ListDocumentsUseCase(documents),
        get_document=GetDocumentUseCase(documents),
        rename_document=RenameDocumentUseCase(documents),
        delete_document=DeleteDocumentUseCase(documents),
    )
