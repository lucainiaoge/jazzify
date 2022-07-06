from config import config
from data.data_utils import chord_to_binary, pitch_num_to_id_np, id_to_pitch_num_np, notes_chord_to_midi
from music_struct import Note, Piece, Chord, TimeSignature, Tempo
from rules.pitch_names import *
from rules.chord2symbol import *
from rules.chord_symbols import *
from rules.intervals import *
from rules.find_key import *
from rules.extend_chords import *

from math import ceil
import numpy as np
from copy import deepcopy
import random
import json
import os

def insert_rests_structed(note_track):
    note_id = 0
    while note_id < len(note_track):
        note = note_track[note_id]
        if note_id < len(note_track) - 1:
            next_note = note_track[note_id + 1]
            note_end_time = note.time + note.duration
            rest_time = next_note.time - note_end_time
                
            if rest_time > 0:
                if hasattr(note, "pitch"):
                    note_track.insert(
                        note_id + 1,
                        Note(**{
                            "time": note_end_time,
                            "pitch": -1,
                            "duration": rest_time,
                            "velocity": 64,
                        }),
                    )
                elif hasattr(note, "pitches"):
                    note_track.insert(
                        note_id + 1,
                        Chord(**{
                            "time": note_end_time,
                            "pitches": [-1],
                            "duration": rest_time,
                            "velocity": 64,
                        }),
                    )
                note_id += 1
        note_id += 1
    return note_track

def reduce_chord_into_chroma(chord_notes):
    chroma = []
    for note in chord_notes:
        if note%12 not in chroma:
            chroma.append(note%12)
    return chroma

STYLES = [
    "swing",
    "bossa",
]

# 24 = 16 + 8
# when using: one can anticipatify normal rhythm, and can break 4th notes into successive 8th swing notes
SWING_VOICING_RHYTHM_TEMPLATES_44 = {
    "normal": [
        [(16,8+24), (48,16)],
        [(16,8+24), (48+16,8)],
        [(16,8), (48,24)],
    ],
    "anticipate": [
        [(16,8), (24+16,8), (48+16,8), (72+16,8)],
        [(24+16,8), (72+16,8)],
    ],
    "holding": [
        [(0,24), (24+16,8), (48+16,8)],
        [(0,16), (16,8+16), (48+16,8)],
        [(0,24), (24+16,8)],
    ],
    "coda": [
        [(0,96)],
    ],
}
N_TEMPLATE_PER_SWING_VOICING_RHYTHM_44 = {
    tag:len(templates) for tag,templates in SWING_VOICING_RHYTHM_TEMPLATES_44.items()
}

def randomly_partite_4th_note_into_swing_8ths(rhythm_template, p = 0.4):
    new_rhythm_template = rhythm_template[:]
    i = 0
    while i<len(rhythm_template):
        time, dur = rhythm_template[i]
        if time%24 == 0 and dur == 24:
            if np.random.random() < p:
                new_rhythm_template[i] = (time, 16)
                new_rhythm_template.insert(i+1, (time+16, 8))
                i += 1
        i += 1
    return new_rhythm_template

def randomly_acticipatify_rhythm(rhythm_template, p = 0.4):
    new_rhythm_template = rhythm_template[:]
    last_time, last_dur = rhythm_template[-1]
    if last_time + last_dur <= 72+16:
        if np.random.random() < p:
            new_rhythm_template.append((72+16,8))
    return new_rhythm_template

def can_be_anticipation_rhythm(rhythm_template):
    if len(rhythm_template) > 0:
        return rhythm_template[-1] == (72+16,8)
    else:
        return False
def can_be_holding_rhythm(rhythm_template):
    if len(rhythm_template) > 0:
        return rhythm_template[0][0] == 0
    else:
        return False

def rhythm_tag_change_44(rhythm_tag):
    if rhythm_tag == "normal":
        if np.random.random() < 0.3:
            rhythm_tag = "anticipate"
    elif rhythm_tag == "anticipate":
        p = np.random.random() < 0.8
        if p < 0.8:
            rhythm_tag = "holding"
        elif p < 0.9:
            rhythm_tag = "anticipate"
        else:
            rhythm_tag = "normal"
    elif rhythm_tag == "holding":
        if np.random.random() < 0.8:
            rhythm_tag = "normal"
    return rhythm_tag
            

SWING_VOICING_RHYTHM_TEMPLATES_34 = {
    "normal": [
        [(16,8+16), (48,16)],
        [(24,48)],
        [(24,24), (48+16,8)],
    ],
    "symcopate": [
        [(0,24+12), (24+12,24+12)],
        [(0,24), (24+16,8)],
    ],
    "coda": [
        [(0,72)],
    ],
}
N_TEMPLATE_PER_SWING_VOICING_RHYTHM_34 = {
    tag:len(templates) for tag,templates in SWING_VOICING_RHYTHM_TEMPLATES_34.items()
}

CONTOUR_UP = 1
CONTOUR_DOWN = -1
CONTOUR_STAY = 0

def rhythm_tag_change_34(rhythm_tag):
    if rhythm_tag == "normal":
        if np.random.random() < 0.3:
            rhythm_tag = "symcopate"
    elif rhythm_tag == "symcopate":
        if np.random.random() < 0.2:
            rhythm_tag = "normal"
    return rhythm_tag


