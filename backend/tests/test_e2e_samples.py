"""End-to-end on the 6 seeded sample documents: each file -> expected findings."""
from pathlib import Path

import pytest

from tests.pipeline_helper import run_pipeline

# /sample-data in the container; repo-relative when run from a CI checkout.
_CANDIDATES = [Path("/sample-data"), Path(__file__).resolve().parents[2] / "sample-data"]
SAMPLE_DIR = next((p for p in _CANDIDATES if p.is_dir()), None)

pytestmark = pytest.mark.skipif(SAMPLE_DIR is None, reason="sample-data directory not found")


def _run(name: str) -> dict:
    return run_pipeline((SAMPLE_DIR / name).read_text().splitlines(), name)


def test_risky_loan_1_flags_fees_and_penalties():
    r = _run("loan_risky_1.txt")
    assert {"processing_fee", "late_fee", "foreclosure_charge", "vague_pricing_revision"} <= r["types"]
    assert r["band"] != "Low"


def test_risky_loan_2_flags_prepayment_bundle_consent():
    r = _run("loan_risky_2.txt")
    assert {"prepayment_penalty", "bundled_addon", "implied_consent"} <= r["types"]
    assert r["band"] != "Low"


@pytest.mark.parametrize("name", ["loan_clean_1.txt", "loan_clean_2.txt"])
def test_clean_loans_are_low_risk(name):
    r = _run(name)
    assert r["findings"] == []
    assert r["band"] == "Low"


def test_subscription_trial_flags_autorenew():
    r = _run("subscription_trial.txt")
    assert {"auto_renew_trap", "hard_cancellation", "implied_consent"} <= r["types"]


def test_bundled_addon_flagged():
    r = _run("bundled_addon.txt")
    assert "bundled_addon" in r["types"]
