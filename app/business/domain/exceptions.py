"""errores de negocio y de comunicacion con otros servicios, no conocen http ni fastapi"""


class DomainError(Exception):
    """base de todos los errores"""


class InvalidPDFError(DomainError):
    def __init__(self, detail: str = "el archivo no es un PDF valido") -> None:
        super().__init__(detail)


class PDFTooLargeError(DomainError):
    def __init__(self, detail: str = "el archivo supera el tamaño maximo") -> None:
        super().__init__(detail)


class DocumentNotFoundError(DomainError):
    def __init__(self, detail: str = "no existe el documento") -> None:
        super().__init__(detail)


class DuplicateDocumentError(DomainError):
    def __init__(self, detail: str = "ya existe un documento con el mismo contenido") -> None:
        super().__init__(detail)


class InvalidRequestError(DomainError):
    def __init__(self, detail: str = "datos invalidos") -> None:
        super().__init__(detail)


class ServiceUnavailableError(DomainError):
    """el servicio interno no responde, esta caido o saturado"""

    def __init__(self, service: str, detail: str = "") -> None:
        super().__init__(f"el servicio {service} no esta disponible {detail}".strip())
        self.service = service


class ServiceTimeoutError(DomainError):
    def __init__(self, service: str) -> None:
        super().__init__(f"el servicio {service} no respondio a tiempo")
        self.service = service


class UnexpectedResponseError(DomainError):
    def __init__(self, service: str, status: int) -> None:
        super().__init__(f"respuesta inesperada de {service} (status {status})")
        self.service = service
        self.status = status