BOSSA_VOICING_RHYTHM_TEMPLATES = {
    "measure1": [
        [(0,24), (24,24), (48+12,12), (72+12,12)],
        [(24,24), (48+12,12), (72+12,12)],
        [(0,36), (36,12), (72+12,12), (72+12,12)],
    ],
    "measure2": [
        [(12,36), (48,24), (72,24)],
        [(12,12), (36,48+12)],
    ],
    "coda": [
        [(0,96)],
    ],
}
N_TEMPLATE_PER_BOSSA_VOICING_RHYTHM = {
    tag:len(templates) for tag,templates in BOSSA_VOICING_RHYTHM_TEMPLATES.items()
}
def rhythm_tag_change_bossa_44(rhythm_tag):
    if rhythm_tag == "measure1":
        rhythm_tag = "measure2"
    elif rhythm_tag == "measure2":
        rhythm_tag = "measure1"
    return rhythm_tag


def get_onset_duration_track_out_of_rhythm_templates(rhythm_templates, template_durations, template_start_time = 0, anticipate = True):
    onset_duration_track = []
    anticipation_track = []
    prev_is_anticipation = False
    for rhythm_template, template_duration in zip(rhythm_templates, template_durations):
        if prev_is_anticipation and anticipate:
            holding = can_be_holding_rhythm(rhythm_template)
            if holding:
                onset_duration_track[-1] = (onset_duration_track[-1][0], onset_duration_track[-1][1]+rhythm_template[0][1])
                anticipation_track[-1] = True
                this_rhythm_template = rhythm_template[1:]
        else:
            this_rhythm_template = rhythm_template[:]
        
        for onset, duration in this_rhythm_template:
            onset_duration_track.append((onset + template_start_time, duration))
            anticipation_track.append(False)
        
        template_start_time += template_duration
        
        prev_is_anticipation = can_be_anticipation_rhythm(rhythm_template)
    return onset_duration_track, anticipation_track

def get_onset_duration_track_out_of_rhythm_templates_bossa(rhythm_templates, template_durations, template_start_time = 0):
    onset_duration_track = []
    for rhythm_template, template_duration in zip(rhythm_templates, template_durations):
        for onset, duration in rhythm_template[:]:
            onset_duration_track.append((onset + template_start_time, duration))
        template_start_time += template_duration
    return onset_duration_track

def to_int_or_remains(s):
    try:
        return int(s)
    except ValueError:
        return s

    
def get_5th_root_note(chord_root, chord_quality):
    if DIM not in chord_quality and AUG not in chord_quality:
        bass_note = chord_root + INT_5
    elif AUG in chord_quality:
        bass_note = chord_root + INT_a5
    else:
        bass_note = chord_root + INT_a4
    return bass_note

def get_leading_bass_note(next_chord_bass, p_above=0.6):
    p = np.random.random()
    if p < p_above:
        bass_note = next_chord_bass + INT_m2
    else:
        bass_note = next_chord_bass - INT_m2
    return bass_note

def get_root_or_5th(chord_root, chord_quality, p_root = 0.3):
    p = np.random.random()
    if p < p_root:
        bass_note = chord_root
    else:
        bass_note = get_5th_root_note(chord_root, chord_quality)
    return bass_note

def get_leading_or_5th(next_chord_bass, chord_root, chord_quality, p_above=0.6, p_leading = 0.8):
    p = np.random.random()
    if p < p_leading:
        bass_note = get_leading_bass_note(next_chord_bass, p_above=p_above)
    else:
        bass_note = get_5th_root_note(chord_root, chord_quality)
    return bass_note

def determine_note_contour(prev_pitch, this_pitch):
    if prev_pitch > this_pitch:
        return CONTOUR_DOWN
    elif prev_pitch < this_pitch:
        return CONTOUR_UP
    else:
        return CONTOUR_STAY
    
