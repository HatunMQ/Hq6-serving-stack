# Capacity note (team, one page)

Fill every field from your bench_report.json. The green check reads this file and
refuses template placeholders, so replace every placeholder line with your value.

## The numbers

- Locked model: `Qwen/Qwen2.5-1.5B-Instruct-AWQ`
- Target p95 end-to-end latency (your SLO today): `3.0` seconds
- Knee concurrency (highest concurrency whose p95 is still under target): `8`
- Tokens per second at the knee: `363.5`
- Max sustainable request rate at the target p95: `3.56 req/s`

## The limiting family

One sentence, using this morning's triage lens (compute vs memory vs overhead):
which family limits this stack at the knee, and the tell that points to it.

- Not clearly compute- or memory-bound yet at this knee: throughput kept rising strongly all the way to concurrency 16 (565 tok/s, zero errors) with no sign of flattening, so the real ceiling for this model on this card sits past what this sweep covered — the stretch run to concurrency 32 is what would show which family actually caps it.

## Why the knee, not the peak

One sentence in your own words on why you report the knee at the SLO rather than
the peak throughput.

- The peak (565 tok/s at concurrency 16) came with a p95 of 3.098s, already past my 3.0s SLO, so reporting it as "capacity" would flatter the number by counting requests I'd actually be serving too slowly to promise; the knee at concurrency 8 is the highest load I can guarantee under my real latency target.
