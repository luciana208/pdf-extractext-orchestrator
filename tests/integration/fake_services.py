"""los tres servicios internos simulados en memoria detras de un httpx.MockTransport"""

import hashlib
import json
from datetime import datetime, timezone
from itertools import count

import httpx

NOW = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc).isoformat()


def problem(status: int, detail: str) -> httpx.Response:
    body = {"type": "about:blank", "title": "error", "status": status, "detail": detail, "instance": ""}
    return httpx.Response(status, json=body, headers={"content-type": "application/problem+json"})


class FakeServices:
    def __init__(self) -> None:
        self.documents: dict[str, dict] = {}
        self._ids = count(1)
        self.down: set[str] = set()
        self.calls: list[str] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        host = request.url.host
        if host in self.down:
            raise httpx.ConnectError("servicio caido", request=request)
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if host == "validation.internal":
            return self._validation(request)
        if host == "extract.internal":
            return self._extract(request)
        return self._documents(request)

    def _validation(self, request: httpx.Request) -> httpx.Response:
        self.calls.append("validate")
        content = request.read()
        if not content.startswith(b"%PDF"):
            return problem(400, "el archivo no es un PDF valido")
        return httpx.Response(200, json={"checksum": hashlib.sha256(content).hexdigest(), "size_bytes": len(content), "page_count": 1})

    def _extract(self, request: httpx.Request) -> httpx.Response:
        self.calls.append("extract")
        content = request.read()
        return httpx.Response(200, json={"content": content.decode("latin-1")[5:], "page_count": 1})

    def _documents(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path.removeprefix("/api/v1/documents")
        method = request.method
        if method == "POST" and path == "/reservations":
            self.calls.append("reserve")
            body = json.loads(request.read())
            if any(d["checksum"] == body["checksum"] for d in self.documents.values()):
                return problem(409, "ya existe un documento con ese checksum")
            document_id = f"{next(self._ids):024x}"
            self.documents[document_id] = {**body, "id": document_id, "status": "pending", "text": ""}
            return httpx.Response(201, json={"id": document_id, "status": "pending", "expires_at": NOW})
        if method == "PUT" and path.endswith("/content"):
            self.calls.append("confirm")
            document = self.documents[path.split("/")[1]]
            document.update(status="completed", text=json.loads(request.read())["extracted_text"])
            return httpx.Response(200, json=self._public(document))
        if method == "DELETE" and path.startswith("/reservations/"):
            self.calls.append("release")
            self.documents.pop(path.split("/")[2], None)
            return httpx.Response(204)
        if method == "GET" and path == "":
            return httpx.Response(200, json=[self._public(d) for d in self.documents.values() if d["status"] == "completed"])

        document = self.documents.get(path.strip("/"))
        if document is None or document["status"] != "completed":
            return problem(404, "no existe el documento")
        if method == "GET":
            return httpx.Response(200, json=self._public(document))
        if method == "PUT":
            document["filename"] = json.loads(request.read())["custom_name"]
            return httpx.Response(200, json=self._public(document))
        del self.documents[document["id"]]
        return httpx.Response(200, json={"message": "Documento eliminado correctamente."})

    @staticmethod
    def _public(document: dict) -> dict:
        return {
            "id": document["id"],
            "name": document["filename"],
            "checksum": document["checksum"],
            "extracted_text": document["text"],
            "text_preview": document["text"][:500],
            "created_at": NOW,
            "updated_at": NOW,
        }
