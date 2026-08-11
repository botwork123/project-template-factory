#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 3 ]; then
  echo "Usage: $0 <url> [attempts] [interval-seconds]" >&2
  exit 2
fi

url="$1"
attempts="${2:-60}"
interval="${3:-2}"

for _ in $(seq 1 "$attempts"); do
  if curl --fail --silent --show-error "$url" >/dev/null; then
    exit 0
  fi
  sleep "$interval"
done

echo "Timed out waiting for $url" >&2
exit 1
