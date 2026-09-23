from app.services.observability import metrics_snapshot, record_metric

def test_metrics_counter_is_incremented() -> None:
    record_metric("test.counter")
    assert metrics_snapshot()["test.counter"] >= 1
