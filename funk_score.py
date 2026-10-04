"""Original syncopated funk-pop score with restrained bass and brass answers."""


def funk_bar(note, bar, root, section):
    beat = bar * 4
    transpose = root - 4
    # Em9 -> A13, voiced around common tones, with an occasional Dmaj9 lift.
    chords = [[55,59,62,66],[55,61,66,71],[54,57,61,64],[55,61,66,71]]
    index = bar % 4
    chord = chords[index]
    bass = [40,33,38,33][index] + transpose
    quiet = section in ('intro','breakdown','outro')
    for offset in ((.5,2.5) if quiet else (.5,1.75,2.5,3.75)):
        for pitch in chord:
            note('keys',pitch+transpose,beat+offset,.24,62 if quiet else 76)
    if section != 'intro':
        for i in range(8):
            if i in (2,6):
                continue
            for pitch in chord[:3]:
                note('pad',pitch+12+transpose,beat+i*.5+.02,.10,45 if i%2 else 34)
    for offset,pitch,length,velocity in [(0,bass,.65,83),(1.5,bass+12,.23,68),
                                        (2,bass,.55,77),(3.25,bass+7,.22,65),(3.75,bass+12,.18,67)]:
        note('bass',pitch,beat+offset,length,velocity)
    for offset in ((0,2) if quiet else (0,1.75,2,3.5)):
        note('drums',36,beat+offset,.12,93)
    for offset in (1,3):
        note('drums',38,beat+offset+.006,.1,83)
        note('drums',39,beat+offset+.012,.1,48)
    for i in range(8):
        note('drums',42,beat+i*.5,.05,43 if i%2 else 58)
    if not quiet:
        note('drums',46,beat+3.5,.12,45)
    # Original two-bar call and response; silence leaves room for the rhythm.
    if section in ('groove','lift') and bar%2==0:
        for offset,pitch,length in [(0,71,.28),(.75,74,.24),(1.5,76,.55),(3,74,.4)]:
            note('lead',pitch+transpose,beat+offset,length,76)
    elif section in ('groove','lift'):
        for offset,pitch,length in [(1.5,69,.25),(2.25,66,.25),(3,64,.7)]:
            note('lead',pitch+transpose,beat+offset,length,67)
