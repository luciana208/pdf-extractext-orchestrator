from datetime import datetime

from app.business.entities.document import Document, Reservation
from app.business.services.interfaces.i_document_service import IDocumentService
from app.data.clients.service_client import ServiceClient

BASE = "/api/v1/documents"


def _to_document(body: dict) -> Document:
    return Document(
        id=body["id"],
        filename=body["name"],
        checksum=body["checksum"],
        extracted_text=body["extracted_text"],
        created_at=datetime.fromisoformat(body["created_at"]),
        updated_at=datetime.fromisoformat(body["updated_at"]),
    )


class DocumentsClient(ServiceClient, IDocumentService):
    async def reserve(self, saga_id: str, checksum: str, filename: str) -> Reservation:
        payload = {"saga_id": saga_id, "checksum": checksum, "filename": filename}
        body = (await self._send("POST", f"{BASE}/reservations", json=payload)).json()
        return Reservation(id=body["id"], expires_at=datetime.fromisoformat(body["expires_at"]))

    async def confirm(self, reservation_id: str, saga_id: str, extracted_text: str) -> Document:
        payload = {"saga_id": saga_id, "extracted_text": extracted_text}
        return _to_document((await self._send("PUT", f"{BASE}/{reservation_id}/content", json=payload)).json())

    async def release(self, reservation_id: str, saga_id: str) -> None:
        await self._send("DELETE", f"{BASE}/reservations/{reservation_id}", params={"saga_id": saga_id})

    async def list(self, skip: int, limit: int) -> list[Document]:
        response = await self._send("GET", BASE, params={"skip": skip, "limit": limit})
        return [_to_document(item) for item in response.json()]

    async def get(self, document_id: str) -> Document:
        return _to_document((await self._send("GET", f"{BASE}/{document_id}")).json())

    async def rename(self, document_id: str, custom_name: str | None) -> Document:
        payload = {"custom_name": custom_name}
        return _to_document((await self._send("PUT", f"{BASE}/{document_id}", json=payload)).json())

    async def delete(self, document_id: str) -> str:
        return (await self._send("DELETE", f"{BASE}/{document_id}")).json()["message"]
