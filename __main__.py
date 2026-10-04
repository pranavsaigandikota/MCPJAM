"""Launch the workshop DAW with python -m MCPJAM from its parent folder."""

import sys

if '--headless' in sys.argv:
    from .audio_player import main
else:
    from .app import main

main()
