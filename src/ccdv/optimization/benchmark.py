"""Módulo 04 — medir latência antes de otimizar. Sem número, não há decisão."""

import statistics
import time
from collections.abc import Callable
from typing import Any


def time_calls(fn: Callable[[], Any], n: int = 5) -> dict[str, float]:
    """Executa `fn` n vezes e devolve latências em segundos (mean, p50, p95, max)."""
    if n < 1:
        raise ValueError("n deve ser >= 1")
    samples: list[float] = []
    for _ in range(n):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    ordered = sorted(samples)
    p95_index = min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))
    return {
        "mean": statistics.fmean(ordered),
        "p50": statistics.median(ordered),
        "p95": ordered[p95_index],
        "max": ordered[-1],
    }
