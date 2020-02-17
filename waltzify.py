import sys
from mido import Message, MetaMessage, MidiFile, MidiTrack

try:
    assert(len(sys.argv) in [5, 6])
    S_MIDI = sys.argv[1]
    D_MIDI = sys.argv[2]

    S_BEATS_PER_MEASURE = 4
    D_BEATS_PER_MEASURE = 3
    S_BEAT_OFFSET = int(sys.argv[3])
    S_TEMPO_SCALE = 1/float(sys.argv[4])

    DELETE_FOURTH_MEASURE = (len(sys.argv) == 6)
except:
    print("Usage: waltzify.py source destination offset speed [skip]")
    exit(1)


src = MidiFile(S_MIDI)
dst = MidiFile()

def transform_ticks(s_ticks):
    s_total_beats = (s_ticks / src.ticks_per_beat) + (S_BEATS_PER_MEASURE - S_BEAT_OFFSET)
    s_measures = s_total_beats // S_BEATS_PER_MEASURE
    s_beats = s_total_beats - s_measures * S_BEATS_PER_MEASURE
    d_measures = s_measures
    if DELETE_FOURTH_MEASURE:
        d_beats = s_beats if s_beats < 3 else 3
    else:
        d_beats = s_beats if s_beats < 2 else 2 + (s_beats - 2)/2
    d_total_beats = d_measures * D_BEATS_PER_MEASURE + d_beats
    return int(S_TEMPO_SCALE * ((d_total_beats * src.ticks_per_beat) - (S_BEATS_PER_MEASURE - S_BEAT_OFFSET)))

for i, s_track in enumerate(src.tracks):
    d_track = MidiTrack()
    dst.tracks.append(d_track)
    s_ticks = 0
    d_ticks = 0
    for s_msg in s_track:
        if s_msg.type == 'unknown_meta':
            continue
        s_dt = s_msg.time
        d_dt = transform_ticks(s_ticks + s_dt) - transform_ticks(s_ticks)
        d_msg = s_msg.copy(time = d_dt)
        d_track.append(d_msg)
        s_ticks += s_msg.time
        d_ticks += d_msg.time
    # print(d_ticks - transform_ticks(s_ticks))

dst.save(D_MIDI)