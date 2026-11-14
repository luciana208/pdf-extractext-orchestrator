"""clientes http hacia los servicios internos, uno por servicio y por proceso"""

from dataclasses import dataclass

import httpx

from app.config.settings import Settings


@dataclass
class HttpClients:
    validation: httpx.AsyncClient
    extraction: httpx.AsyncClient
    documents: httpx.AsyncClient

    async def aclose(self) -> None:
        for client in (self.validation, self.extraction, self.documents):
            await client.aclose()


def build_http_clients(config: Settings, transport: httpx.AsyncBaseTransport | None = None) -> HttpClients:
    def client(base_url: str, timeout: float) -> httpx.AsyncClient:
        # retries del transporte: reintenta solo si falla la conexion, nunca un request ya enviado
        return httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout, connect=3.0),
            transport=transport or httpx.AsyncHTTPTransport(retries=config.http_connect_retries),
        )

    return HttpClients(
        validation=client(config.validation_url, config.validation_timeout),
        extraction=client(config.extraction_url, config.extraction_timeout),
        documents=client(config.documents_url, config.documents_timeout),
    )
