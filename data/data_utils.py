import numpy as np
import music21
import json

def get_oct_and_chroma(p):
    oct = int(p) / 12 + 1
    chr = p % 12
    return oct, chr


def chord_to_binary(list_notes):
    chroma_vec = np.zeros(12)
    for p in list_notes:
        chr = p % 12
        chroma_vec[chr] = 1
    return chroma_vec


def insert_rests(note_track):
    note_id = 0
    while note_id < len(note_track):
        note = note_track[note_id]
        if note_id < len(note_track) - 1:
            next_note = note_track[note_id + 1]
            note_end_time = note["time"] + note["duration"]
            rest_time = next_note["time"] - note_end_time
            if rest_time > 0:
                note_track.insert(
                    note_id + 1,
                    {
                        "time": note_end_time,
                        "pitch": -1,
                        "duration": rest_time,
                        "velocity": 64,
                    },
                )
                note_id += 1
        note_id += 1
    return note_track

def note_chord_to_midi(
    note_list, chord_list, time_signature_list, out_path="test.mid", resolution=24
):
#     print(note_list)
    part_notes = music21.stream.Part()
    part_chords = music21.stream.Part()
    for note in note_list:
        if note.pitch == -1:
            note_m21 = music21.note.Rest()
        else:
            note_m21 = music21.note.Note(int(note.pitch))
        note_m21.quarterLength = float(note.duration) / resolution
        part_notes.append(note_m21)
    
    if chord_list[0].time > 0:
        chord_rest = music21.note.Rest()
        chord_rest.quarterLength = float(chord_list[0].time) / resolution
        part_chords.append(chord_rest)
    for i, chord in enumerate(chord_list):
        chord.pitches = [int(p) for p in chord.pitches]
        chord_m21 = music21.chord.Chord(chord.pitches)
        chord_m21.quarterLength = float(chord.duration) / resolution
        part_chords.append(chord_m21)

    stream = music21.stream.Stream()

    for time_signature in time_signature_list:
        pos = float(time_signature.time) / resolution
        value = (
            str(int(time_signature.numerator))
            + "/"
            + str(int(time_signature.denominator))
        )
        part_notes.insert(pos, music21.meter.TimeSignature(value))
        part_chords.insert(pos, music21.meter.TimeSignature(value))

    score = music21.stream.Score([part_notes, part_chords])

    mf = music21.midi.translate.streamToMidiFile(score)
    mf.open(out_path, "wb")
    mf.write()
    mf.close()

def notes_chord_to_midi(
    list_of_note_list, chord_list, time_signature_list, out_path="test.mid", resolution=24
):
    N_note_list = len(list_of_note_list)
    parts_notes = [music21.stream.Part() for _ in range(N_note_list)]
    for i in range(N_note_list):
        if list_of_note_list[i][0].time > 0:
            note_rest = music21.note.Rest()
            note_rest.quarterLength = float(list_of_note_list[i][0].time) / resolution
            parts_notes[i].append(note_rest)
        for note in list_of_note_list[i]:
            if note.pitch == -1:
                note_m21 = music21.note.Rest()
            else:
                note_m21 = music21.note.Note(int(note.pitch))
            note_m21.quarterLength = float(note.duration) / resolution
            parts_notes[i].append(note_m21)
    
    part_chords = music21.stream.Part()
    if chord_list[0].time > 0:
        chord_rest = music21.note.Rest()
        chord_rest.quarterLength = float(chord_list[0].time) / resolution
        part_chords.append(chord_rest)
    for i, chord in enumerate(chord_list):
        chord.pitches = [int(p) for p in chord.pitches]
        if -1 in chord.pitches:
            chord_m21= music21.note.Rest()
        else:
            chord_m21 = music21.chord.Chord(chord.pitches)
        chord_m21.quarterLength = float(chord.duration) / resolution
        part_chords.append(chord_m21)

    stream = music21.stream.Stream()

    for time_signature in time_signature_list:
        pos = float(time_signature.time) / resolution
        value = (
            str(int(time_signature.numerator))
            + "/"
            + str(int(time_signature.denominator))
        )
        for part_notes in parts_notes:
            part_notes.insert(pos, music21.meter.TimeSignature(value))
        part_chords.insert(pos, music21.meter.TimeSignature(value))
    
    score = music21.stream.Score(parts_notes + [part_chords])

    mf = music21.midi.translate.streamToMidiFile(score)
    mf.open(out_path, "wb")
    mf.write()
    mf.close()

