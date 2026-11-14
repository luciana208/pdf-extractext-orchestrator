"""
patron saga orquestado: ejecuta los pasos en orden y, si uno falla,
corre las compensaciones de los pasos ya hechos en orden inverso.
"""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

SagaContext = dict[str, Any]
StepAction = Callable[[SagaContext], Awaitable[Any]]
Compensation = Callable[[SagaContext], Awaitable[None]]


@dataclass(frozen=True)
class SagaStep:
    # el resultado de cada paso queda en el contexto bajo su nombre
    name: str
    action: StepAction
    compensation: Compensation | None = None


class Saga:
    def __init__(self, saga_id: str, steps: list[SagaStep]) -> None:
        self.saga_id = saga_id
        self._steps = steps

    async def execute(self) -> SagaContext:
        context: SagaContext = {}
        done: list[SagaStep] = []
        for step in self._steps:
            logger.info("saga=%s paso=%s inicio", self.saga_id, step.name)
            try:
                context[step.name] = await step.action(context)
            except Exception as exc:
                logger.warning("saga=%s paso=%s fallo: %s", self.saga_id, step.name, exc)
                await self._compensate(done, context)
                raise
            done.append(step)
            logger.info("saga=%s paso=%s ok", self.saga_id, step.name)
        logger.info("saga=%s completada", self.saga_id)
        return context

    async def _compensate(self, done: list[SagaStep], context: SagaContext) -> None:
        for step in reversed(done):
            if step.compensation is None:
                continue
            try:
                await step.compensation(context)
                logger.info("saga=%s compensacion=%s ok", self.saga_id, step.name)
            except Exception as exc:
                # si la compensacion falla, la reserva vence sola por el ttl de mongo
                logger.error("saga=%s compensacion=%s fallo: %s", self.saga_id, step.name, exc)
