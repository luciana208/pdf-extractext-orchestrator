import httpx
import pytest

from app.business.domain.exceptions import (
    DocumentNotFoundError,
    DuplicateDocumentError,
    InvalidPDFError,
    InvalidRequestError,
    PDFTooLargeError,
    ServiceTimeoutError,
    ServiceUnavailableError,
    UnexpectedResponseError,
)
from app.data.clients.documents_client import DocumentsClient
from app.data.clients.extraction_client import ExtractionClient
from app.data.clients.validation_client import ValidationClient


def client_with(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url="http://servicio", transport=httpx.MockTransport(handler))


def problem(status: int) -> httpx.Response:
    return httpx.Response(status, json={"type": "about:blank", "status": status, "detail": f"detalle {status}"})


@pytest.mark.parametrize(
    ("status", "error"),
    [
        (400, InvalidPDFError),
        (404, DocumentNotFoundError),
        (409, DuplicateDocumentError),
        (413, PDFTooLargeError),
        (422, InvalidRequestError),
        (500, ServiceUnavailableError),
        (503, ServiceUnavailableError),
        (418, UnexpectedResponseError),
    ],
)
async def test_traduce_status_a_error_de_dominio(status, error):
    client = DocumentsClient("pdf-extractext", client_with(lambda request: problem(status)))
    with pytest.raises(error):
        await client.get("abc")


async def test_conserva_el_detalle_del_problem_json():
    client = ValidationClient("pdf-validation-service", client_with(lambda request: problem(400)))
    with pytest.raises(InvalidPDFError, match="detalle 400"):
        await client.validate(b"x")


async def test_timeout_se_traduce_a_service_timeout():
    def handler(request):
        raise httpx.ReadTimeout("lento", request=request)

    client = ExtractionClient("pdf-extract-service", client_with(handler))
    with pytest.raises(ServiceTimeoutError):
        await client.extract_text(b"%PDF")


async def test_error_de_conexion_se_traduce_a_service_unavailable():
    def handler(request):
        raise httpx.ConnectError("sin conexion", request=request)

    client = ExtractionClient("pdf-extract-service", client_with(handler))
    with pytest.raises(ServiceUnavailableError):
        await client.extract_text(b"%PDF")


async def test_extraccion_pide_formato_texto_y_manda_el_pdf_binario():
    seen = {}

    def handler(request):
        seen["format"] = request.url.params["format"]
        seen["content_type"] = request.headers["content-type"]
        return httpx.Response(200, json={"content": "hola", "page_count": 1})

    client = ExtractionClient("pdf-extract-service", client_with(handler))
    assert await client.extract_text(b"%PDF") == "hola"
    assert seen == {"format": "text", "content_type": "application/pdf"}


async def test_reserva_manda_saga_checksum_y_nombre():
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["body"] = request.read()
        return httpx.Response(201, json={"id": "r1", "status": "pending", "expires_at": "2026-11-13T12:00:00+00:00"})

    client = DocumentsClient("pdf-extractext", client_with(handler))
    reservation = await client.reserve("s1", "f" * 64, "a.pdf")
    assert reservation.id == "r1"
    assert seen["path"] == "/api/v1/documents/reservations"
    assert b'"saga_id":"s1"' in seen["body"]
