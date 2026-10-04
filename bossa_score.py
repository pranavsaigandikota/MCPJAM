"""Original playful bossa nova with nylon guitar and a quiet root/fifth bass."""


def bossa_bar(note, bar, root, section):
    beat = bar * 4
    transpose = root  # Written in C major.
    # Cmaj9, A minor 9, D minor 9, G13: connected upper voices.
    chords = [[52,55,59,62],[52,55,59,60],[53,57,60,64],[53,57,59,64]]
    chord = chords[bar % 4]
    bass = [36,33,38,31][bar % 4] + transpose
    quiet = section in ('intro','outro')
    for offset in (0,1.5,2.5):
        for voice,pitch in enumerate(chord):
            note('pad',pitch+transpose,beat+offset+voice*.012,.65,55 if quiet else 64)
    for offset,pitch in ((0,bass),(2,bass+7)):
        note('bass',pitch,beat+offset,1.65,62)
    if section != 'intro':
        phrases = [
            [(0,76,.75),(1,74,.45),(1.75,72,1),(3,71,.7)],
            [(.5,72,.6),(1.5,76,.7),(2.5,79,1.1)],
            [(0,77,.8),(1.5,76,.45),(2.25,74,1.1)],
            [(.5,71,.6),(1.5,69,.5),(2.5,67,1.2)],
        ]
        for offset,pitch,length in phrases[bar%4]:
            note('lead',pitch+transpose,beat+offset,length,64 if quiet else 73)
    if bar % 2 == 0:
        for pitch in chord[1:3]:
            note('keys',pitch+12+transpose,beat+1.5,1.7,42)
    for offset in (0,2):
        note('drums',36,beat+offset,.12,38)
    for offset in (.75,2,3.5):
        note('drums',37,beat+offset,.1,46)
    for i in range(8):
        note('drums',70,beat+i*.5,.06,31 if i%2 else 39)
