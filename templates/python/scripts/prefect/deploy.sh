#!/usr/bin/env bash
set -euo pipefail

# Minimal optional helper for image-based Prefect deploys.
# Local development does not require Prefect.

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <image-tag> [deployment-name]"
  echo "Example: $0 sha-abc123 app"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
  echo "python runtime not found in PATH. Install Python 3 to run deploys."
  exit 1
fi

if ! command -v prefect >/dev/null 2>&1; then
  echo "prefect CLI not found. Install it to run deploys."
  exit 1
fi

IMAGE_TAG="$1"
DEPLOYMENT_NAME="${2:-app}"
export IMAGE_TAG

prefect deploy --prefect-file prefect.yaml --name "$DEPLOYMENT_NAME"
