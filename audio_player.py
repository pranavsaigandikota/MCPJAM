"""Background GeneralUser GS player: no window, controlled by the music MCP tools."""
import json
import io
import socket
import sys
import threading
import time
from pathlib import Path
import pygame

from .constants import HOST, PORT
from .soundfont_audio import SOUNDFONT, create_synth


class AudioPlayer:
    def __init__(self):
        self.synth = create_synth(live=True)
        self.lock = threading.RLock()
        self.generation = 0
        self.wav_playback = False
        self.state = {'ok': True, 'audio_engine': 'generaluser_gs', 'audio_enabled': True,
                      'soundfont_path': str(SOUNDFONT), 'soundfont_error': None,
                      'playing': False, 'timeline_active': False, 'timeline_paused': False,
                      'song_position_seconds': 0, 'song_id': '', 'song_revision': 0,
                      'bpm': 112, 'swing': 8, 'muted': {}}
        self.state['player_mode'] = 'headless'

    def silence(self):
        for ch in range(16):
            self.synth.cc(ch, 120, 0)

    def command(self, cmd):
        with self.lock:
            kind = cmd.get('cmd')
            if kind == 'get_state':
                return dict(self.state)
            if kind == 'play_wav':
                path = Path(cmd['wav_path']).resolve()
                output = Path(__file__).resolve().parent / 'generated_music'
                if path.parent != output.resolve() or path.suffix != '.wav':
                    raise ValueError('Only generated project WAVs can be played')
                self.generation += 1
                self.silence()
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=44100)
                self.wav_buffer = io.BytesIO(path.read_bytes())
                pygame.mixer.music.load(self.wav_buffer, 'wav')
                pygame.mixer.music.play()
                self.wav_playback = True
                self.state.update(playing=True,timeline_active=True,timeline_paused=False,
                                  song_position_seconds=0,song_id=cmd['song_id'],song_revision=cmd['revision'],
                                  song_title=cmd['title'],song_duration_seconds=cmd['duration_seconds'],
                                  song_tracks=cmd['song_tracks'],bpm=cmd['bpm'],song_engine=cmd['song_engine'])
                threading.Thread(target=self.wav_status,args=(self.generation,),daemon=True).start()
            elif kind == 'play_midi_raw':
                if self.wav_playback:
                    pygame.mixer.music.stop()
                    self.wav_playback = False
                self.generation += 1
                self.silence()
                self.state.update(playing=True, timeline_active=True, timeline_paused=False,
                                  song_position_seconds=0, song_title=cmd.get('title', 'Music'),
                                  song_id=cmd.get('song_id', ''), song_revision=cmd.get('revision', 0),
                                  song_duration_seconds=cmd.get('duration_seconds', 0),
                                  song_tracks=cmd.get('song_tracks', {}), bpm=cmd.get('bpm', 112),
                                  articulation=cmd.get('articulation', 'legato'),
                                  song_event_count=len(cmd.get('events', [])))
                threading.Thread(target=self.play, args=(cmd['events'], self.generation), daemon=True).start()
            elif kind == 'pause':
                if self.state['timeline_active']:
                    self.state.update(timeline_paused=True, playing=False)
                    self.silence()
                    if self.wav_playback:
                        pygame.mixer.music.pause()
            elif kind == 'play':
                if self.state['timeline_active']:
                    self.state.update(timeline_paused=False, playing=True)
                    if self.wav_playback:
                        pygame.mixer.music.unpause()
            elif kind == 'stop':
                self.generation += 1
                self.silence()
                if self.wav_playback:
                    pygame.mixer.music.stop()
                    self.wav_playback = False
                self.state.update(timeline_active=False, timeline_paused=False, playing=False,
                                  song_position_seconds=0)
            else:
                return {'ok': False, 'error': 'Use the music MCP server for this background player.'}
            return {'ok': True}

    def wav_status(self, generation):
        previous = time.monotonic()
        while True:
            now = time.monotonic()
            with self.lock:
                if generation != self.generation or not self.state['timeline_active']:
                    return
                if not self.state['timeline_paused']:
                    self.state['song_position_seconds'] += now-previous
                    if not pygame.mixer.music.get_busy():
                        self.state.update(playing=False,timeline_active=False)
                        return
            previous = now
            time.sleep(.01)

    def play(self, events, generation):
        events = sorted(events, key=lambda e: e['time_sec'])
        index, position, held, paused = 0, 0.0, {}, False
        previous = time.monotonic()
        while True:
            now = time.monotonic()
            with self.lock:
                if generation != self.generation or not self.state['timeline_active']:
                    return
                if self.state['timeline_paused']:
                    paused = True
                else:
                    if paused:
                        for (ch, pitch), velocity in held.items():
                            self.synth.noteon(ch, pitch, velocity)
                        paused = False
                    else:
                        position += now - previous
                    self.state['song_position_seconds'] = round(position, 3)
                    while index < len(events) and events[index]['time_sec'] <= position:
                        event = events[index]
                        ch, kind = event['channel'], event['type']
                        if kind == 'program_change' and ch != 9:
                            self.synth.program_change(ch, event['program'])
                        elif kind == 'note_on':
                            pitch, velocity = event['note'], event['velocity']
                            self.synth.noteon(ch, pitch, velocity)
                            held[(ch, pitch)] = velocity
                        elif kind == 'note_off':
                            pitch = event['note']
                            self.synth.noteoff(ch, pitch)
                            held.pop((ch, pitch), None)
                        index += 1
                    if position >= self.state['song_duration_seconds']:
                        self.silence()
                        self.state.update(timeline_active=False, playing=False,
                                          song_position_seconds=self.state['song_duration_seconds'])
                        return
            previous = now
            time.sleep(.005)

    def connection(self, conn):
        with conn, conn.makefile('rb') as stream:
            line = stream.readline(2_000_001)
            try:
                if len(line) > 2_000_000 or not line.endswith(b'\n'):
                    raise ValueError('Invalid or oversized command')
                result = self.command(json.loads(line))
            except Exception as exc:
                result = {'ok': False, 'error': str(exc)}
            conn.sendall(json.dumps(result).encode() + b'\n')


def main():
    with socket.socket() as server:
        if sys.platform == 'win32':
            server.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        player = AudioPlayer()
        server.listen(5)
        print('GeneralUser GS audio player ready. Control playback from music chat.', flush=True)
        try:
            while True:
                conn, _ = server.accept()
                threading.Thread(target=player.connection, args=(conn,), daemon=True).start()
        finally:
            with player.lock:
                player.generation += 1
                player.silence()
                player.synth.delete()
