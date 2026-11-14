"""api publica de documentos (/api/v1/documents), la misma que tenia el monolito"""

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status

from app.config.settings import settings
from app.dependencies import get_document_controller
from app.presentation.controllers.document_controller import DocumentController
from app.presentation.dto.request.update_request import UpdateRequestDTO
from app.presentation.dto.request.upload_request import UploadRequestDTO
from app.presentation.dto.response.document_response import DocumentResponseDTO

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post(
    "/",
    response_model=DocumentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Subir un documento PDF",
)
async def upload_document(
    file: UploadFile = File(..., description="Archivo PDF a subir."),
    custom_name: str | None = Form(default=None, description="Nombre opcional."),
    controller: DocumentController = Depends(get_document_controller),
) -> DocumentResponseDTO:
    """
    corre la saga de subida: validacion, reserva del checksum, extraccion y confirmacion.
    errores: 400 pdf invalido, 409 duplicado, 413 muy grande, 503/504 servicio interno caido o lento.
    """
    dto = UploadRequestDTO(custom_name=custom_name)
    return await controller.upload_document(file, dto)


@router.get(
    "/",
    response_model=list[DocumentResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Listar documentos (paginado)",
)
async def get_all_documents(
    skip: int = Query(0, ge=0, description="Documentos a saltar."),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size, description="Documentos por pagina."),
    controller: DocumentController = Depends(get_document_controller),
) -> list[DocumentResponseDTO]:
    return await controller.get_all_documents(skip=skip, limit=limit)


@router.get(
    "/{document_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Descargar el texto extraido como .txt",
)
async def download_document_text(
    document_id: str,
    controller: DocumentController = Depends(get_document_controller),
) -> Response:
    return await controller.download_document_text(document_id)


@router.get(
    "/{document_id}",
    response_model=DocumentResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Obtener un documento por ID",
)
async def get_document_by_id(
    document_id: str,
    controller: DocumentController = Depends(get_document_controller),
) -> DocumentResponseDTO:
    return await controller.get_document_by_id(document_id)


@router.put(
    "/{document_id}",
    response_model=DocumentResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Actualizar el nombre de un documento",
)
async def update_document(
    document_id: str,
    dto: UpdateRequestDTO,
    controller: DocumentController = Depends(get_document_controller),
) -> DocumentResponseDTO:
    return await controller.update_document(document_id, dto)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un documento",
)
async def delete_document(
    document_id: str,
    controller: DocumentController = Depends(get_document_controller),
) -> dict[str, str]:
    return await controller.delete_document(document_id)
