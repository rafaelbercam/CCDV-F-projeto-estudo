from datetime import date

import pytest

from ccdv.projects.extraction import ExtractionError, extract_invoice
from tests.fakes import FakeClient, tool_use_response


GOOD = {"vendor": "Loja ana@empresa.com", "total": 150.0, "currency": "BRL", "issued_on": "2026-03-01"}


def test_valid_extraction_returns_invoice_with_pii_removed():
    client = FakeClient([tool_use_response(("tu", "record_invoice", GOOD))])
    invoice = extract_invoice(client, "nota fiscal de teste")
    assert invoice.issued_on == date(2026, 3, 1)
    assert invoice.vendor == "Loja [EMAIL]"


def test_forced_tool_choice_is_sent():
    client = FakeClient([tool_use_response(("tu", "record_invoice", GOOD))])
    extract_invoice(client, "nota")
    assert client.calls[0]["tool_choice"] == {"type": "tool", "name": "record_invoice"}


def test_invalid_output_is_retried_with_error_feedback():
    bad = {**GOOD, "currency": "XYZ"}
    client = FakeClient(
        [
            tool_use_response(("tu1", "record_invoice", bad)),
            tool_use_response(("tu2", "record_invoice", GOOD)),
        ]
    )
    invoice = extract_invoice(client, "nota")
    assert invoice.currency == "BRL"

    retry_messages = client.calls[1]["messages"]
    feedback = retry_messages[-1]["content"][0]
    assert feedback["is_error"] is True
    assert feedback["tool_use_id"] == "tu1"


def test_gives_up_after_max_attempts():
    bad = {**GOOD, "total": -1}
    client = FakeClient([tool_use_response(("t", "record_invoice", bad))] * 3)
    with pytest.raises(ExtractionError):
        extract_invoice(client, "nota", max_attempts=3)


def test_rejects_bad_input_before_calling_model():
    client = FakeClient()
    with pytest.raises(ValueError):
        extract_invoice(client, "   ")
    assert client.calls == []