class Jazzifier:
    def __init__(self, piece, style = "swing", bass_max = 54, bass_min = 24, voicing_min = 38, voicing_max = 64, p_remove_note = 0.1, max_voicing_jump = 6, verbose = False):
        if style == "bossa" and piece.time_signatures[0].numerator % 3 == 0:
            raise ValueError("impossible to convert this piece into bossa style...")
        
        self.piece = piece
        self.name = self.piece.name[:-5] + "_" + self.piece.title
        
        self.N_notes = len(piece.notes)
        self.note_time_track = [None]*self.N_notes
        self.note_duration_track = [None]*self.N_notes
        self.note_pitch_track = [None]*self.N_notes
        for i,note_obj in enumerate(piece.notes):
            self.note_time_track[i] = note_obj.time
            self.note_duration_track[i] = note_obj.duration
            self.note_pitch_track[i] = note_obj.pitch
            
        self.N_chords = len(piece.chords)
        self.chord_time_track = [None]*self.N_chords
        self.chord_duration_track = [None]*self.N_chords
        self.chord_notes_track = [None]*self.N_chords
        for i,chord_obj in enumerate(piece.chords):
            self.chord_time_track[i] = chord_obj.time
            self.chord_duration_track[i] = chord_obj.duration
            self.chord_notes_track[i] = chord_obj.pitches
        
        '''
        self.melody_aware_chord_track = self.get_melody_aware_chords()
        self.melody_aware_chord_notes_track = [None]*self.N_chords
        for i in range(self.N_chords):
            self.melody_aware_chord_notes_track[i] = self.melody_aware_chord_track[i].pitches
        '''
        self.melody_aware_chord_notes_track = [None]*self.N_chords
        for i in range(self.N_chords):
            self.melody_aware_chord_notes_track[i] = piece.chords[i].pitches
        
        self.root_list_orig, self.symb_list_orig, self.bass_list_orig = get_root_symb_bass_from_progression(self.chord_notes_track)
        self.root_list, self.symb_list, self.bass_list = get_root_symb_bass_from_progression(self.melody_aware_chord_notes_track)
        for i in range(self.N_chords):
            if UNK_CHORD in self.symb_list[i]:
                self.root_list[i] = self.root_list_orig[i]
                self.symb_list[i] = self.symb_list_orig[i]
                self.bass_list[i] = self.bass_list_orig[i]
                self.melody_aware_chord_notes_track[i] = self.chord_notes_track[i]
                
        self.function_key_tuples = find_key_given_chord_track(self.melody_aware_chord_notes_track)
        
        if verbose:
            func_key_strings = function_key_tuples_to_string_tuples(self.function_key_tuples, self.root_list, self.symb_list)
            chord_symbols_track = [None]*self.N_chords
            melody_aware_chord_notes_name_track = [None]*self.N_chords
            for i in range(self.N_chords):
                chord_symbols_track[i] = form_chord_name(self.root_list[i], self.symb_list[i], self.bass_list[i])
                melody_aware_chord_notes_name_track[i] = [PITCH_NUM_2_NAME[note%12] for note in self.melody_aware_chord_notes_track[i]]
            to_print = list(zip(melody_aware_chord_notes_name_track, chord_symbols_track,func_key_strings))
            for element in to_print:
                print(element)
        
        for i in range(self.N_chords):
            function, key = self.function_key_tuples[i]
            function = to_int_or_remains(function)
            key = to_int_or_remains(key)
            self.function_key_tuples[i] = (function, key)
                
        self.bassline = self.get_bassline()
        
        self.voicings = self.get_extended_chords_and_voicings(
            bass_max = bass_max, voicing_min = voicing_min, voicing_max = voicing_max, 
            p_remove_note = p_remove_note, max_voicing_jump = max_voicing_jump, verbose = verbose
        )
        
    def get_melody_aware_chords(self):
        i_chord = 0
        i_note = 0
        self.melody_aware_chord_track = deepcopy(self.piece.chords[:])
        while i_chord < self.N_chords and i_note < self.N_notes:
            chord_start_time = self.chord_time_track[i_chord]
            chord_end_time = self.chord_time_track[i_chord] + self.chord_duration_track[i_chord]
            chord_chorma = reduce_chord_into_chroma(self.melody_aware_chord_track[i_chord].pitches)
            while i_note < self.N_notes:
                note_time = self.note_time_track[i_note]
                
                if note_time < chord_end_time and self.note_pitch_track[i_note]%12 not in chord_chorma:
                    self.melody_aware_chord_track[i_chord].pitches.append(self.note_pitch_track[i_note])
                i_note += 1
                
                
            i_chord += 1
        return self.melody_aware_chord_track
    
    def get_bassline(self):
        self.bassline = self.root_list[:]
        for i in range(self.N_chords):
            if self.bass_list[i] is not None:
                self.bassline[i] = self.bass_list[i]
        return self.bassline
    
    def find_first_downbeat_time(self):
        return self.piece.chords[0].time
    
    def get_extended_chords_and_voicings(self, bass_max = 36, voicing_min = 38, voicing_max = 64, p_remove_note = 0.1, max_voicing_jump = 6, verbose = False):
        self.extended_chord_notes_track = self.chord_notes_track[:]
        self.voicings = [None]*self.N_chords
        for i in range(self.N_chords):
            chord_notes = self.extended_chord_notes_track[i]
            chord_type = self.symb_list[i]
            chord_root = self.root_list[i]
            chord_bass = self.bass_list[i]
            chord_root_name = PITCH_NUM_2_NAME[chord_root%12]
            key = self.function_key_tuples[i][1]
            extended = extend_chord(chord_type, chord_root, key)[0]
            self.bassline[i], self.voicings[i] = chord_to_voicing(chord_root, extended, chord_bass, 
                chord_notes = chord_notes,
                invert_voicing_times = 2 * int(i%2==0), 
                bass_max = bass_max, 
                voicing_min = voicing_min, 
                p_remove_note = p_remove_note
            )
            
            if i >= 1:
                inv_counter = 0
                while len(self.voicings[i]) >= 1 and len(self.voicings[i-1]) >= 1 and self.voicings[i][0] >= voicing_min and inv_counter <= 2:
                    if self.voicings[i][0] - self.voicings[i-1][0] > max_voicing_jump:
                        self.voicings[i] = inv_invert_no_chrma24(self.voicings[i], time_inversion = 1)
                    elif self.voicings[i][0] - self.voicings[i-1][0] < -max_voicing_jump:
                        self.voicings[i] = invert_no_chrma24(self.voicings[i], time_inversion = 1)
                    else:
                        break
                    inv_counter += 1
                
            inv_counter = 0
            while len(self.voicings[i]) >= 1 and self.voicings[i][-1] >= voicing_max and inv_counter <= 2:
                self.voicings[i] = inv_invert_no_chrma24(self.voicings[i], time_inversion = 1)
                inv_counter += 1
            resulting_chord_notes = [self.bassline[i]] + self.voicings[i]
            if verbose:
                resulting_chord = [PITCH_NUM_2_NAME[note%12] for note in resulting_chord_notes]
                print(chord_root_name, extended, resulting_chord)
                
            self.extended_chord_notes_track[i] = resulting_chord_notes[:]
        return self.voicings

    def get_meter_information(self,i_meter):
        meter_obj = self.piece.time_signatures[i_meter]
        meter_start_time = meter_obj.time
        if i_meter == len(self.piece.time_signatures) - 1:
            meter_end_time = max([self.note_time_track[-1]+self.note_duration_track[-1],
                                  self.chord_time_track[-1]+self.chord_duration_track[-1]])
        else:
            meter_end_time = self.piece.time_signatures[1].time
        meter_duration = meter_end_time - meter_start_time
        numerator, denominator = meter_obj.numerator, meter_obj.denominator
        measure_length = int(24 * numerator * 4/denominator)
        n_measures = ceil(meter_duration/measure_length)
        return meter_start_time, meter_end_time, numerator, denominator, measure_length, n_measures
    
    def get_chord_timing_information(self, i_chord):
        chord_start = self.chord_time_track[i_chord]
        if i_chord < self.N_chords - 1:
            next_chord_start = self.chord_time_track[i_chord+1]
        else:
            measure_length = int(24 * self.piece.time_signatures[-1].numerator * 4/self.piece.time_signatures[-1].denominator)
            next_chord_start = chord_start + measure_length
        chord_end = chord_start + self.chord_duration_track[i_chord]
        return chord_start, chord_end, next_chord_start
    
    def get_chord_meter(self, i_chord):
        chord_start, chord_end, next_chord_start = self.get_chord_timing_information(i_chord)
        for i_meter,meter_obj in enumerate(self.piece.time_signatures):
            meter_start_time, meter_end_time, numerator, denominator, measure_length, n_measures = self.get_meter_information(i_meter)
            if chord_start < meter_end_time:
                return numerator, denominator
    
    def output_json(self, out_path="test.json"):
        if not (hasattr(self, 'modified_note_track') and hasattr(self, 'bass_track')):
            print("Please use the jazzifier in a certain style, e.g., Swingifier or Bossaifier.")
            return
        
        new_piece = {
            "metadata": {"title":self.piece.title},
            "tracks": [{
                "notes":[],
                "voicings":[],
                "basses":[],
                }
            ],
            "time_signatures": [],
            "chord_symbols": [], # list of triples (root, symbol, bass)
            "tempos":[],
            "beats":[],
        }
        # swingified notes
        note_list_new = [None]*len(self.modified_note_track)
        for i in range(len(self.modified_note_track)):
            note_list_new[i] = {"pitch": self.modified_note_track[i].pitch,
                                "duration": self.modified_note_track[i].duration}
        new_piece["tracks"][0]["notes"] = note_list_new
        
        # voicings
        voicing_list = [None]*len(self.voicing_track)
        for i in range(len(self.voicing_track)):
            voicing_list[i] = {"pitches": self.voicing_track[i].pitches,
                                 "duration": self.voicing_track[i].duration,
                                 "time": self.voicing_track[i].time}
        new_piece["tracks"][0]["voicings"] = voicing_list
        
        # basses
        bass_list = [None]*len(self.bass_track)
        for i in range(len(self.bass_track)):
            bass_list[i] = {"pitch": self.bass_track[i].pitch,
                                "duration": self.bass_track[i].duration}
        new_piece["tracks"][0]["basses"] = bass_list
        
        # time signatures
        time_signature_list_new = [None]*len(self.piece.time_signatures)
        for i in range(len(self.piece.time_signatures)):
            time_signature_list_new[i] = {"numerator": self.piece.time_signatures[i].numerator,
                                 "denominator": self.piece.time_signatures[i].denominator,
                                 "time": self.piece.time_signatures[i].time}
        new_piece["time_signatures"] = time_signature_list_new
        
        # chord symbols
        chord_symbol_list = [None]*self.N_chords
        for i in range(self.N_chords):
            chord_symbol_list[i] = (self.root_list[i], self.symb_list[i], self.bass_list[i])
        new_piece["chord_symbols"] = chord_symbol_list
        
        # tempos
        tempo_list_new = [None]*len(self.piece.tempos)
        for i in range(len(self.piece.tempos)):
            tempo_list_new[i] = {"qpm": self.piece.tempos[i].qpm,
                                 "time": self.piece.tempos[i].time}
        new_piece["tempos"] = tempo_list_new
        
        # downbeats
        new_piece["beats"] = self.piece.beats
        with open(out_path, 'w') as f:
            json.dump(new_piece, f)
    
    
