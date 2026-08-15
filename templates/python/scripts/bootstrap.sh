#!/usr/bin/env bash
set -euo pipefail

if command -v python3 >/dev/null 2>&1; then
  python3 scripts/generate_env_example.py >/dev/null
else
  echo "⚠️  python3 not found; skipping initial .env.example generation"
fi

if command -v pixi >/dev/null 2>&1; then
  echo "Generating pixi.lock..."
  pixi install >/dev/null
else
  echo "⚠️  pixi not found; run 'pixi install' to generate pixi.lock"
fi
