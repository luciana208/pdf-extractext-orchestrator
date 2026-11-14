from pydantic import BaseModel, Field


class UpdateRequestDTO(BaseModel):
    # solo los metadatos se pueden cambiar, el texto y el checksum no
    custom_name: str | None = Field(default=None, max_length=255, description="Nuevo nombre del documento.")

    model_config = {"frozen": True}
