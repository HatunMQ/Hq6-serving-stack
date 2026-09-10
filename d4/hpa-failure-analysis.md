# HPA failure analysis

Today's CPU-based HPA fails on the real vLLM engine because the workload is GPU-bound.

CPU stays low while requests queue and GPU resources are saturated, so CPU HPA may keep one replica during overload.

The signal I would deploy instead is engine queue depth (vllm_num_requests_waiting), because it directly measures waiting requests.

I would start with a target based on acceptable queue latency and tune it by watching p95 latency and queue depth during real traffic.
