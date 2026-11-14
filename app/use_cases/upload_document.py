import uuid
from collections.abc import Callable

from app.business.entities.document import Document
from app.business.saga.saga import Saga, SagaStep
from app.business.services.interfaces.i_document_service import IDocumentService
from app.business.services.interfaces.i_extraction_service import IExtractionService
from app.business.services.interfaces.i_validation_service import IValidationService

VALIDATION = "validacion"
RESERVATION = "reserva"
EXTRACTION = "extraccion"
CONFIRMATION = "confirmacion"


def new_saga_id() -> str:
    return uuid.uuid4().hex


class UploadDocumentUseCase:
    """saga de subida: validar -> reservar checksum -> extraer texto -> confirmar"""

    def __init__(
        self,
        validation: IValidationService,
        extraction: IExtractionService,
        documents: IDocumentService,
        saga_id_factory: Callable[[], str] = new_saga_id,
    ) -> None:
        self._validation = validation
        self._extraction = extraction
        self._documents = documents
        self._saga_id_factory = saga_id_factory

    async def execute(self, file_bytes: bytes, filename: str) -> Document:
        saga_id = self._saga_id_factory()
        steps = [
            # 1. validacion: no deja nada hecho, no necesita compensacion
            SagaStep(VALIDATION, lambda ctx: self._validation.validate(file_bytes)),
            # 2. reserva: si falla algo despues, se libera
            SagaStep(
                RESERVATION,
                lambda ctx: self._documents.reserve(saga_id, ctx[VALIDATION].checksum, filename),
                compensation=lambda ctx: self._documents.release(ctx[RESERVATION].id, saga_id),
            ),
            # 3. extraccion: es la parte cara, va despues de descartar duplicados
            SagaStep(EXTRACTION, lambda ctx: self._extraction.extract_text(file_bytes)),
            # 4. confirmacion: guarda el texto y completa el documento
            SagaStep(
                CONFIRMATION,
                lambda ctx: self._documents.confirm(ctx[RESERVATION].id, saga_id, ctx[EXTRACTION]),
            ),
        ]
        context = await Saga(saga_id, steps).execute()
        return context[CONFIRMATION]
