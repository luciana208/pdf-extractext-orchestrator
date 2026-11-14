"""entidades que el orquestador recibe de los servicios internos"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Document:
    id: str
    filename: str
    checksum: str
    extracted_text: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ValidatedPDF:
    checksum: str
    size_bytes: int
    page_count: int


@dataclass(frozen=True)
class Reservation:
    id: str
    expires_at: datetime
