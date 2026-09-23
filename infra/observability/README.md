# AtlasAI observability

The API emits OpenTelemetry spans through the atlasai.api tracer and exposes lightweight counters at GET /api/v1/metrics.

The counters are intentionally process-local for the MVP; production deployments should export OpenTelemetry to a collector and use a durable metrics backend. Request IDs are returned on every API response for correlation.
