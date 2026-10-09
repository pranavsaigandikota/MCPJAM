"""Isolated offline FluidSynth renderer (keeps native audio out of MCP workers)."""
import json
import sys
import faulthandler

from music_arranger import read_project, render_wav

if __name__ == '__main__':
    faulthandler.dump_traceback_later(45, exit=True)
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] != '--mp3'):
        raise SystemExit('Usage: render_song.py SONG_ID [--mp3]')
    rendered = render_wav(read_project(sys.argv[1]))
    if '--mp3' in sys.argv:
        from mp3_audio import encode_mp3
        rendered.update(encode_mp3(rendered.pop('wav_path')))
    print(json.dumps(rendered))
    faulthandler.cancel_dump_traceback_later()
