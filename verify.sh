#!/usr/bin/env bash
set -euo pipefail

TARGET_MB=300
MIN_SAVINGS_PCT=20
CONTAINER_NAME=registry-verify
PORT=8000

echo "checking images exist..."
docker image inspect registry:naive >/dev/null 2>&1 || { echo "GREEN CHECK: FAIL (registry:naive not found)"; exit 1; }
docker image inspect registry:multistage >/dev/null 2>&1 || { echo "GREEN CHECK: FAIL (registry:multistage not found)"; exit 1; }

naive_size=$(docker images registry:naive --format "{{.Size}}")
multi_size=$(docker images registry:multistage --format "{{.Size}}")

result=$(python3 - "$naive_size" "$multi_size" "$TARGET_MB" "$MIN_SAVINGS_PCT" << 'PYEOF'
import sys

def parse_size_to_mb(size_str):
    size_str = size_str.strip()
    if size_str.endswith("GB"):
        return float(size_str[:-2]) * 1024
    if size_str.endswith("MB"):
        return float(size_str[:-2])
    if size_str.endswith("kB"):
        return float(size_str[:-2]) / 1024
    if size_str.endswith("B"):
        return float(size_str[:-1]) / (1024 * 1024)
    raise ValueError(f"unrecognized size format: {size_str}")

naive_str, multi_str = sys.argv[1], sys.argv[2]
target_mb, min_savings = float(sys.argv[3]), float(sys.argv[4])

naive_mb = parse_size_to_mb(naive_str)
multi_mb = parse_size_to_mb(multi_str)
savings_pct = ((naive_mb - multi_mb) / naive_mb) * 100 if naive_mb > 0 else 0

ok = multi_mb <= target_mb and savings_pct >= min_savings
print(f"{multi_mb:.1f} {savings_pct:.1f} {1 if ok else 0}")
PYEOF
)

multi_mb=$(echo "$result" | awk '{print $1}')
savings_pct=$(echo "$result" | awk '{print $2}')
size_ok=$(echo "$result" | awk '{print $3}')

echo "multi-stage size: ${multi_mb} MB"
echo "savings: ${savings_pct}%"

if [ "$size_ok" != "1" ]; then
  echo "GREEN CHECK: FAIL (size/savings requirement not met)"
  exit 1
fi

echo "starting container..."
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER_NAME" -p "$PORT:8000" registry:multistage >/dev/null

cleanup() {
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "waiting for /health..."
for i in $(seq 1 30); do
  if curl -sf "http://localhost:$PORT/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

health_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/health")
registry_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/registry")
lookup_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/registry/Qwen2.5-0.5B-Instruct")
notfound_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/registry/does-not-exist")

echo "health: $health_status"
echo "registry: $registry_status"
echo "model lookup: $lookup_status"
echo "unknown model: $notfound_status"

if [ "$health_status" != "200" ] || [ "$registry_status" != "200" ] || [ "$lookup_status" != "200" ] || [ "$notfound_status" != "404" ]; then
  echo "GREEN CHECK: FAIL (endpoint check failed)"
  exit 1
fi

echo "GREEN CHECK: PASS"
