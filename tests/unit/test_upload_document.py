import pytest

from app.business.domain.exceptions import (
    DuplicateDocumentError,
    InvalidPDFError,
    ServiceTimeoutError,
    ServiceUnavailableError,
)
from app.use_cases.upload_document import UploadDocumentUseCase
from tests.unit.fakes import FakeDocuments, FakeExtraction, FakeValidation


def build(calls, validation_error=None, extraction_error=None, reserve_error=None, confirm_error=None):
    documents = FakeDocuments(calls, reserve_error, confirm_error)
    use_case = UploadDocumentUseCase(
        FakeValidation(calls, validation_error),
        FakeExtraction(calls, extraction_error),
        documents,
        saga_id_factory=lambda: "saga-fija",
    )
    return use_case, documents


async def test_camino_feliz_valida_reserva_extrae_y_confirma():
    calls = []
    use_case, documents = build(calls)
    document = await use_case.execute(b"%PDF", "a.pdf")

    assert calls == ["validate", "reserve", "extract", "confirm"]
    assert document.extracted_text == "texto extraido"
    assert set(documents.saga_ids) == {"saga-fija"}


async def test_pdf_invalido_corta_antes_de_reservar():
    calls = []
    use_case, _ = build(calls, validation_error=InvalidPDFError())
    with pytest.raises(InvalidPDFError):
        await use_case.execute(b"x", "a.pdf")
    assert calls == ["validate"]


async def test_duplicado_corta_antes_de_extraer_y_no_compensa():
    calls = []
    use_case, _ = build(calls, reserve_error=DuplicateDocumentError())
    with pytest.raises(DuplicateDocumentError):
        await use_case.execute(b"%PDF", "a.pdf")
    assert calls == ["validate", "reserve"]


async def test_si_falla_la_extraccion_libera_la_reserva():
    calls = []
    use_case, _ = build(calls, extraction_error=ServiceUnavailableError("pdf-extract-service"))
    with pytest.raises(ServiceUnavailableError):
        await use_case.execute(b"%PDF", "a.pdf")
    assert calls == ["validate", "reserve", "extract", "release"]


async def test_si_falla_la_confirmacion_libera_la_reserva():
    calls = []
    use_case, _ = build(calls, confirm_error=ServiceTimeoutError("pdf-extractext"))
    with pytest.raises(ServiceTimeoutError):
        await use_case.execute(b"%PDF", "a.pdf")
    assert calls == ["validate", "reserve", "extract", "confirm", "release"]
