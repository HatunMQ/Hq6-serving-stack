# Model lock (team record)

Fill every field. This is your team's record of the model you serve for the rest
of the course. The green check reads this file and refuses template placeholders,
so replace every placeholder line with your real value.

## The locked model

- Model id: `Qwen/Qwen2.5-1.5B-Instruct-AWQ`
- Quantisation: `awq`
- Why this one: Passed the smoke test 10/10, identical to fp16's score, while using 4-bit weights that free up GPU memory for more KV-cache capacity.

## The launch flags

The exact vLLM flags your team runs. Copy them from the SERVER_ARGS you launched
with.

```
--model Qwen/Qwen2.5-1.5B-Instruct-AWQ --dtype half --max-model-len 4096 \
--gpu-memory-utilization 0.85 \
--quantization awq --enable-auto-tool-choice --tool-call-parser hermes
```

- Tool-call parser: `hermes`

## The smoke score

- Score (valid behaviours out of 10): `10`
- Distractor stayed call-free in the majority: `yes`
- Passed the gate (>= 8/10 and distractor majority clean): `yes`
- Measured against: both — AWQ scored 10/10, fp16 scored 10/10

## Quality spot check note

- The AWQ build held up well against fp16 across all five prompts; no obvious degradation in coherence, formatting, or content quality was observed between the two.
