#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/python gemini_host.py --server mcp_server_music.py --ask-key --chat