class Swingifier(Jazzifier):
    def __init__(self, piece, bass_max = 54, bass_min = 24, voicing_min = 38, voicing_max = 64, p_remove_note = 0.1, max_voicing_jump = 6, verbose = False):
        super().__init__(piece, "swing", bass_max, bass_min, voicing_min, voicing_max, p_remove_note, max_voicing_jump, verbose)
        self.modified_note_track = self.get_swingified_melody()
        self.voicing_track = self.arrange_voicing_track()
        self.bass_track = self.arrange_walking_bass_track(bass_max, bass_min)
    
    def get_swingified_melody(self):
        first_downbeat_time = self.find_first_downbeat_time()
        self.modified_note_track = deepcopy(self.piece.notes[:])
        
        prolong_dur_flag = False
        for i,note in enumerate(self.modified_note_track):
            beat_time = note.time - first_downbeat_time
            if i < len(self.modified_note_track) - 1:
                next_note_duration = self.modified_note_track[i+1].duration
            else:
                next_note_duration = note.duration
            if note.duration % 24 == 12:
                if beat_time % 24 == 0 and (next_note_duration % 24 == 12 or next_note_duration % 24 == 0):
                    note.duration = note.duration + 4
                    prolong_dur_flag = True
                elif beat_time % 24 == 12 and prolong_dur_flag:
                    note.duration = note.duration - 4
                    note.time = note.time + 4
                    prolong_dur_flag = False
                
            elif note.duration % 24 == 0 and prolong_dur_flag:
                if beat_time % 24 == 12:
                    note.time = note.time + 4
                    prolong_dur_flag = True
            
            self.modified_note_track[i] = note
        
        return self.modified_note_track
    
    def arrange_voicing_track(self):
        # get voicing rhythm
        voicing_rhythm_templates = []
        voicing_rhythm_template_durations = []
        for i_meter,meter_obj in enumerate(self.piece.time_signatures):
            meter_start_time, meter_end_time, numerator, denominator, measure_length, n_measures = self.get_meter_information(i_meter)
            
            # select templates for each measure
            rhythm_tag = "normal"
            for i_measure in range(n_measures):
                if (numerator, denominator) == (4,4):
                    if i_measure < n_measures - 1:
                        rhythm_tag = rhythm_tag_change_44(rhythm_tag)
                        N_templates = N_TEMPLATE_PER_SWING_VOICING_RHYTHM_44[rhythm_tag]
                        i_template = random.randrange(0, N_templates)
                        rhythm_template = SWING_VOICING_RHYTHM_TEMPLATES_44[rhythm_tag][i_template]
