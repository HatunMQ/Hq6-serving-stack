Serving is guaranteed and allowed to burst, dashboard is best-effort for small refresh spikes, and batch throttles first when CPU is under contention.

Serving
resources:
  requests:
    cpu: "2"
  limits:
    cpu: "2"
Batch
resources:
  requests:
    cpu: "500m"
  limits:
    cpu: "1"
Dashboard
resources: {}

Batch throttles first because our Step 4 measurements showed p95 latency of 8ms with an unlimited neighbour versus 17ms with the 500m-limited neighbour, demonstrating that CPU contention affects serving latency.