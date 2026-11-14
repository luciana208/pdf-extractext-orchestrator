import pytest

from app.business.saga.saga import Saga, SagaStep


async def test_ejecuta_los_pasos_en_orden_y_guarda_resultados():
    order = []

    async def step(name, value):
        order.append(name)
        return value

    saga = Saga("s1", [
        SagaStep("a", lambda ctx: step("a", 1)),
        SagaStep("b", lambda ctx: step("b", ctx["a"] + 1)),
    ])
    context = await saga.execute()

    assert order == ["a", "b"]
    assert context == {"a": 1, "b": 2}


async def test_si_un_paso_falla_compensa_en_orden_inverso_y_relanza():
    compensations = []

    async def ok(ctx):
        return "ok"

    async def boom(ctx):
        raise RuntimeError("fallo")

    async def compensate(name):
        compensations.append(name)

    saga = Saga("s1", [
        SagaStep("a", ok, compensation=lambda ctx: compensate("a")),
        SagaStep("b", ok, compensation=lambda ctx: compensate("b")),
        SagaStep("c", boom, compensation=lambda ctx: compensate("c")),
    ])
    with pytest.raises(RuntimeError):
        await saga.execute()

    # el paso que fallo no se compensa: no llego a hacer nada
    assert compensations == ["b", "a"]


async def test_una_compensacion_que_falla_no_frena_las_demas():
    compensations = []

    async def ok(ctx):
        return None

    async def boom(ctx):
        raise RuntimeError("fallo")

    async def compensation_boom(ctx):
        raise ConnectionError("caido")

    async def compensate_a(ctx):
        compensations.append("a")

    saga = Saga("s1", [
        SagaStep("a", ok, compensation=compensate_a),
        SagaStep("b", ok, compensation=compensation_boom),
        SagaStep("c", boom),
    ])
    with pytest.raises(RuntimeError):
        await saga.execute()
    assert compensations == ["a"]
