"""V2/V3 platform metrics. Instruments are created lazily on a meter that is a
no-op until telemetry is configured, so every call here is safe with AI/OTel off."""
from app.telemetry import get_meter

_inst: dict = {}


def _instruments() -> dict:
    if not _inst:
        m = get_meter("clearclause.platform")
        # names omit the unit/_total suffix; the Prometheus exporter appends it
        _inst["stage"] = m.create_histogram(
            "clearclause_stage_duration", unit="s", description="Pipeline stage duration",
        )
        _inst["classified"] = m.create_counter(
            "clearclause_documents_classified", description="Documents classified, by type",
        )
        _inst["analyzer"] = m.create_counter(
            "clearclause_analyzer_runs", description="Analyzer runs, by analyzer and status",
        )
        _inst["ai"] = m.create_histogram(
            "clearclause_ai_request_duration", unit="s",
            description="AI/embedding/retrieval latency, by kind",
        )
        # The two ways this system goes quietly wrong rather than loudly down. Both
        # were log lines only, and nobody greps logs at 3am.
        _inst["degraded"] = m.create_counter(
            "clearclause_degraded_events",
            description="Silent-degradation events, by kind "
                        "(rate_limiter_unavailable | low_ocr_confidence)",
        )
    return _inst


def record_stage(stage: str, seconds: float) -> None:
    _instruments()["stage"].record(seconds, {"stage": stage})


def count_classification(doc_type: str) -> None:
    _instruments()["classified"].add(1, {"type": doc_type})


def count_analyzer(analyzer: str, status: str) -> None:
    _instruments()["analyzer"].add(1, {"analyzer": analyzer, "status": status})


def record_ai(kind: str, seconds: float) -> None:
    _instruments()["ai"].record(seconds, {"kind": kind})


def count_degraded(kind: str) -> None:
    """Something is serving, but not correctly. Alert on this, not on the log line."""
    _instruments()["degraded"].add(1, {"kind": kind})
