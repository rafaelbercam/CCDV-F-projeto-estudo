from types import SimpleNamespace as NS

from ccdv.optimization.batch import build_batch_requests, collect_results
from ccdv.optimization.benchmark import time_calls
from ccdv.optimization.caching import cached_ask, usage_report
from tests.fakes import FakeClient, text_response, usage_obj


def test_cache_control_is_on_system_block():
    client = FakeClient([text_response("ok")])
    cached_ask(client, "SYSTEM LONGO", "pergunta")
    system = client.calls[0]["system"]
    assert system[0]["cache_control"] == {"type": "ephemeral"}


def test_usage_report_counts_cache_in_total_input():
    report = usage_report(usage_obj(input_tokens=100, output_tokens=20, cache_read=900, cache_write=0))
    assert report["cache_hit_ratio"] == 0.9


def test_usage_report_without_cache_is_zero_ratio():
    report = usage_report(usage_obj(input_tokens=50, output_tokens=5))
    assert report["cache_hit_ratio"] == 0.0


def test_batch_requests_keep_custom_ids():
    reqs = build_batch_requests([("a", "oi"), ("b", "tchau")], model="m", max_tokens=10)
    assert [r["custom_id"] for r in reqs] == ["a", "b"]
    assert reqs[1]["params"]["messages"][0]["content"] == "tchau"


def test_collect_results_skips_errors():
    entries = [
        NS(custom_id="ok", result=NS(type="succeeded", message=text_response("resposta"))),
        NS(custom_id="ruim", result=NS(type="errored", message=None)),
    ]
    assert collect_results(entries) == {"ok": "resposta"}


def test_benchmark_reports_percentiles():
    stats = time_calls(lambda: None, n=10)
    assert set(stats) == {"mean", "p50", "p95", "max"}
    assert stats["p50"] <= stats["p95"] <= stats["max"]
