path = "app/main.py"

with open(path, "r") as f:
    content = f.read()

replacements = [
    (
        'print(f"Loading {MODEL_ID} on CPU...")',
        'DEVICE = "cuda" if torch.cuda.is_available() else "cpu"\nprint(f"Loading {MODEL_ID} on {DEVICE}...")'
    ),
    (
        'model.to("cpu")',
        'model.to(DEVICE)'
    ),
    (
        'def _generate(\n    input_ids,\n    req: ChatCompletionRequest\n):\n    with torch.no_grad():',
        'def _generate(\n    input_ids,\n    req: ChatCompletionRequest\n):\n    input_ids = input_ids.to(DEVICE)\n    with torch.no_grad():'
    ),
]

changed = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new, 1)
        changed += 1
    else:
        print(f"WARNING: pattern not found, skipping: {old[:50]}...")

with open(path, "w") as f:
    f.write(content)

print(f"Applied {changed}/{len(replacements)} replacements to app/main.py")
