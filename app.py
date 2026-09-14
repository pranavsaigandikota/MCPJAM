import json
import queue
import random
import socket
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
import pygame.midi

from .constants import HOST, PORT, STEPS, TRACKS, TRACK_PILLARS, COLORS, TRACK_LABELS, BASS_FREQS
from .presets import DYNAMIC_LEVELS, ITALIAN_EXPRESSIONS, GENRE_PRESETS
from .synth import AUDIO_ENABLED, HighFiSynthesizer, parse_chord_frequencies, parse_note_frequency

class BeatBoxStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("MCPJAM Studio — AI Music Production & Dynamic DAW")
        self.root.geometry("1020x800")
        self.root.minsize(980, 740)
        self.root.configure(bg="#17181c")

        # Playback & Production State
        self.bpm = 118
        self.swing = 10
        self.playing = True
        self.metronome = False
        self.master_volume = 0.85
        self.dj_filter = 100
        self.step_i = 0
        self.cmd_queue = queue.Queue()
        self.mcp_command_count = 0

        # Italian Orchestral Expression & Dynamics State
        self.active_expression = "espressivo"
        self.dynamic_level = "mf"
        self.articulation = "legato"

        self.track_volumes = {t: 0.9 for t in TRACKS}
        self.track_muted = {t: False for t in TRACKS}
        self.track_solo = {t: False for t in TRACKS}
        self.pattern = {t: [0] * STEPS for t in TRACKS}

        # Dynamic Chord Progression State (16 steps mapping)
        self.chord_progression = ["Am", "F", "C", "G"]
        self.step_chords = ["Am"] * 4 + ["F"] * 4 + ["C"] * 4 + ["G"] * 4
        self.song_ref_text = "Pop 4-Chords (Am - F - C - G)"
        self.last_active_chord_idx = -1

        # Lead melody notes per step
        self.step_lead_notes = [""] * STEPS
        self.current_lead_note = "E5"
        self.active_genre = "pop"

        # Audio Sound Caches
        self.drum_sounds = {}
        self.bass_sounds = {}
        self.lead_sounds = {}
        self.chord_cache = {}
        self.pad_cache = {}
        self.bowed_string_cache = {}
        self.timpani_sound = None

        # Hybrid MIDI Engine
        self.midi_out = None
        self._init_midi()

        self._init_core_sounds()
        self._load_genre("pop", silent=True)

        # Build UI
        self._build_ui()

        # Start Playback Thread & Socket Server
        self.running = True
        self.seq_thread = threading.Thread(target=self._sequencer_loop, daemon=True)
        self.seq_thread.start()

        self._start_socket_server()
        self.root.after(30, self._poll_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_midi(self):
        try:
            import pygame
            pygame.init()
            pygame.midi.init()
            # -------------------------------------------------
            # Prefer GeneralUser‑GS bundled soundfont if it exists
            # -------------------------------------------------
            import pathlib
            local_sf2 = pathlib.Path(__file__).parents[1] / "GeneralUser-GS" / "GeneralUser-GS.sf2"
            if local_sf2.is_file():
                try:
                    import fluidsynth
                    self.fs = fluidsynth.Synth()
                    import sys
                    driver = "dsound" if sys.platform == "win32" else ("coreaudio" if sys.platform == "darwin" else "pulseaudio")
                    self.fs.start(driver=driver)
                    sfid = self.fs.sfload(str(local_sf2))
                    # Select program 0 (default preset) on channel 0
                    self.fs.program_select(0, sfid, 0, 0)
                    class FluidSynthWrapper:
                        def __init__(self, fs):
                            self.fs = fs
                        def note_on(self, pitch, velocity, channel=0):
                            self.fs.noteon(channel, pitch, velocity)
                        def note_off(self, pitch, velocity=0, channel=0):
                            self.fs.noteoff(channel, pitch)
                        def set_instrument(self, instrument_id, channel=0):
                            self.fs.program_change(channel, instrument_id)
                        def close(self):
                            self.fs.delete()
                    self.midi_out = FluidSynthWrapper(self.fs)
                    print(f"[BeatBox] Loaded GeneralUser‑GS soundfont from {local_sf2}")
                    return
                except Exception as fe:
                    print(f"[BeatBox] FluidSynth load failed: {fe}")
            # Fallback: use default MIDI output
            port = pygame.midi.get_default_output_id()
            if port != -1:
                self.midi_out = pygame.midi.Output(port, 0)
                print(f"[BeatBox] Initialized default MIDI output on port {port}")
            else:
                print("[BeatBox] No default MIDI output port found.")
        except Exception as e:
            print(f"[BeatBox] Failed to initialize MIDI: {e}")

    def _schedule_midi_note_off(self, channel, pitch, delay_sec):
        def turn_off():
            time.sleep(delay_sec)
            if self.midi_out:
                self.midi_out.note_off(pitch, 127, channel)
        threading.Thread(target=turn_off, daemon=True).start()

    # -------------------------------------------------------------------------
    # Comprehensive General MIDI instrument map (0-indexed GM program numbers)
    # Covers all genres. Each entry: (keys_prog, lead_prog, pad_prog, bass_prog)
    # GM Program reference (0-based):
    #   0=Grand Piano, 4=EP1, 5=EP2, 11=Vibraphone, 19=Church Organ
    #   24=Nylon Guitar, 25=Steel Guitar, 29=Overdriven Guitar, 30=Distortion Guitar
    #   32=Acoustic Bass, 33=Fingered Bass, 34=Picked Bass, 35=Fretless Bass
    #   36=Slap Bass 1, 38=Synth Bass 1, 39=Synth Bass 2
    #   40=Violin, 42=Cello, 44=Tremolo Strings, 48=String Ensemble 1
    #   49=String Ensemble 2, 50=Synth Strings 1, 52=Choir Aahs, 56=Trumpet
    #   57=Trombone, 60=French Horn, 65=Alto Sax, 66=Tenor Sax
    #   73=Flute, 80=Square Lead, 81=Sawtooth Lead, 82=Calliope Lead
    #   84=Chiff Lead, 88=New Age Pad, 89=Warm Pad, 90=Polysynth Pad
    #   91=Choir Pad, 92=Bowed Pad, 95=Halo Pad
    # -------------------------------------------------------------------------
    GM_GENRE_MAP = {
        # genre:         (keys,  lead,  pad,   bass)
        "pop":          (4,     81,    89,    38),   # EP2, Sawtooth Lead, Warm Pad, Synth Bass 1
        "synthpop":     (4,     80,    90,    38),   # EP2, Square Lead, Polysynth Pad, Synth Bass 1
        "lofi":         (5,     11,    88,    33),   # EP2, Vibraphone, New Age Pad, Fingered Bass
        "rnb":          (4,     66,    52,    36),   # EP2, Tenor Sax, Choir Aahs, Slap Bass 1
        "soul":         (19,    52,    91,    33),   # Church Organ, Choir Aahs, Choir Pad, Fingered Bass
        "jazz":         (4,     65,    88,    35),   # EP2, Alto Sax, New Age Pad, Fretless Bass
        "bolero":       (24,    56,    48,    32),   # Nylon Guitar, Trumpet, String Ensemble, Acoustic Bass
        "latin":        (24,    56,    48,    32),   # Nylon Guitar, Trumpet, String Ensemble, Acoustic Bass
        "orchestra":    (0,     40,    49,    42),   # Grand Piano, Violin, String Ensemble 2, Cello
        "cinematic":    (0,     44,    95,    42),   # Grand Piano, Tremolo Strings, Halo Pad, Cello
        "slowballad":   (0,     40,    92,    32),   # Grand Piano, Violin, Bowed Pad, Acoustic Bass
        "rock":         (19,    29,    50,    34),   # Church Organ, Overdriven Guitar, Synth Strings, Picked Bass
        "edm":          (4,     81,    90,    39),   # EP2, Sawtooth Lead, Polysynth Pad, Synth Bass 2
        "trap":         (4,     82,    90,    39),   # EP2, Calliope Lead, Polysynth Pad, Synth Bass 2
        "gospel":       (19,    52,    91,    33),   # Church Organ, Choir, Choir Pad, Fingered Bass
        "flamenco":     (24,    73,    92,    32),   # Nylon Guitar, Flute, Bowed Pad, Acoustic Bass
    }

    # GM drum note map per track name
    GM_DRUM_MAP = {
        "kick":  {"default": 36, "orchestra": 36, "jazz": 35, "rock": 36},  # 36=Bass Drum 1, 35=Acoustic Bass Drum
        "snare": {"default": 38, "jazz": 40, "rock": 38},                   # 38=Acoustic Snare, 40=Electric Snare
        "hihat": {"default": 42, "open": 46},                               # 42=Closed HH, 46=Open HH
        "clap":  {"default": 39, "edm": 39, "synthpop": 39},               # 39=Hand Clap
        "ride":  {"default": 51},                                            # 51=Ride Cymbal
        "crash": {"default": 49},                                            # 49=Crash Cymbal
        "tom":   {"default": 47},                                            # 47=Low-Mid Tom
    }

    def _trigger_midi_sound(self, track, active_chord, override_note, step_num, override_program=None):
        import math
        genre = getattr(self, "active_genre", "pop")
        gm = self.GM_GENRE_MAP.get(genre, self.GM_GENRE_MAP["pop"])
        keys_prog, lead_prog, pad_prog, bass_prog = gm

        vol = int(min(1.0, max(0.0, self.master_volume * self.track_volumes.get(track, 1.0))) * 127)
        if vol == 0:
            return

        beat_sec = max(0.1, 60.0 / max(40, self.bpm))

        # ── Drums ──────────────────────────────────────────────────────────────
        drum_note_map = self.GM_DRUM_MAP.get(track)
        if drum_note_map is not None:
            pitch = drum_note_map.get(genre, drum_note_map.get("default", 36))
            # Orchestra: route kick to timpani on ch4
            if track == "kick" and genre in ("orchestra", "cinematic"):
                self.midi_out.set_instrument(47, 4)  # Timpani on ch 4
                self.midi_out.note_on(48, vol, 4)    # Low Timpani pitch
                self._schedule_midi_note_off(4, 48, beat_sec * 0.6)
            else:
                self.midi_out.note_on(pitch, vol, 9)
                self._schedule_midi_note_off(9, pitch, min(0.3, beat_sec * 0.5))
            return

        # ── Keys ───────────────────────────────────────────────────────────────
        if track == "keys":
            ch = 0
            prog = override_program if override_program is not None else keys_prog
            self.midi_out.set_instrument(prog, ch)
            try:
                _, _, freqs, _ = parse_chord_frequencies(active_chord)
                for f in freqs:
                    p = int(round(69 + 12 * math.log2(f / 440.0)))
                    p = max(21, min(108, p))  # clamp to piano range
                    self.midi_out.note_on(p, vol, ch)
                    self._schedule_midi_note_off(ch, p, beat_sec * 0.9)
            except Exception:
                pass
            return

        # ── Pad ────────────────────────────────────────────────────────────────
        if track == "pad":
            ch = 2
            prog = override_program if override_program is not None else pad_prog
            self.midi_out.set_instrument(prog, ch)
            try:
                _, _, freqs, _ = parse_chord_frequencies(active_chord)
                for f in freqs:
                    p = int(round(69 + 12 * math.log2(f / 440.0)))
                    p = max(21, min(108, p))
                    self.midi_out.note_on(p, max(40, vol - 30), ch)  # pads slightly quieter
                    self._schedule_midi_note_off(ch, p, beat_sec * 1.5)  # pads hold longer
            except Exception:
                pass
            return

        # ── Lead ───────────────────────────────────────────────────────────────
        if track == "lead":
            ch = 1
            prog = override_program if override_program is not None else lead_prog
            self.midi_out.set_instrument(prog, ch)
            active_note = override_note or (self.step_lead_notes[step_num % len(self.step_lead_notes)] if self.step_lead_notes else "")
            if not active_note:
                active_note = self.current_lead_note
            try:
                f = parse_note_frequency(active_note)
                p = int(round(69 + 12 * math.log2(f / 440.0)))
                p = max(21, min(108, p))
                self.midi_out.note_on(p, vol, ch)
                self._schedule_midi_note_off(ch, p, beat_sec * 0.6)
            except Exception:
                pass
            return

        # ── Bass ───────────────────────────────────────────────────────────────
        if track == "bass":
            ch = 3
            prog = override_program if override_program is not None else bass_prog
            self.midi_out.set_instrument(prog, ch)
            try:
                _, _, _, bass_note = parse_chord_frequencies(active_chord)
                f = BASS_FREQS.get(bass_note, 55.0)
                p = int(round(69 + 12 * math.log2(f / 440.0)))
                p = max(24, min(60, p))  # keep bass in low register
                self.midi_out.note_on(p, vol, ch)
                self._schedule_midi_note_off(ch, p, beat_sec * 0.85)
            except Exception:
                pass
            return


    def _init_core_sounds(self):
        if not AUDIO_ENABLED:
            return
        try:
            self.timpani_sound = HighFiSynthesizer.generate_timpani(73.41, dynamic="mf")
            self.drum_sounds = {
                "kick":  HighFiSynthesizer.generate_kick(),
                "snare": HighFiSynthesizer.generate_snare(),
                "hihat": HighFiSynthesizer.generate_hihat_closed(),
                "clap":  HighFiSynthesizer.generate_clap(),
            }
            # Pre-generate 12 chromatic sub bass notes
            for note, freq in BASS_FREQS.items():
                self.bass_sounds[note] = HighFiSynthesizer.generate_bass_note(freq)

            # Pre-generate initial lead hook notes
            synth_type = self._get_lead_type_for_genre(getattr(self, "active_genre", "pop"))
            for note in ["C4", "D4", "Eb4", "E4", "F4", "F#4", "G4", "Ab4", "A4", "Bb4", "B4",
                         "C5", "C#5", "D5", "Eb5", "E5", "F5", "F#5", "G5", "Ab5", "A5", "Bb5", "B5", "C6"]:
                f = parse_note_frequency(note)
                self.lead_sounds[note] = HighFiSynthesizer.generate_synth_lead(f, synth_type)
        except Exception as e:
            print(f"[MCPJAM] Core sounds initialization warning: {e}")

    def get_or_create_chord_sound(self, chord_name, for_pad=False):
        """Dynamically retrieve or synthesize on-the-fly any chord sound."""
        if not AUDIO_ENABLED:
            return None
        cache = self.pad_cache if for_pad else self.chord_cache
        clean = chord_name.strip().upper()
        if clean in cache:
            return cache[clean]

        try:
            root, quality, freqs, bass_note = parse_chord_frequencies(clean)
            if for_pad:
                if getattr(self, "active_genre", "pop") == "bolero":
                    snd = HighFiSynthesizer.generate_mariachi_brass_chord(freqs)
                else:
                    snd = HighFiSynthesizer.generate_synth_pad(freqs)
            else:
                if getattr(self, "active_genre", "pop") == "bolero":
                    snd = HighFiSynthesizer.generate_nylon_guitar_chord(freqs)
                else:
                    snd = HighFiSynthesizer.generate_rhodes_chord(freqs)
            cache[clean] = snd
            return snd
        except Exception as e:
            print(f"[MCPJAM] Could not synthesize chord '{chord_name}': {e}")
            return None

    def get_or_create_orchestral_strings_sound(self, chord_name):
        """Retrieve or synthesize polyphonic bowed string ensemble for the chord."""
        if not AUDIO_ENABLED:
            return None
        clean = chord_name.strip().upper()
        key = (clean, self.articulation, self.dynamic_level)
        if key in self.bowed_string_cache:
            return self.bowed_string_cache[key]
        try:
            _, _, freqs, _ = parse_chord_frequencies(clean)
            snd = HighFiSynthesizer.generate_bowed_string_chord(
                freqs, articulation=self.articulation, dynamic=self.dynamic_level
            )
            self.bowed_string_cache[key] = snd
            return snd
        except Exception as e:
            print(f"[MCPJAM] Could not synthesize string section '{chord_name}': {e}")
            return self.get_or_create_chord_sound(clean, for_pad=True)

    def get_or_create_bowed_lead_sound(self, note_name):
        """Retrieve or synthesize physical modeled bowed string solo instrument with vibrato."""
        if not AUDIO_ENABLED:
            return None
        clean = note_name.strip().upper()
        key = (clean, self.articulation, self.dynamic_level)
        if key in self.bowed_string_cache:
            return self.bowed_string_cache[key]
        try:
            freq = parse_note_frequency(clean)
            snd = HighFiSynthesizer.generate_bowed_string(
                freq, duration=0.7, articulation=self.articulation, dynamic=self.dynamic_level
            )
            self.bowed_string_cache[key] = snd
            return snd
        except Exception as e:
            print(f"[MCPJAM] Could not synthesize bowed lead '{note_name}': {e}")
            return self.get_or_create_lead_sound(clean)

    def apply_expression_internal(self, expr_name: str, dynamic_name: str = "mf", apply_progression: bool = True):
        """Apply any Italian musical expression mark and dynamic level."""
        clean_expr = expr_name.strip().lower().replace("_", " ")
        clean_dyn = dynamic_name.strip().lower()
        if clean_dyn not in DYNAMIC_LEVELS:
            clean_dyn = "mf"
        self.dynamic_level = clean_dyn

        expr_data = ITALIAN_EXPRESSIONS.get(clean_expr)
        if not expr_data:
            for k, v in ITALIAN_EXPRESSIONS.items():
                if k in clean_expr or clean_expr in k:
                    expr_data = v
                    clean_expr = k
                    break

        if expr_data:
            self.active_expression = clean_expr
            self.articulation = expr_data.get("articulation", self.articulation)
            self.set_bpm(expr_data.get("bpm", self.bpm))
            self.swing = expr_data.get("swing", self.swing)
            self.dj_filter = expr_data.get("filter", self.dj_filter)
            self.scale_swing.set(self.swing)
            self.lbl_swing_val.configure(text=f"{self.swing}%")
            self.scale_filter.set(self.dj_filter)

            if apply_progression and "chords" in expr_data:
                self.set_chord_progression_internal(
                    expr_data["chords"],
                    f"{expr_data['term']} ({expr_data['desc']})"
                )
            if "lead" in expr_data:
                self.set_melody_internal(expr_data["lead"])
        else:
            self.active_expression = clean_expr

        dyn_info = DYNAMIC_LEVELS.get(clean_dyn, DYNAMIC_LEVELS["mf"])
        self.master_volume = dyn_info["volume"]
        self.scale_master.set(int(self.master_volume * 100))

        # Clear bowed string cache so new articulation & dynamics apply immediately
        self.bowed_string_cache.clear()

        self._update_expr_hud_ui()
        term_title = expr_data["term"].upper() if expr_data else clean_expr.upper()
        desc_txt = expr_data["desc"] if expr_data else dyn_info["label"]
        self.ai_action_banner.configure(
            text=f"AI PRODUCER: Expression {term_title} [{clean_dyn.upper()}] ({desc_txt})"
        )

    def _update_expr_hud_ui(self):
        if hasattr(self, "lbl_expr_hud"):
            self.lbl_expr_hud.configure(
                text=f"EXPR: {self.active_expression.upper()} [{self.dynamic_level.upper()}] · {self.articulation.upper()}"
            )

    def get_or_create_lead_sound(self, note_name):
        """Dynamically retrieve or synthesize any synth lead note."""
        if not AUDIO_ENABLED:
            return None
        clean = note_name.strip().upper()
        if clean in self.lead_sounds:
            return self.lead_sounds[clean]
        try:
            freq = parse_note_frequency(clean)
            synth_type = self._get_lead_type_for_genre(getattr(self, "active_genre", "pop"))
            snd = HighFiSynthesizer.generate_synth_lead(freq, synth_type)
            self.lead_sounds[clean] = snd
            return snd
        except Exception as e:
            print(f"[MCPJAM] Could not synthesize lead note '{note_name}': {e}")
            return self.lead_sounds.get("E5")

    def set_chord_progression_internal(self, chords_list, song_ref=""):
        """Map a list of chord names across the 16 steps."""
        if not chords_list:
            return
        self.chord_progression = [c.strip() for c in chords_list if c.strip()]
        n = len(self.chord_progression)
        steps_per_chord = max(1, STEPS // n)
        new_step_chords = []
        for i in range(STEPS):
            idx = min(n - 1, i // steps_per_chord)
            new_step_chords.append(self.chord_progression[idx])
        self.step_chords = new_step_chords

        if song_ref:
            self.song_ref_text = song_ref
        else:
            self.song_ref_text = " ➔ ".join(self.chord_progression)

        # Pre-synthesize the chords in background thread
        def _precache_chords():
            for ch in self.chord_progression:
                self.get_or_create_chord_sound(ch, for_pad=False)
                self.get_or_create_chord_sound(ch, for_pad=True)
        threading.Thread(target=_precache_chords, daemon=True).start()

        self._update_chord_hud_ui()

    def set_melody_internal(self, notes_list):
        """Set custom lead melody notes across 16 steps."""
        if isinstance(notes_list, list):
            self.step_lead_notes = (list(notes_list) + [""] * STEPS)[:STEPS]
            def _precache_lead():
                for n in self.step_lead_notes:
                    if n:
                        self.get_or_create_lead_sound(n)
            threading.Thread(target=_precache_lead, daemon=True).start()

    GENRE_ALIASES = {
        "mariokart": "jfusion",
        "mario kart": "jfusion",
        "mario_kart": "jfusion",
        "jazzfusion": "jfusion",
        "jazz fusion": "jfusion",
        "j-fusion": "jfusion",
        "jfusion": "jfusion",
        "casiopea": "jfusion",
        "t-square": "jfusion",
        "anirudh": "anirudh",
        "masstrap": "anirudh",
        "mass": "anirudh",
        "kuthu": "anirudh",
        "southtrap": "anirudh",
        "tamil": "anirudh",
        "indian": "anirudh",
        "rock": "heavyrock",
        "heavyrock": "heavyrock",
        "hardrock": "heavyrock",
        "grunge": "heavyrock",
        "metal": "heavyrock",
        "powerchords": "heavyrock",
        "edm": "electronic",
        "electronic": "electronic",
        "ukbass": "electronic",
        "techno": "electronic",
        "dubstep": "electronic",
        "dnb": "electronic",
        "drum and bass": "electronic",
        "house": "electronic",
        "slow": "slowballad",
        "slowballad": "slowballad",
        "slowmusic": "slowballad",
        "neosoul": "slowballad",
        "neo-soul": "slowballad",
        "ballad": "slowballad",
        "soul": "slowballad",
        "hip-hop": "anirudh",
        "hiphop": "anirudh",
        "trap": "anirudh",
        "lo-fi": "lofi",
        "orchestra": "orchestra",
        "orchestral": "orchestra",
        "symphony": "orchestra",
        "symphonic": "orchestra",
        "classical": "orchestra",
        "strings": "orchestra",
        "bowedstrings": "orchestra",
        "cinematic": "cinematic",
        "filmscore": "cinematic",
        "soundtrack": "cinematic",
        "movie": "cinematic",
        "epic": "cinematic",
    }

    def _get_lead_type_for_genre(self, genre):
        """Map genre to the optimal synth lead tone."""
        g = genre.strip().lower()
        if g in ("synthpop", "electronic", "heavyrock"):
            return "supersaw"
        elif g in ("anirudh", "funk"):
            return "funk"
        elif g in ("slowballad", "lofi"):
            return "lofi"
        elif g == "bolero":
            return "nylon"
        return "square"


    def _load_genre(self, genre_name, silent=False):
        raw = genre_name.strip().lower()
        genre = self.GENRE_ALIASES.get(raw, raw)
        if genre not in GENRE_PRESETS:
            genre = "pop"
        self.active_genre = genre
        preset = GENRE_PRESETS[genre]
        self.bpm = preset.get("bpm", self.bpm)
        self.swing = preset.get("swing", self.swing)

        prog = preset.get("progression", ["Am", "F", "C", "G"])
        self.set_chord_progression_internal(prog, preset.get("song_ref", ""))

        for t in TRACKS:
            if t in preset:
                self.pattern[t] = list(preset[t])
            else:
                self.pattern[t] = [0] * STEPS
                
        # Clear cached lead sounds so they re-render with the new genre's synth_type
        if hasattr(self, "lead_sounds"):
            self.lead_sounds.clear()
            self.chord_cache.clear()
            self.pad_cache.clear()
            
        # Re-render dynamic acoustic drums/bass
        if hasattr(self, "drum_sounds") and hasattr(self, "bass_sounds"):
            try:
                self.drum_sounds["snare"] = HighFiSynthesizer.generate_snare(genre)
                for note, freq in BASS_FREQS.items():
                    self.bass_sounds[note] = HighFiSynthesizer.generate_bass_note(freq, genre)
            except Exception as e:
                print(f"[MCPJAM] Failed to switch acoustic drums/bass: {e}")
            
        return genre

    def _build_ui(self):
        # ===================================================================
        # 1. TOP ABLETON-STYLE TRANSPORT & MASTER SECTION
        # ===================================================================
        top_bar = tk.Frame(self.root, bg="#1f2127", height=66, bd=1, relief="solid")
        top_bar.pack(fill="x", side="top")

        # Brand / Logo
        brand = tk.Frame(top_bar, bg="#1f2127")
        brand.pack(side="left", padx=(12, 6), pady=8)
        tk.Label(brand, text="MCPJAM", fg="#00e5ff", bg="#1f2127",
                 font=("Segoe UI", 15, "bold")).pack(side="left")
        tk.Label(brand, text="STUDIO", fg="#bb9af7", bg="#1f2127",
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=(3, 6))

        # Expression & Dynamic HUD Badge
        expr_box = tk.Frame(top_bar, bg="#101114", padx=6, pady=3, bd=1, relief="sunken")
        expr_box.pack(side="left", padx=(2, 6), pady=8)
        self.lbl_expr_hud = tk.Label(
            expr_box, text=f"EXPR: {self.active_expression.upper()} [{self.dynamic_level.upper()}] · {self.articulation.upper()}",
            fg="#2ee59d", bg="#101114", font=("Segoe UI", 8, "bold")
        )
        self.lbl_expr_hud.pack(side="left")

        # Ableton LCD BPM & Meter Display
        lcd_frame = tk.Frame(top_bar, bg="#101114", padx=6, pady=3, bd=1, relief="sunken")
        lcd_frame.pack(side="left", padx=6, pady=8)

        self.bpm_lcd = tk.Label(
            lcd_frame, text=f"{self.bpm}.00", fg="#00e5ff", bg="#101114",
            font=("Consolas", 13, "bold"), width=7
        )
        self.bpm_lcd.pack(side="left")

        tk.Label(lcd_frame, text="BPM", fg="#565f89", bg="#101114",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(2, 6))
        tk.Label(lcd_frame, text="4/4", fg="#ffcb6b", bg="#101114",
                 font=("Consolas", 9, "bold")).pack(side="left", padx=2)

        # Tempo +/- Nudges
        btn_down = tk.Button(
            top_bar, text="◀", width=2, fg="#ffffff", bg="#2b2d35",
            relief="flat", cursor="hand2", font=("Segoe UI", 8),
            command=lambda: self.set_bpm(self.bpm - 2)
        )
        btn_down.pack(side="left", padx=1)
        btn_up = tk.Button(
            top_bar, text="▶", width=2, fg="#ffffff", bg="#2b2d35",
            relief="flat", cursor="hand2", font=("Segoe UI", 8),
            command=lambda: self.set_bpm(self.bpm + 2)
        )
        btn_up.pack(side="left", padx=(1, 8))

        # Play / Stop Transport
        self.btn_play = tk.Button(
            top_bar, text="▶ PLAY", width=8,
            fg="#101114", bg="#10c971", activebackground="#00e5ff",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            command=self.toggle_play
        )
        self.btn_play.pack(side="left", padx=3)

        btn_stop = tk.Button(
            top_bar, text="⏹ STOP", width=7,
            fg="#ffffff", bg="#2b2d35", activebackground="#3d4250",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            command=self.stop_playback
        )
        btn_stop.pack(side="left", padx=3)

        # Metronome Click
        self.btn_metro = tk.Button(
            top_bar, text="CLICK", width=5, fg="#888888", bg="#2b2d35",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            command=self.toggle_metronome
        )
        self.btn_metro.pack(side="left", padx=(3, 10))

        # Groove Swing Slider
        swing_box = tk.Frame(top_bar, bg="#1f2127")
        swing_box.pack(side="left", padx=4)
        tk.Label(swing_box, text="SWING", fg="#7aa2f7", bg="#1f2127",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=2)
        self.scale_swing = tk.Scale(
            swing_box, from_=0, to=65, orient="horizontal", showvalue=0,
            bg="#1f2127", troughcolor="#101114", fg="#ffffff", length=60,
            highlightthickness=0, cursor="hand2", command=self._on_swing_change
        )
        self.scale_swing.set(self.swing)
        self.scale_swing.pack(side="left", padx=2)
        self.lbl_swing_val = tk.Label(swing_box, text=f"{self.swing}%",
                                      fg="#a9b1d6", bg="#1f2127", font=("Segoe UI", 8))
        self.lbl_swing_val.pack(side="left")

        # Ableton DJ Low-Pass Filter Slider
        filter_box = tk.Frame(top_bar, bg="#1f2127")
        filter_box.pack(side="left", padx=4)
        tk.Label(filter_box, text="FILTER", fg="#bb9af7", bg="#1f2127",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=2)
        self.scale_filter = tk.Scale(
            filter_box, from_=20, to=100, orient="horizontal", showvalue=0,
            bg="#1f2127", troughcolor="#101114", fg="#ffffff", length=60,
            highlightthickness=0, cursor="hand2", command=self._on_filter_change
        )
        self.scale_filter.set(100)
        self.scale_filter.pack(side="left", padx=2)

        # Master Fader & Stereo Peak VU Meter
        master_box = tk.Frame(top_bar, bg="#1f2127")
        master_box.pack(side="right", padx=(4, 14))
        tk.Label(master_box, text="MASTER", fg="#ff7640", bg="#1f2127",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=2)

        self.scale_master = tk.Scale(
            master_box, from_=0, to=100, orient="horizontal", showvalue=0,
            bg="#1f2127", troughcolor="#101114", fg="#ffffff", length=65,
            highlightthickness=0, cursor="hand2", command=self._on_master_vol
        )
        self.scale_master.set(int(self.master_volume * 100))
        self.scale_master.pack(side="left", padx=2)

        self.master_vu_canvas = tk.Canvas(master_box, width=14, height=30,
                                          bg="#101114", highlightthickness=0)
        self.master_vu_canvas.pack(side="left", padx=(4, 2))
        self.vu_bars = []
        for b in range(5):
            col = "#ff5370" if b == 0 else ("#ffcb6b" if b == 1 else "#10c971")
            bar = self.master_vu_canvas.create_rectangle(1, b*6+1, 13, b*6+5,
                                                         fill="#24283b", outline="")
            self.vu_bars.append((bar, col))

        # ===================================================================
        # 2. PROMINENT MCP AI PRODUCER CONTROL BANNER
        # ===================================================================
        mcp_hud = tk.Frame(self.root, bg="#111318", bd=1, relief="solid")
        mcp_hud.pack(fill="x", padx=12, pady=(5, 2))

        mcp_left = tk.Frame(mcp_hud, bg="#111318")
        mcp_left.pack(side="left", padx=8, pady=3)

        self.mcp_pill = tk.Label(
            mcp_left, text="● MCP PROTOCOL ACTIVE :8765",
            fg="#00e5ff", bg="#1a202c", font=("Segoe UI", 9, "bold"),
            padx=8, pady=2, bd=1, relief="ridge"
        )
        self.mcp_pill.pack(side="left")

        self.telemetry_lamp = tk.Label(
            mcp_left, text="REMOTE SYNC", fg="#2ee59d", bg="#111318",
            font=("Segoe UI", 8, "bold"), padx=6
        )
        self.telemetry_lamp.pack(side="left", padx=(4, 0))

        self.ai_action_banner = tk.Label(
            mcp_hud,
            text="AI PRODUCER: Dynamic Pop Chord Engine Active (Ask AI for any song's chords)",
            fg="#c0caf5", bg="#111318", font=("Segoe UI", 9, "italic")
        )
        self.ai_action_banner.pack(side="left", padx=10)

        self.lbl_cmd_counter = tk.Label(
            mcp_hud, text="MCP CALLS: 0", fg="#565f89", bg="#111318",
            font=("Segoe UI", 8, "bold")
        )
        self.lbl_cmd_counter.pack(side="right", padx=10)

        # ===================================================================
        # 3. DYNAMIC CHORD PROGRESSION HUD (Shows active pop progression)
        # ===================================================================
        chord_strip = tk.Frame(self.root, bg="#13151f", bd=1, relief="ridge")
        chord_strip.pack(fill="x", padx=12, pady=(2, 3))

        tk.Label(chord_strip, text="HARMONY / CHORDS:", fg="#2ee59d", bg="#13151f",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(8, 6), pady=4)

        self.chord_chips_frame = tk.Frame(chord_strip, bg="#13151f")
        self.chord_chips_frame.pack(side="left")
        self.chord_chip_labels = []

        self.song_ref_label = tk.Label(
            chord_strip, text=f"Inspiration: {self.song_ref_text}",
            fg="#e0af68", bg="#13151f", font=("Segoe UI", 8, "bold")
        )
        self.song_ref_label.pack(side="right", padx=10)

        self._update_chord_hud_ui()

        # ===================================================================
        # 4. GENRE PRESET SELECTOR (Pop, Synth-Pop, 4-Chords, R&B, etc.)
        # ===================================================================
        genre_frame = tk.Frame(self.root, bg="#17181c")
        genre_frame.pack(fill="x", padx=12, pady=(1, 2))

        tk.Label(genre_frame, text="STYLES:", fg="#565f89", bg="#17181c",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(2, 4))

        self.genre_buttons = {}
        styles = [
            ("pop", "POP"),
            ("synthpop", "SYNTHPOP"),
            ("orchestra", "ORCHESTRA"),
            ("cinematic", "CINEMATIC"),
            ("jfusion", "J-FUSION"),
            ("anirudh", "ANIRUDH"),
            ("heavyrock", "ROCK"),
            ("electronic", "EDM"),
            ("slowballad", "SLOW"),
            ("dancepop", "DANCE"),
            ("fourchords", "4-CHORDS"),
            ("lofi", "LO-FI"),
            ("funk", "FUNK"),
        ]
        for g_name, label in styles:
            btn = tk.Button(
                genre_frame, text=label,
                fg="#7aa2f7" if g_name == self.active_genre else "#a9b1d6",
                bg="#24283b" if g_name == self.active_genre else "#1f2127",
                activebackground="#3b4261", font=("Segoe UI", 7, "bold"),
                relief="flat", cursor="hand2", padx=4, pady=1,
                command=lambda g=g_name: self.apply_genre_from_ui(g)
            )
            btn.pack(side="left", padx=1)
            self.genre_buttons[g_name] = btn

        btn_rnd = tk.Button(
            genre_frame, text="🎲 RANDOM", fg="#ffffff", bg="#2b2d35",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            padx=5, pady=1, command=self.randomize_pattern
        )
        btn_rnd.pack(side="right", padx=2)

        btn_clr = tk.Button(
            genre_frame, text="🗑 CLEAR", fg="#ff5370", bg="#2b2d35",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            padx=5, pady=1, command=self.clear_all
        )
        btn_clr.pack(side="right", padx=2)

        # ===================================================================
        # 5. ABLETON SESSION SEQUENCER MATRIX (8 Tracks x 16 Steps)
        # ===================================================================
        matrix_card = tk.Frame(self.root, bg="#1a1c23", bd=1, relief="solid")
        matrix_card.pack(fill="both", expand=True, padx=12, pady=(2, 2))

        # Ruler Bar (1.1, 1.2, 1.3, 1.4 | 2.1 ...)
        ruler_frame = tk.Frame(matrix_card, bg="#1a1c23")
        ruler_frame.pack(fill="x", padx=6, pady=(4, 1))

        tk.Label(ruler_frame, text="", width=26, bg="#1a1c23").pack(side="left")

        self.playhead_labels = []
        for s in range(STEPS):
            bar = (s // 4) + 1
            sub = (s % 4) + 1
            tag = f"{bar}.{sub}"
            is_downbeat = (sub == 1)
            lbl = tk.Label(
                ruler_frame, text=tag if is_downbeat else "•", width=3,
                fg="#00e5ff" if is_downbeat else "#414868", bg="#1a1c23",
                font=("Consolas", 8, "bold" if is_downbeat else "normal")
            )
            pad_r = 6 if (s % 4 == 3 and s != STEPS - 1) else 2
            lbl.pack(side="left", padx=(1, pad_r))
            self.playhead_labels.append(lbl)

        # 8 Track Rows
        self.step_buttons = {}
        self.track_meters = {}
        self.track_mute_btns = {}
        self.track_solo_btns = {}
        self.track_headers = {}

        for track in TRACKS:
            row_frame = tk.Frame(matrix_card, bg="#1a1c23", pady=1)
            row_frame.pack(fill="x", padx=6)

            # Left Channel Strip (Ableton Style)
            strip = tk.Frame(row_frame, bg="#20222b", width=195, height=27, bd=1, relief="ridge")
            strip.pack(side="left", padx=(0, 6))
            strip.pack_propagate(False)
            self.track_headers[track] = strip

            # Pillar Color Stripe
            accent = tk.Frame(strip, bg=COLORS[track], width=4)
            accent.pack(side="left", fill="y")

            lbl_trk = tk.Label(
                strip, text=TRACK_LABELS[track], fg=COLORS[track], bg="#20222b",
                font=("Segoe UI", 8, "bold"), width=12, anchor="w"
            )
            lbl_trk.pack(side="left", padx=(4, 1))

            btn_m = tk.Button(
                strip, text="M", width=2, fg="#565f89", bg="#1a1c23",
                font=("Segoe UI", 7, "bold"), relief="flat", cursor="hand2",
                command=lambda t=track: self.toggle_mute(t)
            )
            btn_m.pack(side="left", padx=1)
            self.track_mute_btns[track] = btn_m

            btn_s = tk.Button(
                strip, text="S", width=2, fg="#565f89", bg="#1a1c23",
                font=("Segoe UI", 7, "bold"), relief="flat", cursor="hand2",
                command=lambda t=track: self.toggle_solo(t)
            )
            btn_s.pack(side="left", padx=1)
            self.track_solo_btns[track] = btn_s

            meter_canvas = tk.Canvas(strip, width=24, height=12, bg="#101114", highlightthickness=0)
            meter_canvas.pack(side="right", padx=(1, 3))
            meter_rect = meter_canvas.create_rectangle(1, 1, 2, 11, fill="#2ee59d", outline="")
            self.track_meters[track] = (meter_canvas, meter_rect)

            for c in range(STEPS):
                is_on = self.pattern[track][c]
                pad = tk.Button(
                    row_frame, text="", width=3, height=1,
                    bg=COLORS[track] if is_on else "#24283b",
                    activebackground="#ffffff",
                    relief="flat", bd=0, cursor="hand2",
                    command=lambda t=track, s=c: self.toggle_step(t, s)
                )
                pad_r = 6 if (c % 4 == 3 and c != STEPS - 1) else 2
                pad.pack(side="left", padx=(1, pad_r), pady=0)
                self.step_buttons[(track, c)] = pad

        # ===================================================================
        # 6. REAL-TIME MCP TELEMETRY & COMMAND STREAM CONSOLE
        # ===================================================================
        console_frame = tk.Frame(self.root, bg="#111318", height=120, bd=1, relief="solid")
        console_frame.pack(fill="x", side="bottom", padx=12, pady=(2, 6))

        console_header = tk.Frame(console_frame, bg="#111318")
        console_header.pack(fill="x", padx=8, pady=(3, 1))

        tk.Label(
            console_header,
            text="MCP TELEMETRY & SOCKET COMMAND FEED (WATCH AI CONTROL THIS APP IN REAL TIME)",
            fg="#7aa2f7", bg="#111318", font=("Segoe UI", 8, "bold")
        ).pack(side="left")

        btn_clr_feed = tk.Button(
            console_header, text="CLEAR LOG", fg="#565f89", bg="#111318",
            relief="flat", font=("Segoe UI", 7), cursor="hand2",
            command=self.clear_logs
        )
        btn_clr_feed.pack(side="right")

        self.log_text = tk.Text(
            console_frame, height=4, bg="#0e1015", fg="#a9b1d6",
            font=("Consolas", 8), relief="flat", bd=0, wrap="none"
        )
        self.log_text.pack(fill="both", expand=True, padx=8, pady=(0, 4))
        self.log_text.tag_config("time", foreground="#565f89")
        self.log_text.tag_config("mcp", foreground="#00e5ff", font=("Consolas", 8, "bold"))
        self.log_text.tag_config("ok", foreground="#2ee59d")
        self.log_text.tag_config("warn", foreground="#ffcb6b")
        self.log_text.tag_config("body", foreground="#c0caf5")

        self.log_event("SYSTEM", "BeatBox Studio Pop DAW active with Dynamic Chord Engine.")
        if AUDIO_ENABLED:
            self.log_event("AUDIO", "Polyphonic Rhodes Piano & Synth Pad engine active.")
        else:
            self.log_event("AUDIO", "Visual mode active (no audio hardware detected).", is_warn=True)
        self.log_event("MCP", f"Socket listener open on {HOST}:{PORT}. Waiting for my_server.py ...")

        self.root.bind("<space>", lambda e: self.toggle_play())

    def _update_chord_hud_ui(self):
        """Update the visual chord chips in the Chord HUD."""
        if not hasattr(self, "chord_chips_frame") or not hasattr(self, "song_ref_label"):
            return
        for widget in self.chord_chips_frame.winfo_children():
            widget.destroy()
        self.chord_chip_labels = []

        for i, ch in enumerate(self.chord_progression):
            chip = tk.Label(
                self.chord_chips_frame, text=f" {ch} ",
                fg="#ffffff", bg="#1e2233", font=("Segoe UI", 9, "bold"),
                padx=6, pady=1, bd=1, relief="solid"
            )
            chip.pack(side="left", padx=2)
            self.chord_chip_labels.append(chip)

        self.song_ref_label.configure(text=f"Inspiration: {self.song_ref_text}")
        self.last_active_chord_idx = -1

    def log_event(self, source, msg, is_warn=False):
        t_str = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{t_str}] ", "time")
        tag_col = "warn" if is_warn else ("mcp" if source == "MCP" else "ok")
        self.log_text.insert("end", f"[{source}] ", tag_col)
        self.log_text.insert("end", f"{msg}\n", "body")
        self.log_text.see("end")

    def clear_logs(self):
        self.log_text.delete("1.0", "end")

    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.btn_play.configure(text="❚❚ PAUSE", bg="#10c971", fg="#101114")
        else:
            self.btn_play.configure(text="▶ PLAY", bg="#ffcb6b", fg="#101114")

    def stop_playback(self):
        self.playing = False
        self.step_i = 0
        self.btn_play.configure(text="▶ PLAY", bg="#ffcb6b", fg="#101114")
        self._update_playhead_ui(0)

    def toggle_metronome(self):
        self.metronome = not self.metronome
        if self.metronome:
            self.btn_metro.configure(fg="#00e5ff", bg="#1a202c")
        else:
            self.btn_metro.configure(fg="#888888", bg="#2b2d35")

    def set_bpm(self, val):
        self.bpm = max(40, min(240, int(val)))
        self.bpm_lcd.configure(text=f"{self.bpm}.00")

    def _on_swing_change(self, val):
        self.swing = int(val)
        self.lbl_swing_val.configure(text=f"{self.swing}%")

    def _on_filter_change(self, val):
        self.dj_filter = int(val)

    def _on_master_vol(self, val):
        self.master_volume = float(val) / 100.0

    def toggle_mute(self, track):
        self.track_muted[track] = not self.track_muted[track]
        btn = self.track_mute_btns[track]
        if self.track_muted[track]:
            btn.configure(bg="#ff7640", fg="#ffffff")
        else:
            btn.configure(bg="#1a1c23", fg="#565f89")

    def toggle_solo(self, track):
        self.track_solo[track] = not self.track_solo[track]
        btn = self.track_solo_btns[track]
        if self.track_solo[track]:
            btn.configure(bg="#f6c944", fg="#101114")
        else:
            btn.configure(bg="#1a1c23", fg="#565f89")

    def toggle_step(self, track, step):
        current = self.pattern[track][step]
        new_val = 0 if current else 1
        self.pattern[track][step] = new_val
        self._update_pad_visual(track, step, new_val)
        if new_val and AUDIO_ENABLED:
            self._trigger_sound(track, step)

    def _update_pad_visual(self, track, step, is_on):
        btn = self.step_buttons.get((track, step))
        if btn:
            btn.configure(bg=COLORS[track] if is_on else "#24283b")

    def apply_genre_from_ui(self, genre_name):
        canonical = self._load_genre(genre_name)
        self.bpm_lcd.configure(text=f"{self.bpm}.00")
        self.scale_swing.set(self.swing)
        self.lbl_swing_val.configure(text=f"{self.swing}%")
        self._refresh_all_pads()

        for g, btn in self.genre_buttons.items():
            if g == canonical or g == genre_name:
                btn.configure(bg="#24283b", fg="#7aa2f7")
            else:
                btn.configure(bg="#1f2127", fg="#a9b1d6")

        desc = GENRE_PRESETS.get(canonical, {}).get("desc", canonical)
        self.ai_action_banner.configure(text=f"AI PRODUCER: Loaded {canonical.upper()} ({desc})")

    def clear_all(self):
        for t in TRACKS:
            self.pattern[t] = [0] * STEPS
        self._refresh_all_pads()
        self.ai_action_banner.configure(text="AI PRODUCER: Cleared all sequencer patterns")

    def randomize_pattern(self):
        for t in TRACKS:
            dens = 0.25 if t in ("kick", "snare", "keys") else 0.35
            self.pattern[t] = [1 if random.random() < dens else 0 for _ in range(STEPS)]
        self._refresh_all_pads()
        self.ai_action_banner.configure(text="AI PRODUCER: Generated randomized groove across all 4 pillars")

    def _refresh_all_pads(self):
        for t in TRACKS:
            for s in range(STEPS):
                self._update_pad_visual(t, s, self.pattern[t][s])

    # -----------------------------------------------------------------------
    # Multi-Pillar & Chord Audio Triggering
    # -----------------------------------------------------------------------
    def _trigger_sound(self, track, step_num, override_chord=None, override_note=None, engine=None, override_program=None):
        if not AUDIO_ENABLED:
            return
        any_solo = any(self.track_solo.values())
        if any_solo and not self.track_solo[track]:
            return
        if self.track_muted[track]:
            return

        active_chord = override_chord if override_chord else self.step_chords[step_num % len(self.step_chords)]
        
        # Hybrid Routing: MIDI (GeneralUser GS) is now the DEFAULT for all genres.
        # DSP math engine only used when explicitly engine='dsp' OR midi unavailable.
        use_midi = engine != "dsp" and self.midi_out is not None

        if use_midi:
            self._trigger_midi_sound(track, active_chord, override_note, step_num, override_program=override_program)
            return
            
        sound = None

        if track in self.drum_sounds:
            if track == "kick" and (self.active_genre in ("orchestra", "cinematic") or self.active_expression in ("maestoso", "grave", "furioso")):
                sound = getattr(self, "timpani_sound", None) or self.drum_sounds.get("kick")
            else:
                sound = self.drum_sounds.get(track)
        elif track == "bass":
            # Exact 12-tone chromatic auto-harmonization
            _, _, _, bass_note = parse_chord_frequencies(active_chord)
            sound = self.bass_sounds.get(bass_note, self.bass_sounds.get("A1"))
        elif track == "keys":
            if self.active_genre in ("orchestra", "cinematic"):
                sound = self.get_or_create_orchestral_strings_sound(active_chord)
            else:
                sound = self.get_or_create_chord_sound(active_chord, for_pad=False)
        elif track == "pad":
            if self.active_genre in ("orchestra", "cinematic"):
                sound = self.get_or_create_orchestral_strings_sound(active_chord)
            else:
                sound = self.get_or_create_chord_sound(active_chord, for_pad=True)
        elif track == "lead":
            if override_note:
                active_note = override_note
            else:
                step_note = self.step_lead_notes[step_num % len(self.step_lead_notes)]
                active_note = step_note if step_note else self.current_lead_note

            if self.active_genre in ("orchestra", "cinematic"):
                sound = self.get_or_create_bowed_lead_sound(active_note)
            else:
                sound = self.get_or_create_lead_sound(active_note)

        if sound:
            filt_factor = self.dj_filter / 100.0
            vol = self.master_volume * self.track_volumes.get(track, 1.0) * filt_factor
            sound.set_volume(max(0.0, min(1.0, vol)))
            sound.play()

    def _sequencer_loop(self):
        while self.running:
            if not self.playing:
                time.sleep(0.02)
                continue

            current_step = self.step_i

            active_hits = []
            for track in TRACKS:
                if self.pattern[track][current_step]:
                    self._trigger_sound(track, current_step)
                    active_hits.append(track)

            self.cmd_queue.put({
                "_internal": "tick",
                "step": current_step,
                "hits": active_hits
            })

            step_sec = (60.0 / max(40, self.bpm)) / 4.0
            swing_offset = (self.swing / 100.0) * 0.33 * step_sec
            if current_step % 2 == 0:
                delay = step_sec + swing_offset
            else:
                delay = max(0.01, step_sec - swing_offset)

            self.step_i = (current_step + 1) % STEPS
            time.sleep(delay)

    def _timeline_loop(self, events, lyrics):
        """Thread that executes a linear song timeline bypassing the 16-step grid."""
        start_time = time.time()
        
        all_events = sorted(events, key=lambda x: x['time_sec'])
        all_lyrics = sorted(lyrics, key=lambda x: x['time_sec'])
        
        event_idx = 0
        lyric_idx = 0
        
        while self.running and getattr(self, "timeline_active", False) and (event_idx < len(all_events) or lyric_idx < len(all_lyrics)):
            if getattr(self, "timeline_paused", False):
                time.sleep(0.05)
                start_time += 0.05
                continue
                
            now = time.time() - start_time
            
            while lyric_idx < len(all_lyrics) and now >= all_lyrics[lyric_idx]['time_sec']:
                text = all_lyrics[lyric_idx]['text']
                self.cmd_queue.put({"_internal": "update_banner", "text": f"🎙️ {text}"})
                lyric_idx += 1
                
            while event_idx < len(all_events) and now >= all_events[event_idx]['time_sec']:
                ev = all_events[event_idx]
                if "cmd" in ev:
                    self.cmd_queue.put(ev)
                else:
                    self._trigger_sound(
                        ev['track'], 0,
                        override_chord=ev.get('chord'),
                        override_note=ev.get('note'),
                        engine=ev.get('engine'),
                        override_program=ev.get('program')
                    )
                event_idx += 1
                
            time.sleep(0.01)
            
        self.cmd_queue.put({"_internal": "update_banner", "text": "AI PRODUCER: Timeline Playback Complete"})
        self.timeline_active = False

    def _raw_midi_timeline_loop(self, raw_events):
        """
        Thread that directly fires MIDI note_on / note_off / program_change
        messages to self.midi_out using absolute timestamps from a parsed
        MIDI file.  Supports full polyphony across all 16 GM channels.
        """
        if not self.midi_out:
            print("[BeatBox] No MIDI output available for raw MIDI playback.")
            self.timeline_active = False
            return

        all_events = sorted(raw_events, key=lambda x: x['time_sec'])
        # Send initial program changes for all channels before playback starts
        seen_programs = {}
        for ev in all_events:
            ch = ev.get('channel', 0)
            prog = ev.get('program', 0)
            if ch != 9 and ch not in seen_programs:
                seen_programs[ch] = prog
                try:
                    self.midi_out.set_instrument(prog, ch)
                except Exception:
                    pass

        start_time = time.time()
        event_idx = 0

        while self.running and getattr(self, "timeline_active", False) and event_idx < len(all_events):
            if getattr(self, "timeline_paused", False):
                time.sleep(0.05)
                start_time += 0.05
                continue

            now = time.time() - start_time

            while event_idx < len(all_events) and now >= all_events[event_idx]['time_sec']:
                ev = all_events[event_idx]
                ev_type = ev.get('type', '')
                ch = ev.get('channel', 0)
                note = ev.get('note', 60)
                vel = ev.get('velocity', 100)
                prog = ev.get('program', 0)

                try:
                    if ev_type == 'program_change' and ch != 9:
                        self.midi_out.set_instrument(prog, ch)
                    elif ev_type == 'note_on':
                        vol = int(vel * self.master_volume)
                        self.midi_out.note_on(note, max(1, min(127, vol)), ch)
                    elif ev_type == 'note_off':
                        self.midi_out.note_off(note, 0, ch)
                except Exception as e:
                    pass  # silently skip bad events

                event_idx += 1

            time.sleep(0.005)  # tighter poll for precise timing

        # All notes off on all channels when done
        try:
            for ch in range(16):
                for note in range(128):
                    self.midi_out.note_off(note, 0, ch)
        except Exception:
            pass

        self.cmd_queue.put({"_internal": "update_banner", "text": "🎵 MIDI File Playback Complete"})
        self.timeline_active = False

    def _update_playhead_ui(self, active_step, hits=None):
        hits = hits or []
        for s in range(STEPS):
            lbl = self.playhead_labels[s]
            sub = (s % 4) + 1
            is_downbeat = (sub == 1)
            if s == active_step:
                lbl.configure(fg="#ffffff", bg="#00e5ff")
            else:
                lbl.configure(
                    fg="#00e5ff" if is_downbeat else "#414868",
                    bg="#1a1c23"
                )

        # Highlight active chord in Chord HUD only when it transitions
        if self.chord_chip_labels and self.chord_progression:
            n_chords = len(self.chord_progression)
            steps_per = max(1, STEPS // n_chords)
            active_chord_idx = min(n_chords - 1, active_step // steps_per)
            if active_chord_idx != self.last_active_chord_idx:
                self.last_active_chord_idx = active_chord_idx
                for idx, chip in enumerate(self.chord_chip_labels):
                    if idx == active_chord_idx:
                        chip.configure(bg="#00e5ff", fg="#101114")
                    else:
                        chip.configure(bg="#1e2233", fg="#ffffff")

        for track in TRACKS:
            for s in range(STEPS):
                btn = self.step_buttons.get((track, s))
                if not btn:
                    continue
                is_on = self.pattern[track][s]
                if s == active_step:
                    btn.configure(bg="#ffffff" if is_on else "#3d425a")
                else:
                    btn.configure(bg=COLORS[track] if is_on else "#24283b")

            canvas, rect = self.track_meters[track]
            if track in hits:
                canvas.coords(rect, 1, 1, 22, 11)
                canvas.itemconfig(rect, fill=COLORS[track])
            else:
                canvas.coords(rect, 1, 1, 2, 11)
                canvas.itemconfig(rect, fill="#1f2335")

        level = len(hits)
        for b, (bar, col) in enumerate(self.vu_bars):
            if level > (4 - b):
                self.master_vu_canvas.itemconfig(bar, fill=col)
            else:
                self.master_vu_canvas.itemconfig(bar, fill="#24283b")

    # -----------------------------------------------------------------------
    # MCP Socket Server & Command Dispatcher
    # -----------------------------------------------------------------------
    def _poll_queue(self):
        try:
            while True:
                item = self.cmd_queue.get_nowait()
                if item.get("_internal") == "tick":
                    self._update_playhead_ui(item["step"], item.get("hits"))
                elif item.get("_internal") == "update_banner":
                    self.ai_action_banner.configure(text=item["text"])
                else:
                    try:
                        self._apply_mcp_cmd(item)
                    except Exception as e:
                        print(f"[BeatBox] Error applying MCP command {item}: {e}")
        except queue.Empty:
            pass
        except Exception as e:
            print(f"[BeatBox] Queue error: {e}")
        finally:
            if self.running:
                self.root.after(20, self._poll_queue)

    def _apply_mcp_cmd(self, cmd):
        kind = cmd.get("cmd")
        self.mcp_command_count += 1
        self.lbl_cmd_counter.configure(text=f"MCP CALLS: {self.mcp_command_count}")

        self.mcp_pill.configure(bg="#00e5ff", fg="#101114", text="● MCP EXECUTING")
        self.telemetry_lamp.configure(fg="#ffcb6b", text="AI PRODUCER")
        self.root.after(450, lambda: self.mcp_pill.configure(
            bg="#1a202c", fg="#00e5ff", text="● MCP PROTOCOL ACTIVE :8765"
        ))
        self.root.after(450, lambda: self.telemetry_lamp.configure(
            fg="#2ee59d", text="REMOTE SYNC"
        ))

        self.log_event("MCP", json.dumps(cmd))

        if kind == "set_chords" or kind == "set_progression":
            chords = cmd.get("chords", ["Am", "F", "C", "G"])
            if isinstance(chords, str):
                chords = [c.strip() for c in chords.replace("-", ",").replace(">", ",").split(",") if c.strip()]
            ref = cmd.get("song_ref") or cmd.get("label") or ""
            self.set_chord_progression_internal(chords, ref)
            self.ai_action_banner.configure(
                text=f"AI PRODUCER: Chords [{', '.join(self.chord_progression)}] ({self.song_ref_text})"
            )

        elif kind == "set_melody":
            notes = cmd.get("notes", [])
            self.set_melody_internal(notes)
            self.ai_action_banner.configure(text="AI PRODUCER: Programmed custom lead melody riff")

        elif kind == "set_tempo":
            bpm = cmd.get("bpm")
            if bpm:
                self.set_bpm(bpm)
                self.ai_action_banner.configure(text=f"AI PRODUCER: Set tempo to {self.bpm} BPM")

        elif kind == "set_pattern":
            track = cmd.get("track")
            steps = cmd.get("steps")
            if track in self.pattern and isinstance(steps, list):
                steps = (steps + [0] * STEPS)[:STEPS]
                self.pattern[track] = [1 if s else 0 for s in steps]
                self._refresh_all_pads()
                self._flash_track_header(track)
                self.ai_action_banner.configure(text=f"AI PRODUCER: Updated {track.upper()} pattern")

        elif kind == "apply_style":
            style = cmd.get("style", "pop").lower()
            self.apply_genre_from_ui(style)

        elif kind == "set_label":
            txt = cmd.get("text", "")
            self.ai_action_banner.configure(text=f"AI PRODUCER: {txt}")

        elif kind == "set_lead_note":
            note = cmd.get("note", "E5").upper()
            self.current_lead_note = note
            self.get_or_create_lead_sound(note)
            self.ai_action_banner.configure(text=f"AI PRODUCER: Lead pitch set to {note}")

        elif kind == "set_swing":
            amt = max(0, min(75, int(cmd.get("amount", 0))))
            self.swing = amt
            self.scale_swing.set(amt)
            self.lbl_swing_val.configure(text=f"{amt}%")
            self.ai_action_banner.configure(text=f"AI PRODUCER: Groove swing set to {amt}%")

        elif kind == "set_filter":
            cutoff = max(20, min(100, int(cmd.get("cutoff", 100))))
            self.dj_filter = cutoff
            self.scale_filter.set(cutoff)
            self.ai_action_banner.configure(text=f"AI PRODUCER: DJ filter cutoff at {cutoff}%")

        elif kind == "clear":
            track = cmd.get("track")
            if track and track in self.pattern:
                self.pattern[track] = [0] * STEPS
                self._refresh_all_pads()
            else:
                self.clear_all()

        elif kind == "play":
            if getattr(self, "timeline_active", False):
                self.timeline_paused = False
            else:
                self.playing = True
            self.btn_play.configure(text="❚❚ PAUSE", bg="#10c971", fg="#101114")
            self.ai_action_banner.configure(text="AI PRODUCER: Started playback ▶")

        elif kind == "pause":
            if getattr(self, "timeline_active", False):
                self.timeline_paused = True
            else:
                self.playing = False
            self.btn_play.configure(text="▶ PLAY", bg="#ffcb6b", fg="#101114")
            self.ai_action_banner.configure(text="AI PRODUCER: Paused playback ❚❚")

        elif kind == "stop":
            self.timeline_active = False
            self.stop_playback()
            self.ai_action_banner.configure(text="AI PRODUCER: Stopped sequencer ⏹")

        elif kind == "mute_track":
            track = cmd.get("track")
            if track in self.track_muted:
                self.track_muted[track] = bool(cmd.get("muted", True))
                btn = self.track_mute_btns[track]
                btn.configure(bg="#ff7640" if self.track_muted[track] else "#1a1c23",
                              fg="#ffffff" if self.track_muted[track] else "#565f89")

        elif kind == "solo_track":
            track = cmd.get("track")
            if track in self.track_solo:
                self.track_solo[track] = bool(cmd.get("solo", True))
                btn = self.track_solo_btns[track]
                btn.configure(bg="#f6c944" if self.track_solo[track] else "#1a1c23",
                              fg="#101114" if self.track_solo[track] else "#565f89")

        elif kind == "randomize":
            self.randomize_pattern()

        elif kind == "batch":
            for sub in cmd.get("commands", []):
                self._apply_mcp_cmd(sub)
                
        elif kind == "play_timeline":
            self.playing = False  # Pause the 16-step sequencer
            self.timeline_active = True
            self.timeline_paused = False
            
            bpm = cmd.get("bpm", 120)
            self.set_bpm(bpm)
            self.apply_genre_from_ui(cmd.get("style", "pop").lower())
            
            events = cmd.get("events", [])
            lyrics = cmd.get("lyrics", [])
            
            # Convert beats to time_sec if not already present
            beat_sec = 60.0 / bpm
            for ev in events:
                if 'time_sec' not in ev:
                    ev['time_sec'] = ev.get('beat', 0.0) * beat_sec
            for ly in lyrics:
                if 'time_sec' not in ly:
                    ly['time_sec'] = ly.get('beat', 0.0) * beat_sec
                    
            self.ai_action_banner.configure(text=f"AI PRODUCER: Starting Linear Timeline Playback...")
            threading.Thread(target=self._timeline_loop, args=(events, lyrics), daemon=True).start()

        elif kind == "play_midi_raw":
            # Faithful MIDI file playback — direct note_on/off to GM synth
            self.playing = False
            self.timeline_active = True
            self.timeline_paused = False
            raw_events = cmd.get("events", [])
            title = cmd.get("title", "MIDI File")
            self.ai_action_banner.configure(text=f"🎵 Playing: {title}")
            threading.Thread(
                target=self._raw_midi_timeline_loop,
                args=(raw_events,),
                daemon=True
            ).start()

        elif kind == "set_expression":
            expr_key = cmd.get("expression", "espressivo").strip().lower()
            dyn = cmd.get("dynamic", "mf").strip().lower()
            apply_prog = cmd.get("apply_progression", True)
            self.apply_expression_internal(expr_key, dyn, apply_prog)

        elif kind == "set_articulation":
            art = cmd.get("articulation", "legato").strip().lower()
            self.articulation = art
            self.bowed_string_cache.clear()
            self._update_expr_hud_ui()
            self.ai_action_banner.configure(text=f"AI PRODUCER: Articulation set to {art.upper()}")

    def _flash_track_header(self, track):
        strip = self.track_headers.get(track)
        if strip:
            strip.configure(bg="#00e5ff")
            self.root.after(400, lambda: strip.configure(bg="#20222b"))

    def get_state(self):
        return {
            "ok": True,
            "bpm": self.bpm,
            "playing": self.playing,
            "swing": self.swing,
            "dj_filter": self.dj_filter,
            "master_volume": round(self.master_volume, 2),
            "active_genre": self.active_genre,
            "active_expression": self.active_expression,
            "dynamic_level": self.dynamic_level,
            "articulation": self.articulation,
            "chord_progression": list(self.chord_progression),
            "song_reference": self.song_ref_text,
            "current_lead_note": self.current_lead_note,
            "step_lead_notes": list(self.step_lead_notes),
            "tracks": list(TRACKS),
            "muted": dict(self.track_muted),
            "solo": dict(self.track_solo),
            "patterns": {t: list(self.pattern[t]) for t in TRACKS},
            "audio_enabled": AUDIO_ENABLED
        }

    def _start_socket_server(self):
        def serve():
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                srv.bind((HOST, PORT))
                srv.listen(5)
            except Exception as e:
                print(f"[BeatBox] Socket bind error on {HOST}:{PORT} - {e}")
                return

            while self.running:
                try:
                    conn, _ = srv.accept()
                    threading.Thread(target=self._handle_conn, args=(conn,), daemon=True).start()
                except Exception:
                    break

        threading.Thread(target=serve, daemon=True).start()

    def _handle_conn(self, conn):
        with conn:
            buf = b""
            while self.running:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    if not line.strip():
                        continue
                    try:
                        cmd = json.loads(line.decode("utf-8"))
                        if cmd.get("cmd") == "get_state":
                            state = self.get_state()
                            try:
                                conn.sendall(json.dumps(state).encode("utf-8") + b"\n")
                            except Exception:
                                break
                        elif cmd.get("cmd") == "batch":
                            for sub in cmd.get("commands", []):
                                self.cmd_queue.put(sub)
                            try:
                                conn.sendall(b'{"ok": true}\n')
                            except Exception:
                                break
                        else:
                            self.cmd_queue.put(cmd)
                            try:
                                conn.sendall(b'{"ok": true}\n')
                            except Exception:
                                break
                    except Exception as e:
                        try:
                            conn.sendall(json.dumps({"ok": False, "error": str(e)}).encode("utf-8") + b"\n")
                        except Exception:
                            break

    def _on_close(self):
        self.running = False
        if self.midi_out:
            try:
                self.midi_out.close()
                pygame.midi.quit()
            except:
                pass
        self.root.destroy()
        sys.exit(0)


def main():
    root = tk.Tk()
    BeatBoxStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
