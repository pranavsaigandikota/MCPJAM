import io
import math
import random
import struct
import wave
from .constants import SEMI_MAP, CHORD_FORMULAS, ROOT_TO_BASS_NOTE, BASS_FREQS

AUDIO_ENABLED = False
try:
    import pygame
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    AUDIO_ENABLED = True
except Exception as _e:
    print(f"[BeatBox] Audio initialization warning: {_e}. Running in visual-only mode.")


def parse_chord_frequencies(chord_name: str):
    """Parse any chord name (e.g. 'Am', 'Fmaj7', 'C#m', 'Bb', 'Gsus4') into audio frequencies."""
    clean = chord_name.strip().upper().replace("MIN", "M").replace("MAJOR", "MAJ")
    if len(clean) > 1 and clean[1] in ("#", "B"):
        root = clean[:2]
        quality = clean[2:]
    elif clean:
        root = clean[:1]
        quality = clean[1:]
    else:
        root = "C"
        quality = ""

    semi = SEMI_MAP.get(root, 0)
    intervals = CHORD_FORMULAS.get(quality, [0, 4, 7])

    # Base root in octave 3/4 (C4 = 261.63 Hz)
    root_f = 261.63 * (2.0 ** (semi / 12.0))
    if root_f > 380:
        root_f /= 2.0  # Keep in comfortable mid octave

    freqs = [root_f * (2.0 ** (iv / 12.0)) for iv in intervals]
    bass_note = ROOT_TO_BASS_NOTE.get(root, "A1")
    return root, quality, freqs, bass_note


def parse_note_frequency(note_str: str) -> float:
    """Parse a note string like 'C4', 'Eb5', 'A#4', 'F#5' to Hz."""
    note = note_str.strip().upper()
    if not note:
        return 440.0
    # Extract octave if present
    if note[-1].isdigit():
        octave = int(note[-1])
        pitch = note[:-1]
    else:
        octave = 5
        pitch = note

    semi = SEMI_MAP.get(pitch, 0)
    # C4 = 261.6256 Hz
    return (440.0 / (2.0 ** (9 / 12.0))) * (2.0 ** (octave - 4)) * (2.0 ** (semi / 12.0))