def note_chord_to_json(
    note_list, chord_list, time_signature_list, title="unknown", out_path="test.json",
):
    piece = {
        "metadata": {"title":title},
        "tracks": [{
            "chords":[],
            "notes":[]
            }
        ],
        "time_signatures": [],
    }
    note_list_new = [None]*len(note_list)
    chord_list_new = [None]*len(chord_list)
    time_signature_list_new = [None]*len(time_signature_list)
    for i in range(len(note_list)):
        note_list_new[i] = {"pitch": note_list[i].pitch,
                            "duration": note_list[i].duration}
    for i in range(len(chord_list)):
        chord_list_new[i] = {"pitches": chord_list[i].pitches,
                             "duration": chord_list[i].duration,
                             "time": chord_list[i].time}
    for i in range(len(time_signature_list)):
        time_signature_list_new[i] = {"numerator": time_signature_list[i].numerator,
                             "denominator": time_signature_list[i].denominator,
                             "time": time_signature_list[i].time}
    piece["tracks"][0]["chords"] = chord_list_new
    piece["tracks"][0]["notes"] = note_list_new
    piece["time_signatures"] = time_signature_list_new
    with open(out_path, 'w') as f:
        json.dump(piece, f)
        
def rectify_note_durs(note_track):
    note_track_rec = []
    for i in range(len(note_track)):
        if "duration" in note_track[i]:
            if note_track[i]["duration"]>0:
                note_track_rec.append(note_track[i])
    return note_track_rec
    
def rectify_chord_durs(chord_track, max_time, resolution=24):
    for i in range(len(chord_track)):
        if i < len(chord_track) - 1:
            chord_track[i]["duration"] = (
                chord_track[i + 1]["time"] - chord_track[i]["time"]
            )
        else:
            chord_track[i]["duration"] = max_time - chord_track[i]["time"] + resolution
    return chord_track

def rectify_times(track):
    if "time" not in track[0]:
        track[0]["time"] = 0
    for i in range(1,len(track)):
        if "time" not in track[i]:
            track[i]["time"] = track[i-1]["time"] + track[i-1]["duration"]
    return track

def get_max_time(notes, chords):
    note_max = notes[-1]["time"] + notes[-1]["duration"]
    chord_max = chords[-1]["time"] + chords[-1]["duration"]
    return max(min(note_max, chord_max + 192), chord_max)


# p is a tensor of integer in size (*), rest note pitch is -1
# output a tensor of  integers in size (*), resto note pitch is 0, and min_pitch is 1, and so on
def pitch_num_to_id(p, min_pitch=55-6):
    ids = (p + 0).long()
    ids[ids >= 0] = ids[ids >= 0] - min_pitch
    ids = ids + 1
    return ids


def id_to_pitch_num(ids, min_pitch=55-6):
    p = (ids - 1).long()
    p[p >= 0] = p[p >= 0] + min_pitch
    return p

def pitch_num_to_id_np(p, min_pitch=55-6):
    ids = np.array(p + 0)
    ids[ids >= 0] = ids[ids >= 0] - min_pitch
    ids = ids + 1
    return ids

def id_to_pitch_num_np(ids, min_pitch=55-6):
    p = np.array(ids - 1)
    p[p >= 0] = p[p >= 0] + min_pitch
    return p
