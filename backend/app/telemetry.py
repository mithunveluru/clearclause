"""OpenTelemetry wiring. Everything is a no-op unless OTEL_EXPORTER_OTLP_ENDPOINT
is set, so the app runs identically with or without the observability stack.

Traces + logs go OTLP -> Collector -> Tempo/Loki. HTTP metrics are exposed on
/metrics by prometheus-fastapi-instrumentator (wired in main.py) and scraped by
Prometheus directly, independent of this module.
"""
import logging

from app.core.config import settings

_INITIALIZED = False


def _enabled() -> bool:
    return bool(settings.OTEL_EXPORTER_OTLP_ENDPOINT)


def setup_telemetry(service_name: str) -> None:
    global _INITIALIZED
    if _INITIALIZED or not _enabled():
        return
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)
        )
    )
    trace.set_tracer_provider(provider)
    _setup_logs(resource)
    _setup_metrics(resource)
    _INITIALIZED = True


def _setup_metrics(resource) -> None:
    from opentelemetry import metrics
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True),
        export_interval_millis=15000,
    )
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))


def _setup_logs(resource) -> None:
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

    lp = LoggerProvider(resource=resource)
    lp.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)
        )
    )
    set_logger_provider(lp)
    root = logging.getLogger()
    root.addHandler(LoggingHandler(level=logging.INFO, logger_provider=lp))
    root.setLevel(logging.INFO)


def instrument_fastapi(app) -> None:
    if not _enabled():
        return
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app)


def instrument_engine(engine) -> None:
    if not _enabled():
        return
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)


def instrument_celery() -> None:
    if not _enabled():
        return
    from opentelemetry.instrumentation.celery import CeleryInstrumentor

    CeleryInstrumentor().instrument()


def instrument_redis() -> None:
    if not _enabled():
        return
    from opentelemetry.instrumentation.redis import RedisInstrumentor

    RedisInstrumentor().instrument()


def get_tracer(name: str = "clearclause"):
    """Returns a tracer; produces no-op spans when no provider is configured."""
    from opentelemetry import trace

    return trace.get_tracer(name)


def get_meter(name: str = "clearclause"):
    """Returns a meter; no-op instruments when no provider is configured."""
    from opentelemetry import metrics

    return metrics.get_meter(name)
