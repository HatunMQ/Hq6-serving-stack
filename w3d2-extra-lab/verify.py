#!/usr/bin/env python3
# Green check for the extra W3D2 lab (the paged KV allocator).
# Run next to kv_sim_report.json:  python verify.py
# Prints exactly one line last: GREEN CHECK: PASS  or  GREEN CHECK: FAIL (<reason>)
# stdlib only. The lab is fully deterministic (random.seed(7)), so this
# verifier recomputes the workload and both simulations with its own reference
# implementation and demands an exact match.
import json, os, random
from typing import NoReturn

KB_PER_TOKEN = 2 * 28 * 2 * 128 * 2 / 1024   # layers 28, kv_heads 2, head_dim 128, fp16
BLOCK_TOKENS = 16
BLOCK_KB = BLOCK_TOKENS * KB_PER_TOKEN
MAX_LEN = 4096
BUDGET_KB = 2 * 1024 * 1024
MIN_ADVANTAGE = 1.5


class _Stop(Exception):
    pass


def _fail(reason) -> NoReturn:
    print("GREEN CHECK: FAIL (%s)" % reason)
    raise _Stop()


def make_workload(n_sequences=60, max_len=MAX_LEN):
    random.seed(7)
    lengths = []
    for _ in range(n_sequences):
        if random.random() < 0.85:
            lengths.append(random.randint(50, 400))
        else:
            lengths.append(random.randint(2000, max_len))
    return lengths


def simulate_slab(budget_kb, workload):
    used, admitted, rejected = 0.0, 0, 0
    need = MAX_LEN * KB_PER_TOKEN
    for _ in workload:
        if used + need <= budget_kb:
            used += need
            admitted += 1
        else:
            rejected += 1
    return {"peak_concurrent": admitted, "admitted": admitted, "rejected": rejected}


def simulate_blockpool(budget_kb, workload):
    total_blocks = int(budget_kb // BLOCK_KB)
    free = total_blocks
    admitted = rejected = 0
    for length in workload:
        needed = -(-length // BLOCK_TOKENS)
        if needed < 1:
            needed = 1
        if free >= needed:
            free -= needed
            admitted += 1
        else:
            rejected += 1
    return {"peak_concurrent": admitted, "admitted": admitted, "rejected": rejected}


def check_block(name, got, want):
    for key in ("peak_concurrent", "admitted", "rejected"):
        if got.get(key) != want[key]:
            _fail("%s %s=%r, reference computes %r (deterministic seed; the "
                  "difference is in your allocator or simulation)"
                  % (name, key, got.get(key), want[key]))


def main():
    if not os.path.isfile("kv_sim_report.json"):
        _fail("kv_sim_report.json not found; run Step 6 first")
    try:
        with open("kv_sim_report.json") as f:
            r = json.load(f)
    except json.JSONDecodeError as e:
        _fail("kv_sim_report.json is not valid JSON: %s" % e)

    for key in ("kb_per_token", "block_tokens", "budget_kb", "slab",
                "blockpool", "blockpool_advantage"):
        if key not in r:
            _fail("missing key '%s'" % key)
    if abs(r["kb_per_token"] - KB_PER_TOKEN) > 0.01:
        _fail("kb_per_token=%r, the Qwen2.5-1.5B formula gives %.2f"
              % (r["kb_per_token"], KB_PER_TOKEN))
    if r["block_tokens"] != BLOCK_TOKENS:
        _fail("block_tokens=%r, the lab fixes 16" % r["block_tokens"])
    if r["budget_kb"] != BUDGET_KB:
        _fail("budget_kb=%r, the lab fixes 2 GB (%d KB) so the slab binds"
              % (r["budget_kb"], BUDGET_KB))

    workload = make_workload()
    want_slab = simulate_slab(BUDGET_KB, workload)
    want_pool = simulate_blockpool(BUDGET_KB, workload)
    check_block("slab", r["slab"], want_slab)
    check_block("blockpool", r["blockpool"], want_pool)

    want_adv = round(want_pool["peak_concurrent"] / want_slab["peak_concurrent"], 2)
    if abs(r["blockpool_advantage"] - want_adv) > 0.01:
        _fail("blockpool_advantage=%r, reference computes %s"
              % (r["blockpool_advantage"], want_adv))
    if want_adv < MIN_ADVANTAGE:
        _fail("verifier bug: reference advantage %.2f under the %.1fx bar"
              % (want_adv, MIN_ADVANTAGE))

    print("reference: slab %d resident, block-pool %d resident, advantage %.2fx"
          % (want_slab["peak_concurrent"], want_pool["peak_concurrent"], want_adv))
    print("GREEN CHECK: PASS")


if __name__ == "__main__":
    try:
        main()
    except _Stop:
        raise SystemExit(1)
