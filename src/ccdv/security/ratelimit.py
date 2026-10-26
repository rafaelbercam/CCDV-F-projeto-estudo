"""Módulo 05 — rate limiting com token bucket.

`burst` é o que permite rajadas curtas legítimas; `rate_per_sec` é a taxa sustentada.
Sem burst, um usuário que faz 3 perguntas em 1 segundo seria bloqueado sem motivo.
"""

import time
from collections.abc import Callable


class TokenBucket:
    def __init__(
        self,
        rate_per_sec: float,
        burst: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.rate = rate_per_sec
        self.capacity = burst
        self._tokens = burst
        self._clock = clock
        self._last = clock()

    def allow(self, cost: float = 1.0) -> bool:
        now = self._clock()
        self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rate)
        self._last = now
        if self._tokens >= cost:
            self._tokens -= cost
            return True
        return False
