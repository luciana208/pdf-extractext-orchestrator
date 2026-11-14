from app.config.settings import Settings
from app.infrastructure.traefik_tags import build_traefik_tags


def test_router_interno_con_circuit_breaker_y_reintentos():
    tags = build_traefik_tags(Settings(router_name="orchestrator", internal_host="orchestrator.internal", public_host=""))
    assert "traefik.enable=true" in tags
    assert "traefik.http.routers.orchestrator-internal.rule=Host(`orchestrator.internal`)" in tags
    assert "traefik.http.routers.orchestrator-internal.entrypoints=internal" in tags
    assert "traefik.http.routers.orchestrator-internal.middlewares=orchestrator-cb,orchestrator-retry" in tags
    assert any(tag.startswith("traefik.http.middlewares.orchestrator-cb.circuitbreaker.expression=") for tag in tags)
    assert "traefik.http.middlewares.orchestrator-retry.retry.attempts=3" in tags


def test_sin_host_publico_no_hay_router_https():
    tags = build_traefik_tags(Settings(router_name="orchestrator", public_host=""))
    assert not any(".routers.orchestrator.rule" in tag for tag in tags)


def test_con_host_publico_agrega_router_https_con_tls():
    tags = build_traefik_tags(Settings(router_name="orchestrator", public_host="orchestrator.pdfextractext.localhost"))
    assert "traefik.http.routers.orchestrator.entrypoints=https" in tags
    assert "traefik.http.routers.orchestrator.tls=true" in tags