class HighFiSynthesizer:
    SAMPLE_RATE = 44100

    @classmethod
    def _create_wav(cls, samples):
        if not AUDIO_ENABLED:
            return None
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(cls.SAMPLE_RATE)
            frames = bytearray()
            for s in samples:
                val = int(max(-1.0, min(1.0, s)) * 32767.0)
                frames.extend(struct.pack("<h", val))
            wf.writeframes(frames)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    # 1. DRUMS & PERCUSSION
    @classmethod
    def generate_kick(cls):
        duration = 0.38
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            freq = 155.0 * math.exp(-t * 24.0) + 46.0
            phase = 2.0 * math.pi * freq * t
            sub = math.sin(phase) * math.exp(-t * 7.5)
            click = 0.35 * math.exp(-t * 130.0) * math.sin(2.0 * math.pi * 950.0 * t)
            body = 0.3 * math.exp(-t * 15.0) * math.sin(2.0 * math.pi * 85.0 * t)
            samples.append(math.tanh(sub * 1.2 + click + body))
        return cls._create_wav(samples)

    @classmethod
    def generate_snare(cls, genre="pop"):
        if genre.lower() == "bolero":
            return cls._generate_brush_snare()
        duration = 0.24
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            tone = math.sin(2.0 * math.pi * 185.0 * t) * math.exp(-t * 22.0)
            noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 16.0)
            reverb = (random.random() * 2.0 - 1.0) * math.exp(-t * 8.0) * 0.2
            samples.append(math.tanh((tone * 0.6 + noise * 0.55 + reverb) * 1.2))
        return cls._create_wav(samples)

    @classmethod
    def _generate_brush_snare(cls):
        duration = 0.5
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        b0 = b1 = b2 = b3 = b4 = b5 = b6 = 0.0
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            white = (random.random() * 2.0 - 1.0)
            b0 = 0.99886 * b0 + white * 0.0555179
            b1 = 0.99332 * b1 + white * 0.0750759
            b2 = 0.96900 * b2 + white * 0.1538520
            b3 = 0.86650 * b3 + white * 0.3104856
            b4 = 0.55000 * b4 + white * 0.5329522
            b5 = -0.7616 * b5 - white * 0.0168980
            pink = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362
            b6 = white * 0.115926
            env = math.exp(-t * 4.0)
            tap = math.sin(2.0 * math.pi * 180.0 * t) * math.exp(-t * 30.0) * 0.3
            raw = (pink * 0.15 * env) + tap
            samples.append(raw * 0.8)
        return cls._create_wav(samples)

    @classmethod
    def generate_hihat_closed(cls):
        duration = 0.045
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        last_noise = 0.0
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            curr = random.random() * 2.0 - 1.0
            hp = curr - last_noise
            last_noise = curr
            amp = math.exp(-t * 90.0)
            samples.append(hp * amp * 0.7)
        return cls._create_wav(samples)

    @classmethod
    def generate_clap(cls):
        duration = 0.26
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            raw = random.random() * 2.0 - 1.0
            amp = 0.0
            for delay in (0.0, 0.011, 0.022):
                if t >= delay:
                    amp += math.exp(-(t - delay) * 85.0) * 0.45
            if t >= 0.022:
                amp += math.exp(-(t - 0.022) * 14.0) * 0.4
            samples.append(raw * amp)
        return cls._create_wav(samples)

    # 2. BASS (Groove Bass & 808 Sub)
    @classmethod
    def generate_bass_note(cls, freq=55.0, genre="pop"):
        if genre.lower() == "bolero":
            return cls._generate_precision_bass(freq)
            
        duration = 0.42
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            f = freq
            w1 = math.sin(2.0 * math.pi * f * t)
            w2 = 0.5 * math.sin(2.0 * math.pi * (f * 2.0) * t) * math.exp(-t * 5.0)
            w3 = 0.25 * math.sin(2.0 * math.pi * (f * 3.0) * t) * math.exp(-t * 8.0)
            click = 0.22 * math.exp(-t * 75.0) * math.sin(2.0 * math.pi * 320.0 * t)
            amp = math.exp(-t * 3.6)
            raw = (w1 + w2 + w3 + click) * amp
            samples.append(math.tanh(raw * 1.6) * 0.88)
        return cls._create_wav(samples)

    @classmethod
    def _generate_precision_bass(cls, freq):
        duration = 0.6
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        lp1 = 0.0
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            transient = math.exp(-t * 40.0) * (random.random() * 2.0 - 1.0) * 0.15
            tri = 2.0 * abs(2.0 * (t * freq - math.floor(0.5 + t * freq))) - 1.0
            saw = 2.0 * (t * freq - math.floor(0.5 + t * freq))
            raw = tri * 0.8 + saw * 0.2 + transient
            
            cutoff_hz = 600.0 + math.exp(-t * 5.0) * 800.0
            rc = 1.0 / (2.0 * math.pi * cutoff_hz)
            dt = 1.0 / cls.SAMPLE_RATE
            alpha = dt / (rc + dt)
            lp1 += alpha * (raw - lp1)
            
            amp = math.exp(-t * 2.5) if t > 0.01 else (t / 0.01)
            samples.append(math.tanh(lp1 * 1.5) * amp * 0.9)
        return cls._create_wav(samples)

    # 3. HARMONY (Fender Rhodes & Heavy Rock Power Chords)
    @classmethod
    def generate_nylon_guitar_chord(cls, chord_notes):
        """Polyphonic acoustic nylon guitar chord."""
        duration = 0.85
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            val = 0.0
            for f in chord_notes:
                # Plucked string body
                body = math.sin(2.0 * math.pi * f * t) * math.exp(-t * 4.5)
                h2 = 0.4 * math.sin(2.0 * math.pi * (f * 2.0) * t) * math.exp(-t * 6.0)
                h3 = 0.2 * math.sin(2.0 * math.pi * (f * 3.0) * t) * math.exp(-t * 8.0)
                # Pick attack
                pick = (random.random() * 2.0 - 1.0) * math.exp(-t * 100.0) * 0.1
                val += (body + h2 + h3 + pick)
            samples.append(math.tanh(val * 0.6) * 0.85)
        return cls._create_wav(samples)

    @classmethod
    def generate_mariachi_brass_chord(cls, chord_notes):
        """Polyphonic expressive Mariachi trumpet section."""
        duration = 0.85
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            val = 0.0
            for f in chord_notes:
                # Expressive vibrato
                vib_amt = min(1.0, max(0.0, t * 2.0 - 0.2)) * 0.02
                vib = math.sin(2.0 * math.pi * 6.5 * t) * vib_amt
                cur_f = f * (1.0 + vib)
                
                saw = 2.0 * (t * cur_f - math.floor(0.5 + t * cur_f))
                h2 = math.sin(2.0 * math.pi * cur_f * 2.0 * t) * 0.5
                h3 = math.sin(2.0 * math.pi * cur_f * 3.0 * t) * 0.25
                h4 = math.sin(2.0 * math.pi * cur_f * 4.0 * t) * 0.12
                val += (saw * 0.3 + h2 + h3 + h4)
                
            if t < 0.05:
                amp = t / 0.05
            else:
                amp = 1.0 - (t - 0.05) * 0.2
            samples.append(math.tanh(val * 0.4) * amp * 0.85)
        return cls._create_wav(samples)

    @classmethod
    def generate_rhodes_chord(cls, chord_notes):
        duration = 0.75
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []

        # Detect if this is a rock power chord (Root + 5th, ratio ~ 1.5)
        is_power = False
        if len(chord_notes) in (2, 3) and len(chord_notes) >= 2:
            ratio = chord_notes[1] / chord_notes[0]
            if 1.45 <= ratio <= 1.55:
                is_power = True

        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            val = 0.0
            if is_power:
                # Heavy rock guitar overdrive harmonics
                for f in chord_notes:
                    tone = math.sin(2.0 * math.pi * f * t)
                    h2 = 0.55 * math.sin(2.0 * math.pi * (f * 2.0) * t)
                    h3 = 0.35 * math.sin(2.0 * math.pi * (f * 3.0) * t)
                    val += (tone + h2 + h3)
                env = math.exp(-t * 2.0)
                val = math.tanh(val * 1.5) * env * 0.85
            else:
                # Warm Fender Rhodes electric piano
                for f in chord_notes:
                    tone = math.sin(2.0 * math.pi * f * t) * math.exp(-t * 2.6)
                    h2 = 0.35 * math.sin(2.0 * math.pi * (f * 2.0) * t) * math.exp(-t * 3.5)
                    tine = 0.25 * math.sin(2.0 * math.pi * (f * 4.15) * t) * math.exp(-t * 18.0)
                    chorus = 0.2 * math.sin(2.0 * math.pi * (f * 1.003) * t) * math.exp(-t * 2.8)
                    val += (tone + h2 + tine + chorus)
                val = math.tanh(val * 0.35) * 0.8
            samples.append(val)
        return cls._create_wav(samples)

    @classmethod
    def generate_synth_lead(cls, freq=440.0, synth_type="square"):
        """Dispatcher for different pop synth lead sounds based on genre context."""
        t_clean = synth_type.strip().lower()
        if t_clean == "supersaw":
            return cls._generate_supersaw_lead(freq)
        elif t_clean == "funk":
            return cls._generate_funk_lead(freq)
        elif t_clean == "lofi":
            return cls._generate_lofi_bell(freq)
        elif t_clean == "nylon":
            return cls.generate_nylon_guitar_chord([freq])
        else:
            return cls._generate_square_pluck(freq)

    @classmethod
    def _generate_supersaw_lead(cls, freq):
        """Classic 80s / EDM detuned sawtooth brass lead."""
        duration = 0.4
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        lp1 = lp2 = lp3 = lp4 = 0.0
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            s1 = 2.0 * (t * freq * 0.996 - math.floor(0.5 + t * freq * 0.996))
            s2 = 2.0 * (t * freq * 0.998 - math.floor(0.5 + t * freq * 0.998))
            s3 = 2.0 * (t * freq * 1.002 - math.floor(0.5 + t * freq * 1.002))
            s4 = 2.0 * (t * freq * 1.004 - math.floor(0.5 + t * freq * 1.004))
            raw = (s1 + s2 + s3 + s4) * 0.25
            
            env = math.exp(-t * 8.0)
            cutoff_hz = 600.0 + 4000.0 * env
            rc = 1.0 / (2.0 * math.pi * cutoff_hz)
            dt = 1.0 / cls.SAMPLE_RATE
            alpha = dt / (rc + dt)
            lp1 += alpha * (raw - lp1)
            lp2 += alpha * (lp1 - lp2)
            lp3 += alpha * (lp2 - lp3)
            lp4 += alpha * (lp3 - lp4)
            
            amp = math.exp(-t * 2.5) if t > 0.01 else (t / 0.01)
            samples.append(math.tanh(lp4 * 2.0) * amp * 0.7)
        return cls._create_wav(samples)

    @classmethod
    def _generate_funk_lead(cls, freq):
        """West coast G-Funk moog triangle wave with vibrato."""
        duration = 0.4
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            vib_amt = min(1.0, max(0.0, t * 2.0 - 0.2)) * 0.015
            vib = math.sin(2.0 * math.pi * 6.0 * t) * vib_amt
            cur_f = freq * (1.0 + vib)
            
            tri = 2.0 * abs(2.0 * (t * cur_f - math.floor(0.5 + t * cur_f))) - 1.0
            body = math.sin(2.0 * math.pi * cur_f * t)
            raw = tri * 0.6 + body * 0.4
            
            amp = math.exp(-t * 1.5) if t > 0.02 else (t / 0.02)
            samples.append(math.tanh(raw * 1.2) * amp * 0.7)
        return cls._create_wav(samples)

    @classmethod
    def _generate_lofi_bell(cls, freq):
        """Soft R&B / Lo-Fi FM bell with tape flutter."""
        duration = 0.4
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            drift = math.sin(2.0 * math.pi * 0.5 * t) * 0.008
            cur_f = freq * (1.0 + drift)
            
            c_phase = 2.0 * math.pi * cur_f * t
            m_env = math.exp(-t * 20.0)
            mod = math.sin(2.0 * math.pi * (cur_f * 3.5) * t) * m_env * 2.0
            
            raw = math.sin(c_phase + mod)
            noise = (random.random() * 2.0 - 1.0) * 0.02
            amp = math.exp(-t * 4.0) if t > 0.005 else (t / 0.005)
            samples.append((raw + noise) * amp * 0.6)
        return cls._create_wav(samples)

    @classmethod
    def _generate_square_pluck(cls, freq):
        """Classic dance-pop square wave pluck."""
        duration = 0.4
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        lp1 = 0.0
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            sq1 = 1.0 if (t * freq - math.floor(t * freq)) < 0.5 else -1.0
            sq2 = 1.0 if (t * freq * 1.005 - math.floor(t * freq * 1.005)) < 0.5 else -1.0
            raw = (sq1 + sq2) * 0.5
            
            env = math.exp(-t * 18.0)
            cutoff_hz = 400.0 + 5000.0 * env
            rc = 1.0 / (2.0 * math.pi * cutoff_hz)
            dt = 1.0 / cls.SAMPLE_RATE
            alpha = dt / (rc + dt)
            lp1 += alpha * (raw - lp1)
            
            amp = math.exp(-t * 3.0) if t > 0.005 else (t / 0.005)
            samples.append(lp1 * amp * 0.8)
        return cls._create_wav(samples)

    @classmethod
    def generate_synth_pad(cls, chord_notes):
        duration = 0.95
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            env = min(1.0, t / 0.12) * math.exp(-t * 1.2)
            val = 0.0
            for f in chord_notes:
                s1 = math.sin(2.0 * math.pi * f * t)
                s2 = 0.7 * math.sin(2.0 * math.pi * (f * 1.005) * t)
                s3 = 0.5 * math.sin(2.0 * math.pi * (f * 0.995) * t)
                val += (s1 + s2 + s3)
            val = math.tanh(val * 0.28) * env
            samples.append(val * 0.65)
        return cls._create_wav(samples)

    # 5. ORCHESTRAL INSTRUMENTS (Bowed Strings, Timpani, Fanfare Brass)
    @classmethod
    def generate_timpani(cls, pitch_hz=73.41, dynamic="mf"):
        """Acoustic orchestral timpani drum with mallet transient and pitch drop."""
        duration = 0.75
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        f0 = pitch_hz
        vel = 1.0 if dynamic in ("f", "ff", "fff") else (0.85 if dynamic == "mf" else 0.65)
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            pitch_env = 1.0 + 0.45 * math.exp(-t * 38.0)
            cur_f = f0 * pitch_env
            m1 = math.sin(2.0 * math.pi * cur_f * 1.0 * t) * math.exp(-t * 3.2)
            m2 = 0.52 * math.sin(2.0 * math.pi * cur_f * 1.50 * t) * math.exp(-t * 4.8)
            m3 = 0.28 * math.sin(2.0 * math.pi * cur_f * 1.98 * t) * math.exp(-t * 7.2)
            m4 = 0.15 * math.sin(2.0 * math.pi * cur_f * 2.44 * t) * math.exp(-t * 9.5)
            mallet = 0.35 * math.sin(2.0 * math.pi * 310.0 * t) * math.exp(-t * 85.0)
            raw = (m1 + m2 + m3 + m4 + mallet)
            samples.append(math.tanh(raw * 1.5) * 0.92 * vel)
        return cls._create_wav(samples)

    @classmethod
    def generate_bowed_string(cls, freq=440.0, duration=0.8, articulation="legato", dynamic="mf"):
        """Physical modeling of a bowed string instrument (Bow scratch, comb resonance, vibrato, 4.5kHz low-pass)."""
        n_samples = int(cls.SAMPLE_RATE * duration)
        dynamic_settings = {
            "ppp": (0.35, 2200),
            "pp":  (0.48, 2600),
            "p":   (0.60, 3100),
            "mp":  (0.72, 3700),
            "mf":  (0.85, 4500),
            "f":   (0.95, 5000),
            "ff":  (1.00, 5500),
            "fff": (1.00, 5800)
        }
        vel_scale, cutoff_hz = dynamic_settings.get(dynamic.lower(), (0.85, 4500))

        delay_len = max(2, int(cls.SAMPLE_RATE / max(20.0, freq)))
        delay_buf = [0.0] * delay_len
        delay_idx = 0
        feedback = 0.65 if articulation != "staccato" else 0.35

        b0 = b1 = b2 = b3 = b4 = b5 = b6 = 0.0
        rc = 1.0 / (2.0 * math.pi * cutoff_hz)
        dt = 1.0 / cls.SAMPLE_RATE
        alpha = dt / (rc + dt)
        lp_state = 0.0

        samples = []
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE

            # 1. Bow Scratch (Pink noise friction)
            white = (random.random() * 2.0 - 1.0)
            b0 = 0.99886 * b0 + white * 0.0555179
            b1 = 0.99332 * b1 + white * 0.0750759
            b2 = 0.96900 * b2 + white * 0.1538520
            b3 = 0.86650 * b3 + white * 0.3104856
            b4 = 0.55000 * b4 + white * 0.5329522
            b5 = -0.7616 * b5 - white * 0.0168980
            pink = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362
            b6 = white * 0.115926

            if t < 0.04:
                bow_scratch = pink * 0.35 * (1.0 - t / 0.04)
            else:
                bow_scratch = pink * 0.06

            # 2. Delayed Vibrato (~5.2 Hz)
            if t > 0.12 and articulation != "staccato":
                vib_depth = min(0.018, (t - 0.12) * 0.08)
                vib = vib_depth * math.sin(2.0 * math.pi * 5.2 * t)
            else:
                vib = 0.0

            cur_f = freq * (1.0 + vib)

            # Sawtooth harmonic series
            saw = 0.0
            for h in range(1, 13):
                hf = cur_f * h
                if hf > 16000:
                    break
                saw += (math.sin(2.0 * math.pi * hf * t) / h)
            saw = saw * (2.0 / math.pi)

            # 3. String Comb Length Resonance
            comb_in = saw * 0.75 + bow_scratch * 0.4
            comb_out = comb_in + delay_buf[delay_idx] * feedback
            delay_buf[delay_idx] = comb_out
            delay_idx = (delay_idx + 1) % delay_len

            # 4. Warmth & Body Resonance (4.5 kHz Low-Pass)
            lp_state += alpha * (comb_out - lp_state)
            body = 0.15 * math.sin(2.0 * math.pi * 280.0 * t) + 0.10 * math.sin(2.0 * math.pi * 450.0 * t)
            raw = lp_state + body * 0.2

            # 5. ADSR Envelope
            if articulation == "staccato":
                amp = t / 0.012 if t < 0.012 else math.exp(-(t - 0.012) * 28.0)
            elif articulation == "dolce":
                if t < 0.12:
                    amp = (t / 0.12) ** 1.5
                elif t < duration - 0.25:
                    amp = 1.0
                else:
                    amp = max(0.0, (duration - t) / 0.25)
            elif articulation == "marcato":
                amp = 1.25 * (t / 0.015) if t < 0.015 else math.exp(-(t - 0.015) * 2.2) * 0.95
            else: # Legato
                if t < 0.07:
                    amp = t / 0.07
                elif t < duration - 0.2:
                    amp = 1.0
                else:
                    amp = max(0.0, (duration - t) / 0.2)

            val = math.tanh(raw * 1.2) * amp * vel_scale * 0.8
            samples.append(val)
        return cls._create_wav(samples)

    @classmethod
    def generate_bowed_string_chord(cls, chord_notes, articulation="legato", dynamic="mf"):
        """Polyphonic orchestral bowed string ensemble with voice detuning."""
        duration = 0.9 if articulation != "staccato" else 0.28
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        vel = 1.0 if dynamic in ("f", "ff", "fff") else (0.85 if dynamic == "mf" else 0.65)
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            val = 0.0
            for f in chord_notes:
                s1 = math.sin(2.0 * math.pi * f * t)
                s2 = 0.7 * math.sin(2.0 * math.pi * (f * 1.003) * t)
                s3 = 0.5 * math.sin(2.0 * math.pi * (f * 0.997) * t)
                val += (s1 + s2 + s3)
            if articulation == "staccato":
                amp = math.exp(-t * 22.0)
            elif articulation == "dolce":
                amp = min(1.0, (t / 0.15) ** 1.4) * math.exp(-t * 1.1)
            else:
                amp = min(1.0, t / 0.08) * math.exp(-t * 1.0)
            samples.append(math.tanh(val * 0.24) * amp * vel * 0.8)
        return cls._create_wav(samples)

    @classmethod
    def generate_orchestral_brass(cls, freq=220.0, duration=0.7, articulation="legato", dynamic="mf"):
        """Majestic orchestral brass fanfare (horns & trumpets) with bright harmonic envelope."""
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        vel = 1.0 if dynamic in ("f", "ff", "fff") else (0.85 if dynamic == "mf" else 0.65)
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            f = freq
            b1 = math.sin(2.0 * math.pi * f * t)
            b2 = 0.6 * math.sin(2.0 * math.pi * (f * 2.0) * t)
            b3 = 0.4 * math.sin(2.0 * math.pi * (f * 3.0) * t)
            b4 = 0.25 * math.sin(2.0 * math.pi * (f * 4.0) * t)
            raw = b1 + b2 + b3 + b4
            if articulation == "staccato":
                amp = math.exp(-t * 18.0)
            elif articulation == "marcato":
                amp = 1.2 * math.exp(-t * 2.5)
            else:
                amp = min(1.0, t / 0.06) * math.exp(-t * 1.4)
            val = math.tanh(raw * 1.4) * amp * vel * 0.85
            samples.append(val)
        return cls._create_wav(samples)
