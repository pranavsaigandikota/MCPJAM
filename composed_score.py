"""An original, deliberately scored 16-bar dark piano/808 dance arrangement."""


def score_bar(note, bar, root, section):
    beat = bar * 4
    transpose = root - 2  # Written in D minor, transposable by the MCP tool.
    # Dm(add9), Bbmaj7, Gm(add9), Asus -> A: common tones keep voices smooth.
    voicings = [[50,57,64,65], [46,57,62,65], [43,58,62,69], [45,57,61,64]]
    index = 0 if bar >= 14 else (bar // 2) % 4
    chord = voicings[index]
    quiet = section in ('intro', 'breakdown', 'outro')
    for voice, pitch in enumerate(chord):
        note('keys',pitch+transpose,beat+voice*.025,3.7,49 if quiet else 66)
    # Two sustained inner voices, rather than a full string block on every beat.
    for pitch in chord[1:3]:
        note('pad',pitch+transpose,beat+.07,3.8,40 if quiet else 52)
    # A question, an answer, and a cadence. Rests separate the phrases.
    phrases = [
        [(0,69,1.35),(1.75,72,.55),(2.5,74,1.35)],
        [(.5,77,.75),(1.5,76,.55),(2.5,74,1.35)],
        [(0,69,1.65),(2.25,65,.65),(3.25,67,.55)],
        [(.25,69,1.1),(1.75,73,.7),(3,74,.8)],
    ]
    if bar not in (0,8):
        for i,(offset,pitch,length) in enumerate(phrases[bar%4]):
            if bar == 15:
                break
            note('lead',pitch+transpose,beat+offset,length,
                 (63 if quiet else 78) - i*4)
    if bar == 15:
        note('lead',74+transpose,beat,3.6,60)
    if section in ('intro','breakdown','outro'):
        return
    bass_root = [26,34,31,33][index] + transpose
    for offset,length in ((0,1.55),(1.75,.9),(3, .8)):
        note('bass',bass_root,beat+offset,length,102)
    for offset in (0,1,2,3):
        note('drums',36,beat+offset,.12,108 if offset in (0,2) else 94)
    for offset in (1,3):
        note('drums',38,beat+offset+.008,.12,85)
        note('drums',39,beat+offset+.018,.12,46)
    for i in range(8):
        note('drums',42,beat+i*.5,.06,57 if i%2 else 38)
    if section == 'drop':
        for offset in (1.5,3.5):
            note('drums',46,beat+offset,.12,37)
    # One restrained pickup into the drop; no random fills or octave jumps.
    if bar == 3:
        for i in range(4):
            note('drums',38,beat+3+i*.25,.06,32+i*9)
