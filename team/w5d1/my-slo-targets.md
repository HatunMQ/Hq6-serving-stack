# Service indicators and proposed targets

Team: 05

Use case: Chat serving service using vLLM for user text generation requests.

Service measured: Qwen/Qwen2.5-1.5B-Instruct-AWQ model served by vLLM in team namespace.

Workload: traffic.py generated chat requests with different callers and up to 64 output tokens.

Measurement period: 2026-09-13 13:00 UTC to 2026-09-13 13:30 UTC.

Instrumentation gaps: Measurements are based on a short lab workload. Longer production-like workloads are needed for stable SLO targets.

## SLI 1

Indicator: E2E request latency p95 measured from vLLM serving metrics.

Panel: E2E latency p95

Unit: seconds

Target: p95 latency < 1 second over a 30 minute window.

Window: 5 minute query window.

Observed: 0.285 seconds during traffic.py workload.

Evidence: Grafana dashboard measurement.

Why it fits: Latency affects user experience because users wait for generated responses.

Limitations: Short workload; needs longer testing.

## SLI 2
Indicator: Completed requests per minute from successful vLLM requests.


Panel: Completed requests/min

Unit: requests/min

Target: Maintain at least 20 requests/min during workload execution.

Window: 5 minute query window.

Observed: 22.7 requests/min during traffic.py workload.

Evidence: Grafana dashboard measurement.

Why it fits: Measures ability to complete user requests.

Limitations: Needs testing with different concurrency levels.