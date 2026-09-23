import time
from collections import Counter
from contextlib import contextmanager
from uuid import uuid4

from opentelemetry import trace
from opentelemetry.trace import SpanKind

tracer = trace.get_tracer("atlasai.api")
_metrics = Counter()

def record_metric(name: str, value: int = 1) -> None:
    _metrics[name] += value

def metrics_snapshot() -> dict[str, int]:
    return dict(_metrics)

@contextmanager
def traced_operation(name: str, **attributes):
    started = time.perf_counter()
    with tracer.start_as_current_span(name, kind=SpanKind.INTERNAL) as span:
        for key, value in attributes.items():
            span.set_attribute(key, str(value))
        try:
            yield span
            record_metric(f"{name}.success")
        except Exception as exc:
            record_metric(f"{name}.error")
            span.record_exception(exc)
            raise
        finally:
            span.set_attribute("duration_ms", (time.perf_counter() - started) * 1000)

def request_id() -> str:
    return str(uuid4())
