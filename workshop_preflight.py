"""Check workshop imports or print host configuration for this computer."""
import argparse
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys


def host_config(vscode: bool = False) -> dict:
    # Preserve the venv path: resolving the Unix executable symlink can bypass it.
    server = {
        'command': os.path.abspath(sys.executable),
        'args': [str(Path(__file__).resolve().parent / 'workshop/starter/mcp_server_sdk.py')],
    }
    if vscode:
        server['type'] = 'stdio'
    return {'servers' if vscode else 'mcpServers': {'mcpjam': server}}


def check(with_gui: bool = False, core_only: bool = False) -> int:
    print(f'Platform: {platform.system()} / {platform.machine()}')
    print(f'Python: {platform.python_version()} / {sys.executable}')
    failures = []
    if sys.version_info < (3, 10):
        failures.append('Python 3.10+ is required.')
    if sys.prefix == sys.base_prefix:
        failures.append('Run this check with the workshop .venv interpreter.')
    os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
    modules = ['mcp.server.fastmcp', 'pydantic', 'mido']
    if not core_only:
        modules += ['lameenc', 'numpy']
    if with_gui:
        modules += ['tkinter', 'pygame.midi']
    for module in modules:
        try:
            importlib.import_module(module)
            print(f'OK: {module}')
        except Exception as exc:
            failures.append(f'{module}: {exc}')
    try:
        version = importlib.metadata.version('mcp')
        print(f'MCP SDK: {version}')
        if version != '1.19.0':
            failures.append('Install requirements.txt: this workshop uses mcp==1.19.0.')
    except importlib.metadata.PackageNotFoundError:
        failures.append('MCP SDK is not installed.')
    if not core_only:
        try:
            from soundfont_audio import create_synth
            synth = create_synth(live=False)
            synth.delete()
            print('OK: FluidSynth and bundled soundfont (offline renderer)')
        except Exception as exc:
            failures.append(f'Audio renderer: {exc}. Run the full setup without --core-only/-CoreOnly.')
    for failure in failures:
        print(f'FIX: {failure}')
    if failures:
        return 1
    print('PASS: workshop dependencies. Next: start mcpjam in VS Code and enable its tools in Copilot chat.')
    if core_only:
        print('Core-only mode cannot generate MP3 files; full audio setup is required for this workshop.')
    print('This check does not test the AI host or an end-to-end tool call. No app window is required.')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host-config', action='store_true',
                        help='Print example host JSON with the current interpreter and server paths')
    parser.add_argument('--vscode-config', action='store_true',
                        help='Print VS Code MCP JSON with this interpreter and starter server paths')
    parser.add_argument('--with-gui', action='store_true', help='Also check optional Tk/Pygame interface dependencies')
    parser.add_argument('--core-only', action='store_true', help='Skip offline audio rendering checks (no MP3 generation)')
    args = parser.parse_args()
    if args.host_config or args.vscode_config:
        print(json.dumps(host_config(vscode=args.vscode_config), indent=2))
    else:
        raise SystemExit(check(with_gui=args.with_gui, core_only=args.core_only))
