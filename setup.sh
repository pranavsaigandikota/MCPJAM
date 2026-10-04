#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
core_only=false
if [[ "${1:-}" == "--core-only" ]]; then core_only=true; fi
if [[ "$(uname -s)" != Darwin ]]; then
  echo 'This helper is for macOS. Use setup.ps1 on Windows.' >&2
  exit 1
fi
if ! command -v brew >/dev/null 2>&1; then
  echo 'Install Homebrew from https://brew.sh first, then run bash setup.sh again.' >&2
  echo 'Alternatively use the manual Python-with-Tk setup in MAC_SETUP.md.' >&2
  exit 1
fi
brew install python@3.13 python-tk@3.13
export HOMEBREW_PREFIX="$(brew --prefix)"
python_path="$HOMEBREW_PREFIX/opt/python@3.13/bin/python3.13"
"$python_path" -c 'import tkinter'
if [[ ! -x .venv/bin/python ]]; then "$python_path" -m venv .venv; fi
if $core_only; then
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
else
  brew install fluid-synth
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements-audio.txt
fi
.venv/bin/python workshop_preflight.py
echo 'Setup complete. App: bash run_app.sh'
echo 'Music chat: bash run_music_chat.sh'
