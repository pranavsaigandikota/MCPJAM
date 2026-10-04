#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$(dirname "$repo_dir")"
exec "$repo_dir/.venv/bin/python" -m MCPJAM
