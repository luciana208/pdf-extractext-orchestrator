from app.business.entities.document import ValidatedPDF
from app.business.services.interfaces.i_validation_service import IValidationService
from app.data.clients.service_client import ServiceClient

PDF_HEADERS = {"Content-Type": "application/pdf"}


class ValidationClient(ServiceClient, IValidationService):
    async def validate(self, file_bytes: bytes) -> ValidatedPDF:
        response = await self._send("POST", "/api/v1/validations", content=file_bytes, headers=PDF_HEADERS)
        body = response.json()
        return ValidatedPDF(checksum=body["checksum"], size_bytes=body["size_bytes"], page_count=body["page_count"])
