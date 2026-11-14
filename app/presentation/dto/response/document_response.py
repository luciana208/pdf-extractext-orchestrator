"""contrato de salida de un documento, igual al de la etapa 1 (el cliente no nota la migracion)"""

from datetime import datetime

from pydantic import BaseModel, Field, computed_field, field_serializer

from app.business.entities.document import Document


class DocumentResponseDTO(BaseModel):
    id: str = Field(description="Identificador unico del documento.")
    name: str = Field(description="Nombre del documento.")
    checksum: str = Field(description="Hash SHA-256 del archivo PDF.")
    extracted_text: str = Field(description="Texto extraido. Vacio si el PDF es escaneado.")
    created_at: datetime = Field(description="Fecha y hora de creacion.")
    updated_at: datetime = Field(description="Fecha y hora de ultima modificacion.")

    model_config = {"frozen": True}

    @field_serializer("created_at", "updated_at")
    def _serialize_date(self, moment: datetime) -> str:
        return moment.isoformat()

    @computed_field(return_type=str)
    @property
    def text_preview(self) -> str:
        return self.extracted_text[:500]

    @classmethod
    def from_entity(cls, document: Document) -> "DocumentResponseDTO":
        return cls(
            id=document.id,
            name=document.filename,
            checksum=document.checksum,
            extracted_text=document.extracted_text,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
