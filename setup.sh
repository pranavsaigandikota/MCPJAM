#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
core_only=false
with_gui=false
for option in "$@"; do
  case "$option" in
    --core-only) core_only=true ;;
    --with-gui) with_gui=true ;;
    *) echo "Unknown option: $option. Use --core-only or --with-gui." >&2; exit 1 ;;
  esac
done
if [[ "$(uname -s)" != Darwin ]]; then
  echo 'This helper is for macOS. Use setup.ps1 on Windows.' >&2
  exit 1
fi
if ! command -v brew >/dev/null 2>&1; then
  echo 'Install Homebrew from https://brew.sh first, then run bash setup.sh again.' >&2
  echo 'Alternatively use the manual Python-with-Tk setup in MAC_SETUP.md.' >&2
  exit 1
fi
export HOMEBREW_PREFIX="$(brew --prefix)"
python_path=""
if ! $with_gui; then
  for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys,struct; assert (3,10) <= sys.version_info[:2] <= (3,13); assert struct.calcsize("P") == 8' >/dev/null 2>&1; then
      python_path="$(command -v "$candidate")"
      break
    fi
  done
fi
if [[ -z "$python_path" ]]; then
  if $with_gui; then brew install python@3.13 python-tk@3.13; else brew install python@3.13; fi
  python_path="$HOMEBREW_PREFIX/opt/python@3.13/bin/python3.13"
fi
if $with_gui; then "$python_path" -c 'import tkinter'; fi
if [[ ! -x .venv/bin/python ]]; then "$python_path" -m venv .venv; fi
if $core_only; then
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
else
  brew install fluid-synth
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements-audio.txt
fi
if $with_gui; then .venv/bin/python -m pip install --disable-pip-version-check -r requirements-gui.txt; fi
preflight_args=(workshop_preflight.py)
if $core_only; then preflight_args+=(--core-only); fi
if $with_gui; then preflight_args+=(--with-gui); fi
.venv/bin/python "${preflight_args[@]}"
echo 'Setup complete. Open MCPJAM in VS Code, start mcpjam, and enable its tools in Copilot agent chat.'
echo 'Find your interpreter: ./.venv/bin/python workshop_preflight.py --vscode-config'
if $with_gui; then echo 'Optional GUI: bash run_app.sh'; fi