#                         rhythm_template = randomly_partite_4th_note_into_swing_8ths(rhythm_template, p = 0.4)
#                         rhythm_template = randomly_acticipatify_rhythm(rhythm_template, p = 0.4)
                    else:
                        N_templates = N_TEMPLATE_PER_SWING_VOICING_RHYTHM_44["coda"]
                        i_template = random.randrange(0, N_templates)
                        rhythm_template = SWING_VOICING_RHYTHM_TEMPLATES_44["coda"][i_template]
                    
                elif (numerator, denominator) == (3,4):
                    if i_measure < n_measures - 1:
                        rhythm_tag = rhythm_tag_change_34(rhythm_tag)
                        N_templates = N_TEMPLATE_PER_SWING_VOICING_RHYTHM_34[rhythm_tag]
                        i_template = random.randrange(0, N_templates)
                        rhythm_template = SWING_VOICING_RHYTHM_TEMPLATES_34[rhythm_tag][i_template]
                    else:
                        N_templates = N_TEMPLATE_PER_SWING_VOICING_RHYTHM_34["coda"]
                        i_template = random.randrange(0, N_templates)
                        rhythm_template = SWING_VOICING_RHYTHM_TEMPLATES_34["coda"][i_template]
                        
                voicing_rhythm_templates.append(rhythm_template[:])
                voicing_rhythm_template_durations.append(measure_length)
                    
        voicing_onset_duration_track, voicing_anticipation_track = get_onset_duration_track_out_of_rhythm_templates(
            voicing_rhythm_templates, 
            voicing_rhythm_template_durations,
            template_start_time = self.find_first_downbeat_time()
        )
        self.N_voicing = len(voicing_onset_duration_track)
        
        # given voicing rhythm, get voicing arrangements
        i_chord = 0
        i_voicing = 0
        self.voicing_track = []
        while i_chord < self.N_chords:
            chord_start, chord_end, next_chord_start = self.get_chord_timing_information(i_chord)

            while i_voicing < self.N_voicing:
                voicing_start, voicing_dur = voicing_onset_duration_track[i_voicing]
                voicing_end = voicing_start + voicing_dur
                if voicing_end > chord_end:
                    break
                this_voicing = {
                    "time": voicing_start,
                    "duration": voicing_dur,
                    "pitches": self.voicings[i_chord]
                }
                self.voicing_track.append(Chord(**this_voicing))
                i_voicing += 1

            i_chord += 1
        
        return insert_rests_structed(self.voicing_track)
    
    def get_bass_pitch(self, i_chord, bass_start, prev_bass_pitch, contour, bass_max = 54, bass_min = 24):
        chord_bass = self.bassline[i_chord]
        chord_root = self.root_list[i_chord]
        chord_quality = self.symb_list[i_chord]
        chord_start, chord_end, next_chord_start = self.get_chord_timing_information(i_chord)
        chord_duration = chord_end - chord_start
        
        meter = self.get_chord_meter(i_chord)
        if (chord_duration > 24*4 and meter == (4,4)) or (chord_duration > 24*3 and meter == (3,4)):
            next_chord_bass = chord_bass
        else:
            if i_chord < self.N_chords - 1:
                next_chord_bass = self.bassline[i_chord + 1]
            else:
                next_chord_bass = self.bassline[i_chord]
        
        if i_chord == self.N_chords - 1:
            bass_pitch = chord_bass
        elif contour == CONTOUR_STAY:
            bass_pitch = prev_bass_pitch
        elif (bass_start - chord_start)%96 == 0 and meter == (4,4):
            bass_pitch = chord_bass
        elif (bass_start - chord_start)%72 == 0 and meter == (3,4):
            bass_pitch = chord_bass
        elif (bass_start - chord_start)%96 == 24 and chord_duration >= 24*3:
            bass_pitch = get_root_or_5th(chord_root, chord_quality, p_root = 0.3)
                
        elif (bass_start - chord_start)%72 == 24 and chord_duration >= 24*3:
            bass_pitch = get_root_or_5th(chord_root, chord_quality, p_root = 0.6)
                
        elif (bass_start - chord_start)%96 == 24 and chord_duration == 24*2:
            bass_pitch = get_leading_or_5th(next_chord_bass, chord_root, chord_quality, p_above=0.6, p_leading = 0.8)
                
        elif (bass_start - chord_start)%96 == 48 and meter == (4,4):
            order = int((int(np.random.random() > 0.5) - 0.5) * 2) # -1 or 1
            if (prev_bass_pitch - chord_root)%12 == INT_5:
                bass_pitch = chord_root + 12*order
            else:
                bass_pitch = get_5th_root_note(chord_root, chord_quality)
                
        elif (bass_start - chord_start)%72 == 48 and meter == (3,4):
             bass_pitch = get_leading_or_5th(next_chord_bass, chord_root, chord_quality, p_above=0.6, p_leading = 0.8)
                
        elif (bass_start - chord_start)%96 == 72 and meter == (4,4):
             bass_pitch = get_leading_or_5th(next_chord_bass, chord_root, chord_quality, p_above=0.6, p_leading = 0.8)
        else:
            bass_pitch = chord_root
        
        if contour == CONTOUR_UP:
            while prev_bass_pitch >= bass_pitch:
                bass_pitch += 12
            while bass_pitch - 12 > prev_bass_pitch:
                bass_pitch -= 12
        if contour == CONTOUR_DOWN:
            while prev_bass_pitch <= bass_pitch:
                bass_pitch -= 12
            while bass_pitch + 12 < prev_bass_pitch:
                bass_pitch += 12
        
        while bass_pitch > bass_max:
            bass_pitch -= 12
        while bass_pitch < bass_min:
            bass_pitch += 12
            
        next_contour = determine_note_contour(prev_bass_pitch, bass_pitch)
        if bass_max - bass_pitch <= 0:
            next_contour = CONTOUR_DOWN
        if bass_pitch - bass_min <= 0:
            next_contour = CONTOUR_UP
        if contour == CONTOUR_STAY:
            next_contour = CONTOUR_UP
        
        return bass_pitch, next_contour
            
    # bassline modes: walking, half-time
    # it has chances to split a 4th note into ghost notes
    def arrange_walking_bass_track(self, bass_max = 54, bass_min = 24):
        
        # get bass rhythm
        bass_rhythm_templates = []
        bass_rhythm_template_durations = []
        for i_meter,meter_obj in enumerate(self.piece.time_signatures):
            meter_start_time, meter_end_time, numerator, denominator, measure_length, n_measures = self.get_meter_information(i_meter)
            
            # select templates for each measure
            for i_measure in range(n_measures):
                if (numerator, denominator) == (4,4):
                    rhythm_template = [(0,24),(24,24),(48,24),(72,24)]
                elif (numerator, denominator) == (3,4):
                    rhythm_template = [(0,24),(24,24),(48,24)]
                else:
                    assert 0, "unsupported meter: " + str(numerator) + "/" + str(denominator)
                # ghost note
