HPA Failure Analysis
Where today's scaler fails on the real engine
The echo backend scales fine on CPU because it burns CPU per token. vLLM doesn't work like that - almost everything happens on the GPU, and the CPU barely breaks a sweat no matter how busy the engine is.
I tested this directly: hit the real engine with 32 concurrent callers and watched both numbers. CPU sat around 27% of its 4-core request. GPU was pegged at 91% utilization, ~42GB of VRAM in use, running near its power cap. So the GPU was maxed out and requests were genuinely queuing, but a CPU-based HPA at a 50% target would've looked at that 27% and decided everything's fine - it would never scale out, even in a real outage.
The signal I'd use instead
Queue depth - vllm_num_requests_waiting. It directly answers "is the engine keeping up with demand," which is the thing that actually matters for user latency. In-flight request count doesn't tell you if things are backed up or running smoothly. KV-cache utilization is a decent secondary signal for memory pressure, but it's not really about demand - it can be high just from long contexts even with an empty queue.
Starting target and what I'd tune on
I'd start scaling as soon as the queue is non-empty, rather than waiting for a backlog to build - GPU capacity is expensive and scaling late means real latency pain for users. To tune it I'd watch:
p95 latency, to check the target is actually protecting users
GPU headroom on new replicas, since more pods only help if there's GPU to give them
how often it scales up/down, since GPU pods are slow to start (model load time), so a too-twitchy HPA just pays that cold-start cost over and over
