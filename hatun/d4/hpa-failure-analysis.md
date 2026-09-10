# HPA Failure Analysis

## Where today's scaler fails
Today's HPA watches CPU utilization, which works for the echo backend because
it is CPU-bound (each request spends real CPU cycles). But the team's vLLM
engine is GPU-bound: under a 32-worker load that pushed GPU utilization to
85% (41.8GB/49GB VRAM in use), the engine's CPU usage stayed at 17m against
a 4-CPU (4000m) request — well under 1%. An HPA targeting 50% CPU would read
roughly 0.4%/50% and never scale, holding one replica through an outage where
the engine is actually saturated and the request queue is filling up.

## The signal I'd deploy instead
I would use `vllm_num_requests_waiting` (vLLM's queue-depth metric). It
directly measures whether the engine is falling behind: a growing wait
queue means incoming requests are arriving faster than the engine can
serve them, regardless of how busy the GPU compute happens to look at any
given instant. This maps conceptually to what CPU% was meant to measure on
the echo backend (system load relative to capacity), but on the actual
bottleneck resource for vLLM (throughput/scheduling), not an unrelated one
(CPU). It's also simpler to reason about than KV-cache utilization, which
can spike from long-context requests rather than request volume.

## Target number and what to tune by
I'd start with a target of around 5 waiting requests per replica as the
scale-out trigger — low enough to react before users notice added latency,
high enough to avoid scaling on normal queueing noise. While tuning, I'd
watch end-to-end request latency (p95) and GPU utilization together: if
p95 climbs while waiting-requests stays under target, the target is set
too high; if replicas scale out while GPU utilization is still low, the
target is too aggressive and I'm paying for capacity I don't need.