#                 for i_note in range(len(rhythm_template)):
#                     if np.random.random() < 0.3 and i_measure < n_measures - 1:
#                         rhythm_template[i_note] = (rhythm_template[i_note][0], 16)
#                         rhythm_template.insert(i_note+1, (rhythm_template[i_note][0]+16, 8))
                
                bass_rhythm_templates.append(rhythm_template[:])
                bass_rhythm_template_durations.append(measure_length)
                    
        bass_onset_duration_track, _ = get_onset_duration_track_out_of_rhythm_templates(
            bass_rhythm_templates, 
            bass_rhythm_template_durations,
            template_start_time = self.find_first_downbeat_time(),
            anticipate = False
        )
        self.N_bass = len(bass_onset_duration_track)
        
        # given bass rhythm, get bass arrangements
        i_chord = 0
        i_bass = 0
        self.bass_track = []
        prev_bass_pitch = self.bassline[i_chord]
        contour = CONTOUR_UP
        while i_chord < self.N_chords:
            chord_start, chord_end, next_chord_start = self.get_chord_timing_information(i_chord)
            if contour == CONTOUR_STAY:
                contour = CONTOUR_UP
            while i_bass < self.N_bass:
                bass_start, bass_dur = bass_onset_duration_track[i_bass]
                bass_end = bass_start + bass_dur
                if bass_end > chord_end:
                    break
                
                bass_pitch, contour = self.get_bass_pitch(i_chord, bass_start, prev_bass_pitch, contour, bass_max, bass_min)
                this_bass = {
                    "time": bass_start,
                    "duration": bass_dur,
                    "pitch": bass_pitch
                }
                prev_bass_pitch = bass_pitch
                self.bass_track.append(Note(**this_bass))
                i_bass += 1

                
            i_chord += 1
        return insert_rests_structed(self.bass_track)
        
    def output_swingified_result(self, out_dir=""):
        midi_path = os.path.join(out_dir, self.name + "_swingified" + ".mid")
        json_path =  os.path.join(out_dir, self.name + "_swingified" + ".json")
        notes_chord_to_midi(
            [self.modified_note_track, self.bass_track], self.voicing_track, self.piece.time_signatures, midi_path, resolution=24
        )
        self.output_json(json_path)


