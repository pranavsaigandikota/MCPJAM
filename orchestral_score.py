"""Original fast cinematic orchestral score inspired by layered string writing."""


def orchestral_bar(note, bar, root, section, rng, mood='dramatic', melody_style='smooth'):
    beat = bar * 4
    transposition = root - 2
    chord_roots = [50, 46, 53, 48]
    chord_root = chord_roots[bar % 4] + transposition
    minor = mood != 'happy' and bar % 4 in (0, 1)
    third = 3 if minor else 4
    chord = [chord_root, chord_root + third, chord_root + 7]

    # Short piano ostinato gives the fast pulse; strings carry the long arc.
    pattern = [0, 7, 3, 7, 0, 7, 3, 10]
    for index, interval in enumerate(pattern):
        pitch = chord_root + 12 + interval
        if section == 'climax' and index in (3, 7):
            pitch += 12
        note('keys', pitch, beat + index * 0.5, 0.38, 68 + (index % 2) * 10)

    for pitch in chord:
        note('pad', pitch + 12, beat, 3.85, 62 if section != 'climax' else 78)
    if melody_style == 'jumpy':
        melody = [chord_root + 24, chord_root + 12, chord_root + 19, chord_root + 29,
                  chord_root + 17, chord_root + 26]
        for index, pitch in enumerate(melody):
            note('lead', pitch, beat + index * 0.58, .42 if index < 5 else .9,
                 82 if section == 'climax' else 68 + index * 3)
    else:
        for index, pitch in enumerate((chord_root + 12, chord_root + 7, chord_root + 12, chord_root + 19)):
            note('lead', pitch, beat + index * 0.75, 1.3 if index < 3 else 2.0,
                 76 if section == 'climax' else 60 + index * 4)
    for offset in (0, 2):
        note('bass', chord_root - 12, beat + offset, 1.75, 78)

    if section != 'intro' and mood != 'happy':
        for offset in (0, 1, 2, 3):
            note('drums', 36, beat + offset, .12, 72 if offset % 2 else 92)
        for offset in (1, 3):
            note('drums', 38, beat + offset, .12, 82)
    if section == 'climax' and bar % 2 == 1:
        note('drums', 49, beat, .7, 92)
