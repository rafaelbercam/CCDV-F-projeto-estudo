import pytest

from ccdv.security.audit import AuditLog
from ccdv.security.pii import redact_pii
from ccdv.security.ratelimit import TokenBucket
from ccdv.security.validation import validate_user_text


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_input_rejected(text):
    assert validate_user_text(text).ok is False


def test_too_long_input_rejected():
    assert validate_user_text("a" * 11, max_chars=10).reason.startswith("entrada excede")


def test_control_characters_rejected_but_newlines_allowed():
    assert validate_user_text("oi\x00").ok is False
    assert validate_user_text("linha 1\nlinha 2\tok").ok is True


@pytest.mark.parametrize(
    "raw, label",
    [
        ("fale com ana@empresa.com.br", "EMAIL"),
        ("CPF 123.456.789-09", "CPF"),
        ("SSN 123-45-6789", "SSN"),
        ("ligue (11) 91234-5678", "PHONE"),
        ("ligue +55 11 91234-5678", "PHONE"),
    ],
)
def test_redacts_known_formats(raw, label):
    result = redact_pii(raw)
    assert f"[{label}]" in result.text
    assert label in result.counts


def test_redaction_leaves_plain_text_alone():
    assert redact_pii("nota de R$ 150,00 emitida hoje").text == "nota de R$ 150,00 emitida hoje"


def test_token_bucket_allows_burst_then_blocks_then_refills():
    now = [0.0]
    bucket = TokenBucket(rate_per_sec=1, burst=3, clock=lambda: now[0])
    assert [bucket.allow() for _ in range(4)] == [True, True, True, False]
    now[0] += 1.0  # um segundo depois, uma ficha
    assert bucket.allow() is True
    assert bucket.allow() is False


def test_audit_log_stores_hash_not_raw_id(tmp_path):
    log_path = tmp_path / "audit.log"
    AuditLog(log_path).record("user-123", "extract", chars=42)
    line = log_path.read_text(encoding="utf-8").strip()
    assert "user-123" not in line
    assert '"chars": 42' in line
