from app.business.services.interfaces.i_extraction_service import IExtractionService
from app.data.clients.service_client import ServiceClient

PDF_HEADERS = {"Content-Type": "application/pdf"}


class ExtractionClient(ServiceClient, IExtractionService):
    async def extract_text(self, file_bytes: bytes) -> str:
        # la etapa 1 pide solo el texto, por eso se pide format=text
        response = await self._send(
            "POST", "/extract", params={"format": "text"}, content=file_bytes, headers=PDF_HEADERS
        )
        return response.json()["content"]