class Bossaifier(Jazzifier):
    def __init__(self, piece, bass_max = 54, bass_min = 24, voicing_min = 38, voicing_max = 64, p_remove_note = 0.1, max_voicing_jump = 6, verbose = False):
        super().__init__(piece, "bossa", bass_max, bass_min, voicing_min, voicing_max, p_remove_note, max_voicing_jump, verbose)
        self.modified_note_track = self.get_bossaified_melody()
        self.voicing_track = self.arrange_voicing_track()
        self.bass_track = self.arrange_bossa_bass_track(bass_max, bass_min)
    
    def get_bossaified_melody(self):
        first_downbeat_time = self.find_first_downbeat_time()
        self.modified_note_track = deepcopy(self.piece.notes[:])
        
        steal_8th_flag = False
        syncopate_duration_counter = 0
        for i,note in enumerate(self.modified_note_track):
            beat_time = note.time - first_downbeat_time
            if steal_8th_flag:
                if syncopate_duration_counter >= 24*7:
                    note.time = note.time - 12
                    note.duration = note.duration + 12
                    steal_8th_flag = False
                    syncopate_duration_counter = 0
                else:
                    note.time = note.time - 12
                    syncopate_duration_counter += note.duration
                
            if not steal_8th_flag and beat_time == 24 and note.duration % 24 == 0:
                note.duration = note.duration - 12
                steal_8th_flag = True
                syncopate_duration_counter += note.duration
                
            self.modified_note_track[i] = note
        
        return self.modified_note_track
    
    def arrange_voicing_track(self):
        # get voicing rhythm
        voicing_rhythm_templates = []
        voicing_rhythm_template_durations = []
        for i_meter,meter_obj in enumerate(self.piece.time_signatures):
            meter_start_time, meter_end_time, numerator, denominator, measure_length, n_measures = self.get_meter_information(i_meter)
            
            # select templates for each measure
            rhythm_tag = "measure1"
            for i_measure in range(n_measures):
                if (numerator, denominator) == (4,4):
                    if i_measure < n_measures - 2:
                        N_templates = N_TEMPLATE_PER_BOSSA_VOICING_RHYTHM[rhythm_tag]
                        i_template = random.randrange(0, N_templates)
                        rhythm_template = BOSSA_VOICING_RHYTHM_TEMPLATES[rhythm_tag][i_template]
                    else:
                        N_templates = N_TEMPLATE_PER_BOSSA_VOICING_RHYTHM["coda"]
                        i_template = random.randrange(0, N_templates)
                        rhythm_template = BOSSA_VOICING_RHYTHM_TEMPLATES["coda"][i_template]
                    rhythm_tag = rhythm_tag_change_bossa_44(rhythm_tag)
                else:
                    assert 0, "unsupported meter: " + str(numerator) + "/" + str(denominator)
                        
                voicing_rhythm_templates.append(rhythm_template[:])
                voicing_rhythm_template_durations.append(measure_length)
                    
        voicing_onset_duration_track = get_onset_duration_track_out_of_rhythm_templates_bossa(
            voicing_rhythm_templates, 
            voicing_rhythm_template_durations,
            template_start_time = self.find_first_downbeat_time()
        )
        self.N_voicing = len(voicing_onset_duration_track)
        
        # given voicing rhythm, get voicing arrangements
        i_chord = 0
        i_voicing = 0
        self.voicing_track = []
        while i_chord < self.N_chords:
            chord_start, chord_end, next_chord_start = self.get_chord_timing_information(i_chord)

            while i_voicing < self.N_voicing:
                voicing_start, voicing_dur = voicing_onset_duration_track[i_voicing]
                voicing_end = voicing_start + voicing_dur
                if voicing_end > chord_end:
                    break
                this_voicing = {
                    "time": voicing_start,
                    "duration": voicing_dur,
                    "pitches": self.voicings[i_chord]
                }
                self.voicing_track.append(Chord(**this_voicing))
                i_voicing += 1

            i_chord += 1
        
        return insert_rests_structed(self.voicing_track)
    
    def determine_note_contour(self, prev_pitch, this_pitch):
        if prev_pitch > this_pitch:
            return CONTOUR_DOWN
        elif prev_pitch < this_pitch:
            return CONTOUR_UP
        else:
            return CONTOUR_STAY
    
    def get_bass_pitch(self, i_chord, bass_start, prev_bass_pitch, contour, bass_max = 54, bass_min = 24):
        chord_bass = self.bassline[i_chord]
        chord_root = self.root_list[i_chord]
        chord_quality = self.symb_list[i_chord]
        chord_start, chord_end, next_chord_start = self.get_chord_timing_information(i_chord)
        chord_duration = chord_end - chord_start
        
        meter = self.get_chord_meter(i_chord)
        if chord_duration > 24*4:
            next_chord_bass = chord_bass
        else:
            if i_chord < self.N_chords - 1:
                next_chord_bass = self.bassline[i_chord + 1]
            else:
                next_chord_bass = self.bassline[i_chord]
        
        if i_chord == self.N_chords - 1:
            bass_pitch = chord_bass
        elif contour == CONTOUR_STAY:
            bass_pitch = prev_bass_pitch
        elif (bass_start - chord_start)%96 == 0:
            bass_pitch = chord_bass
        elif (bass_start - chord_start)%96 == 24 and chord_duration == 24*2:
            bass_pitch = get_leading_or_5th(next_chord_bass, chord_root, chord_quality, p_above=0.6, p_leading = 0.8)
        elif (bass_start - chord_start)%96 == 36:
            bass_pitch = get_root_or_5th(chord_root, chord_quality, p_root = 0.3)
        elif (bass_start - chord_start)%96 == 48:
            if (prev_bass_pitch - chord_root)%12 == INT_5:
                bass_pitch = prev_bass_pitch
            else:
                bass_pitch = get_5th_root_note(chord_root, chord_quality)
        elif (bass_start - chord_start)%96 == 84:
             bass_pitch = get_leading_or_5th(next_chord_bass, chord_root, chord_quality, p_above=0.6, p_leading = 0.8)
        else:
            bass_pitch = chord_root
        
        if contour == CONTOUR_UP:
            while prev_bass_pitch > bass_pitch: # we tolerate staying in Bossa style
                bass_pitch += 12
            while bass_pitch - 12 > prev_bass_pitch:
                bass_pitch -= 12
        if contour == CONTOUR_DOWN:
            while prev_bass_pitch < bass_pitch:
                bass_pitch -= 12
            while bass_pitch + 12 < prev_bass_pitch:
                bass_pitch += 12
        
        while bass_pitch > bass_max:
            bass_pitch -= 12
        while bass_pitch < bass_min:
            bass_pitch += 12
            
        next_contour = determine_note_contour(prev_bass_pitch, bass_pitch)
        if bass_max - bass_pitch <= 0:
            next_contour = CONTOUR_DOWN
        if bass_pitch - bass_min <= 0:
            next_contour = CONTOUR_UP
        if contour == CONTOUR_STAY:
            next_contour = CONTOUR_UP
        
        return bass_pitch, next_contour
            
    def arrange_bossa_bass_track(self, bass_max = 54, bass_min = 24):
        # get bass rhythm
        bass_rhythm_templates = []
        bass_rhythm_template_durations = []
        for i_meter,meter_obj in enumerate(self.piece.time_signatures):
            meter_start_time, meter_end_time, numerator, denominator, measure_length, n_measures = self.get_meter_information(i_meter)
            
            # select templates for each measure
            for i_measure in range(n_measures):
                if (numerator, denominator) == (4,4):
                    rhythm_template = [(0,36),(36,12),(48,36),(84,12)]
                else:
                    assert 0, "unsupported meter: " + str(numerator) + "/" + str(denominator)
                
                bass_rhythm_templates.append(rhythm_template[:])
                bass_rhythm_template_durations.append(measure_length)
                    
        bass_onset_duration_track =  get_onset_duration_track_out_of_rhythm_templates_bossa(
            bass_rhythm_templates, 
            bass_rhythm_template_durations,
            template_start_time = self.find_first_downbeat_time(),
        )
        self.N_bass = len(bass_onset_duration_track)
        
        # given bass rhythm, get bass arrangements
        i_chord = 0
        i_bass = 0
        self.bass_track = []
        prev_bass_pitch = self.bassline[i_chord]
        contour = CONTOUR_UP
        while i_chord < self.N_chords:
            chord_start, chord_end, next_chord_start = self.get_chord_timing_information(i_chord)
            if contour == CONTOUR_STAY:
                contour = CONTOUR_UP
            while i_bass < self.N_bass:
                bass_start, bass_dur = bass_onset_duration_track[i_bass]
                bass_end = bass_start + bass_dur
                if bass_end > chord_end:
                    break
                
                bass_pitch, contour = self.get_bass_pitch(i_chord, bass_start, prev_bass_pitch, contour, bass_max, bass_min)
                this_bass = {
                    "time": bass_start,
                    "duration": bass_dur,
                    "pitch": bass_pitch
                }
                prev_bass_pitch = bass_pitch
                self.bass_track.append(Note(**this_bass))
                i_bass += 1

                
            i_chord += 1
        return insert_rests_structed(self.bass_track)
        
    def output_bossaified_result(self, out_dir=""):
        midi_path = os.path.join(out_dir, self.name + "_bossaified" + ".mid")
        json_path =  os.path.join(out_dir, self.name + "_bossaified" + ".json")
        notes_chord_to_midi(
            [self.modified_note_track, self.bass_track], self.voicing_track, self.piece.time_signatures, midi_path, resolution=24, tempo = 140
        )
        self.output_json(json_path)

    

