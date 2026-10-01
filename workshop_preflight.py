"""Check workshop imports or print host configuration for this computer."""
import argparse
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys


def host_config() -> dict:
    # Preserve the venv path: resolving the Unix executable symlink can bypass it.
    return {'mcpServers': {'mcpjam': {
        'command': os.path.abspath(sys.executable),
        'args': [str(Path(__file__).resolve().with_name('mcp_server_sdk.py'))],
    }}}


def check() -> int:
    print(f'Platform: {platform.system()} / {platform.machine()}')
    print(f'Python: {platform.python_version()} / {sys.executable}')
    failures = []
    if sys.version_info < (3, 10):
        failures.append('Python 3.10+ is required.')
    if sys.prefix == sys.base_prefix:
        failures.append('Run this check with the workshop .venv interpreter.')
    os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
    for module in ['tkinter', 'mcp.server.fastmcp', 'pygame.midi', 'mido']:
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
    for failure in failures:
        print(f'FIX: {failure}')
    if failures:
        return 1
    print('PASS: workshop imports and SDK version. Next: run -m tkinter, then launch the DAW.')
    print('This check does not test the GUI, audio device, backend socket, or AI host.')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host-config', action='store_true',
                        help='Print example host JSON with the current interpreter and server paths')
    args = parser.parse_args()
    if args.host_config:
        print(json.dumps(host_config(), indent=2))
    else:
        raise SystemExit(check())
