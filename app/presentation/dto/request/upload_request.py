from pydantic import BaseModel, Field


class UploadRequestDTO(BaseModel):
    # el pdf llega como UploadFile, aca solo van los metadatos que lo acompañan
    custom_name: str | None = Field(default=None, max_length=255, description="Nombre opcional del documento.")

    model_config = {"frozen": True}
