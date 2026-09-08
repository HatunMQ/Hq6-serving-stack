# Policy: three tenants on a 4-CPU node

## The sentence
Serving is guaranteed a fixed floor sized to the burst we measured; dashboard
bursts freely off whatever capacity is left over with no guarantee at all;
batch throttles first, because its limit sits close to its own low request,
so it is squeezed the moment the node gets tight.

## The resources block per tenant

serving:
  resources:
    requests:
      cpu: "1"
      memory: 2Gi
    limits:
      cpu: "1"
      memory: 2Gi

batch:
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 512Mi

dashboard:
  # no resources block at all - BestEffort on purpose

## Defending the loser (batch)
Batch throttling first costs nothing today's users can feel: our own probe
measured serving's p95 at 8ms with twenty unbounded competing loops and 12ms
with those loops capped at 500m each - both numbers came entirely from the
request Step 1 gave serving, not from batch getting extra room. Batch has no
deadline, so trading its throughput for serving's latency is the correct and
cheap trade.
