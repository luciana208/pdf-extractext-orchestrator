URL = "/api/v1/documents/"
PDF = b"%PDF-1.4 Hola Mundo PDF"


async def upload(client, content=PDF, filename="informe.pdf", custom_name=None):
    data = {"custom_name": custom_name} if custom_name else None
    return await client.post(URL, files={"file": (filename, content, "application/pdf")}, data=data)


async def test_subida_corre_la_saga_completa(client, services):
    response = await upload(client)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "informe.pdf"
    assert body["extracted_text"] == "1.4 Hola Mundo PDF"
    assert services.calls == ["validate", "reserve", "extract", "confirm"]


async def test_custom_name_reemplaza_el_nombre(client):
    response = await upload(client, custom_name="mio.pdf")
    assert response.json()["name"] == "mio.pdf"


async def test_duplicado_devuelve_409_sin_extraer(client, services):
    await upload(client)
    services.calls.clear()
    response = await upload(client)
    assert response.status_code == 409
    assert response.headers["content-type"] == "application/problem+json"
    assert services.calls == ["validate", "reserve"]


async def test_no_pdf_devuelve_400(client, services):
    response = await upload(client, content=b"no soy un pdf")
    assert response.status_code == 400
    assert services.calls == ["validate"]


async def test_extraccion_caida_devuelve_503_y_compensa(client, services):
    services.down.add("extract.internal")
    response = await upload(client)
    assert response.status_code == 503
    assert services.calls == ["validate", "reserve", "release"]
    assert services.documents == {}


async def test_validacion_caida_devuelve_503(client, services):
    services.down.add("validation.internal")
    response = await upload(client)
    assert response.status_code == 503


async def test_request_muy_grande_devuelve_413(client):
    response = await upload(client, content=b"%PDF" + b"0" * (11 * 1024 * 1024))
    assert response.status_code == 413


async def test_crud_y_descarga(client):
    document_id = (await upload(client)).json()["id"]

    listed = await client.get(URL)
    assert [d["id"] for d in listed.json()] == [document_id]

    assert (await client.get(f"{URL}{document_id}")).status_code == 200

    renamed = await client.put(f"{URL}{document_id}", json={"custom_name": "nuevo.pdf"})
    assert renamed.json()["name"] == "nuevo.pdf"

    download = await client.get(f"{URL}{document_id}/download")
    assert download.status_code == 200
    assert download.text == "1.4 Hola Mundo PDF"
    assert 'filename="nuevo.txt"' in download.headers["content-disposition"]

    assert (await client.delete(f"{URL}{document_id}")).status_code == 200
    assert (await client.get(f"{URL}{document_id}")).status_code == 404


async def test_limit_fuera_de_rango_devuelve_422(client):
    response = await client.get(URL, params={"limit": 1000})
    assert response.status_code == 422


async def test_health_ok_con_todos_los_servicios(client):
    body = (await client.get("/health")).json()
    assert body["status"] == "ok"
    assert set(body["dependencies"]) == {"pdf-validation-service", "pdf-extract-service", "pdf-extractext"}


async def test_health_degradado_si_cae_un_servicio(client, services):
    services.down.add("documents.internal")
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["dependencies"]["pdf-extractext"] == "down"
