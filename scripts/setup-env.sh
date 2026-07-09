#!/usr/bin/env bash
# Generates backend/.env from the central secrets file + this project's local defaults.
set -euo pipefail

SECRETS="$HOME/.secrets/acore.env"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "$SECRETS" ]; then
  echo "Missing $SECRETS" >&2
  exit 1
fi

cat "$SECRETS" "$ROOT/backend/.env.local.example" > "$ROOT/backend/.env"
echo "Wrote $ROOT/backend/.env"
