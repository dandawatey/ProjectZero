"""
OpenTelemetry integration — optional trace/span export — PRJ0-56.

Gracefully degrades: if opentelemetry packages are not installed,
all calls are no-ops. Install with:
    pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc

NORMAL MODE:
  Each execution event → span with attributes (ticket, epic, agent, workflow).
  Spans exported to OTLP endpoint (Jaeger, Tempo, Honeycomb, etc.).

CAVEMAN MODE:
  Thing run. We record it. Record goes to trace tool.
  Trace tool show timeline. You see what ran, when, how long.
"""
from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False


class OtelExporter:
    """
    Wraps OpenTelemetry tracer. Safe to instantiate even if otel not installed.
    When otel is unavailable, all methods are no-ops.
    """

    def __init__(self, service_name: str = "execution-console", endpoint: str = "http://localhost:4317"):
        self._tracer = None
        self._active_spans: dict[str, object] = {}

        if not _OTEL_AVAILABLE:
            logger.debug("opentelemetry not installed — OTel export disabled")
            return

        try:
            resource = Resource.create({"service.name": service_name})
            provider = TracerProvider(resource=resource)
            exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)
            self._tracer = trace.get_tracer(service_name)
            logger.info(f"OTel tracer initialized → {endpoint}")
        except Exception as exc:
            logger.warning(f"OTel init failed: {exc}")

    def start_span(
        self,
        span_key: str,
        operation: str,
        ticket_id: Optional[str] = None,
        epic_key: Optional[str] = None,
        feature_id: Optional[str] = None,
        workflow_run_id: Optional[str] = None,
        agent: Optional[str] = None,
    ) -> None:
        """Start a named span. span_key used to correlate with end_span()."""
        if not self._tracer:
            return
        try:
            span = self._tracer.start_span(operation)
            if ticket_id:
                span.set_attribute("ticket.id", ticket_id)
            if epic_key:
                span.set_attribute("epic.key", epic_key)
            if feature_id:
                span.set_attribute("feature.id", feature_id)
            if workflow_run_id:
                span.set_attribute("workflow.run_id", workflow_run_id)
            if agent:
                span.set_attribute("agent.name", agent)
            self._active_spans[span_key] = span
        except Exception as exc:
            logger.debug(f"OTel start_span failed: {exc}")

    def end_span(self, span_key: str, status: str = "SUCCESS", error: Optional[str] = None) -> None:
        """End a previously started span."""
        if not self._tracer:
            return
        span = self._active_spans.pop(span_key, None)
        if not span:
            return
        try:
            from opentelemetry.trace import StatusCode
            if status in ("FAILED", "BLOCKED"):
                span.set_status(StatusCode.ERROR, error or status)
            else:
                span.set_status(StatusCode.OK)
            span.end()
        except Exception as exc:
            logger.debug(f"OTel end_span failed: {exc}")

    def record_event(
        self,
        operation: str,
        ticket_id: Optional[str] = None,
        workflow_run_id: Optional[str] = None,
        agent: Optional[str] = None,
        status: str = "SUCCESS",
        duration_ms: Optional[int] = None,
    ) -> None:
        """Convenience: fire-and-forget span for point events."""
        key = f"point_{operation}_{ticket_id}"
        self.start_span(key, operation, ticket_id=ticket_id,
                        workflow_run_id=workflow_run_id, agent=agent)
        if duration_ms:
            pass  # real span timing handled by otel internally
        self.end_span(key, status=status)


# Singleton — import and use directly
_exporter: Optional[OtelExporter] = None


def get_exporter(service_name: str = "execution-console", endpoint: str = "http://localhost:4317") -> OtelExporter:
    global _exporter
    if _exporter is None:
        _exporter = OtelExporter(service_name=service_name, endpoint=endpoint)
    return _exporter
