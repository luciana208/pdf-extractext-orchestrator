"""nombre y header de la descarga del texto como .txt"""

from urllib.parse import quote


def txt_filename(original: str) -> str:
    base = original[:-4] if original.lower().endswith(".pdf") else original
    return f"{base}.txt"


def content_disposition(filename: str) -> str:
    # los headers viajan en latin-1: filename lleva un respaldo ascii y filename* el nombre real (rfc 6266)
    ascii_fallback = filename.encode("ascii", "replace").decode("ascii").replace('"', "")
    return f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{quote(filename)}"
