"""base de los clientes http hacia los servicios internos: traduce errores de red y problem details"""

import logging

import httpx

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

logger = logging.getLogger(__name__)

# status del servicio interno -> error de dominio que entiende el orquestador
_CLIENT_ERRORS = {
    400: InvalidPDFError,
    404: DocumentNotFoundError,
    409: DuplicateDocumentError,
    413: PDFTooLargeError,
    422: InvalidRequestError,
}


def _detail(response: httpx.Response) -> str:
    # los servicios responden rfc 9457; si no, se usa el texto crudo
    try:
        return str(response.json().get("detail", ""))
    except ValueError:
        return response.text[:200]


class ServiceClient:
    def __init__(self, name: str, client: httpx.AsyncClient) -> None:
        self.name = name
        self._client = client

    async def _send(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            response = await self._client.request(method, url, **kwargs)
        except httpx.TimeoutException as exc:
            logger.warning("timeout llamando a %s %s", self.name, url)
            raise ServiceTimeoutError(self.name) from exc
        except httpx.TransportError as exc:
            logger.warning("no se pudo conectar con %s: %s", self.name, exc)
            raise ServiceUnavailableError(self.name) from exc

        if response.is_success:
            return response

        status = response.status_code
        if status in _CLIENT_ERRORS:
            raise _CLIENT_ERRORS[status](_detail(response))
        if status >= 500:
            raise ServiceUnavailableError(self.name, f"(status {status})")
        raise UnexpectedResponseError(self.name, status)

    async def is_healthy(self) -> bool:
        response = await self._client.get("/health", timeout=2.0)
        return response.status_code == 200
