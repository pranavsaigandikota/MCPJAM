"""Isolated offline FluidSynth renderer (keeps native audio out of MCP workers)."""
import json
import sys

from music_arranger import read_project, render_wav

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: render_song.py SONG_ID')
    print(json.dumps(render_wav(read_project(sys.argv[1]))))
