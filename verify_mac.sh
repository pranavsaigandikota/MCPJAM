#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ "$(uname -s)" != Darwin ]]; then
  echo 'Run this check on macOS.' >&2
  exit 1
fi
if [[ ! -x .venv/bin/python ]]; then
  echo 'Run bash setup.sh first.' >&2
  exit 1
fi
export HOMEBREW_PREFIX="$(brew --prefix)"
.venv/bin/python -c 'from mcp_server_sdk import call_daw; import socket; s=socket.socket(); s.bind(("127.0.0.1",8765)); s.close()'
python_path="$PWD/.venv/bin/python"
cd ..
"$python_path" -u -m MCPJAM --headless &
player_pid=$!
trap 'kill "$player_pid" 2>/dev/null || true; wait "$player_pid" 2>/dev/null || true' EXIT
cd MCPJAM
.venv/bin/python - <<'PY'
import time
from mcp_server_sdk import call_daw
for attempt in range(100):
    try:
        state = call_daw({'cmd': 'get_state'})
        assert state['audio_engine'] == 'generaluser_gs'
        break
    except OSError:
        time.sleep(.1)
else:
    raise RuntimeError('Background audio player did not start')
PY
.venv/bin/python verify_music.py
echo 'PASS: macOS live GS playback, timed songs, pause/resume, edits and export.'
