from rules.chord_symbols import *
from rules.intervals import *
from rules.pitch_names import PITCH_NAME_2_NUM, PITCH_NUM_2_NAME
import numpy as np

from typing import Tuple, List, Dict, Optional

def get_bass_chroma24(chord_notes: List[int]) -> (int, List[int]):
    if len(chord_notes) == 0:
        return -1, []
    if len(chord_notes) == 1:
        return chord_notes[0], []
    
    chord_notes.sort()
    bass_note = chord_notes[0]
    
    chroma24 = []
    for note in chord_notes[1:]:
        interval = note - bass_note
        if interval <= 0:
            continue
        if interval < 24:
            interval_chroma = interval
        else:
            interval_chroma = interval % 12 + 12
            
        if interval_chroma not in chroma24:
            chroma24.append(interval_chroma)
    
    return bass_note, rectify_chroma24(chroma24)

'''
    Given a list of intervals, rectify it such that:
    - All intervals in reserves stay at where they are
    - All unisons or octaves are removed
    - All 3rds, 5ths, 7ths (and octave equivalents) remain in the first octave
    - All intervals in reduces remain in the first octave
    - All other intervals over 2 octaves remain in the second octave
    - Remove duplicated intervals
    - Sort the final interval list in ascending order
'''
DEFAULT_REDUCE = [INT_m3,INT_M3,INT_5,INT_m7,INT_M7]
def rectify_chroma24(chroma24: List[int], 
    reduces:List[int]=DEFAULT_REDUCE, 
    reserves:List[int]=[],
    removes:List[int]=[]
) -> List[int]:
    if len(chroma24) == 0:
        return chroma24
    new_chroma24 = []
    for i in range(len(chroma24)):
        interval = chroma24[i]
        chroma = interval % 12
        append = False
        if is_unison(interval) or interval in removes:
            continue
        elif interval in reserves:
            new_chroma24.append(interval % 24)
        elif interval <= 12:
            if chroma not in new_chroma24:
                new_chroma24.append(chroma)
        elif is_3rd(interval) or is_5th(interval) or is_7th(interval) or interval in reduces:
            new_chroma24.append(chroma)
        elif interval > 12:
            if chroma not in new_chroma24:
                new_chroma24.append(interval % 24)
    new_chroma24 = list(dict.fromkeys(new_chroma24))
    new_chroma24.sort()
    return new_chroma24 # remove duplicated elements and sort in ascending order

def chroma24_to_12(chroma24:List[int])->(List[int],List[int]):
    chroma12 = []
    is_octave = []
    for interval in chroma24:
        chroma = interval%12
        if chroma not in chroma12:
            chroma12.append(chroma)
            is_octave.append(int(interval>=12))
            
    chroma12 = np.array(chroma12, dtype=int)
    is_octave = np.array(is_octave, dtype=int)
    sort_ids = np.argsort(np.array(chroma12))
    chroma12 = chroma12[sort_ids]
    is_octave = is_octave[sort_ids]
    return chroma12.tolist(), is_octave.tolist()

def chroma24_to_interval(chroma24:List[int])->List[int]:
    length = len(chroma24)
    if length == 0:
        return []
    interval = [chroma24[0]]
    if length == 1:
        return interval
    
    for i in range(1,length):
        interval.append(chroma24[i]-chroma24[i-1])
    return interval

# set difference of chroma24_1 - chroma24_2, order preserved
def chroma24_difference(chroma24_1:List[int], chroma24_2:List[int])->List[int]:
    chroma24_dif = [i for i in chroma24_1 if i not in chroma24_2]
    return chroma24_dif
# check if chroma24_1 contains chroma24_2
def chroma24_contains(chroma24_1:List[int], chroma24_2:List[int])->bool:
    return set(chroma24_2).issubset(chroma24_1)
    
'''
    get inverse inversion given chord
    e.g., given [E,G,C], get [G,C,E]
    i.e., given [  3,8], get [  5,9]
''' 
def invert(bass_note:int, chroma24:List[int]) -> (int,List[int]):
    if len(chroma24) == 0:
        return bass_note, []
    if len(chroma24) == 1:
        return bass_note, chroma24
    
    first_interval = chroma24[0]
    new_chroma24 = [interval - first_interval for interval in chroma24[1:]]
    top_interval = 12 - first_interval
    if top_interval < new_chroma24[-1]:
        top_interval += 12
    new_chroma24.append(top_interval)
    
    bass_diff = first_interval%12
    if bass_diff > 5:
        bass_diff = bass_diff - 12
    new_bass = bass_note + bass_diff
    return new_bass, new_chroma24

'''
    get inverse inversion given chord
    e.g., given [E,G,C], get [C,E,G]
    i.e., given [  3,8], get [  4,7]
    e.g., given [D,E,G,B,C ], get [C,D,E,G,B]
    i.e., given [  2,5,9,10], get [  2,4,7,11]
    e.g., given [C,E,G,B ,D ], get [D,C ,E ,G ,B ]
    i.e., given [  4,7,11,14], get [  10,14,17,21]
''' 
def inv_invert(bass_note:int, chroma24:List[int]) -> (int,List[int]):
    if len(chroma24) == 0:
        return bass_note, []
    if len(chroma24) == 1:
        return bass_note, chroma24
    
    if chroma24[-1] < 12:
        top_interval = 12 - chroma24[-1]
    else:
        top_interval = 24 - chroma24[-1]
    
    new_chroma24 = [interval + top_interval for interval in [0]+chroma24[:-1]]
    
    bass_diff = chroma24[-1]%12
    if bass_diff > 5:
        bass_diff = bass_diff - 12
    new_bass = bass_note + bass_diff
    return new_bass, new_chroma24

def invert_no_chrma24(note_list:List[int], time_inversion:int = 1):
    def invert_inner_loop(note_list:List[int]):
        if len(note_list) <= 1:
            return note_list
        note_list.sort()
        new_note_list = [note for note in note_list[1:]]
        prev_top = note_list[-1]
        new_top = note_list[0]
        while new_top <= prev_top:
            new_top += 12
        new_note_list.append(new_top)
        return new_note_list
    
    new_note_list = note_list[:]
    for _ in range(time_inversion):
        new_note_list = invert_inner_loop(new_note_list)
    return new_note_list

def inv_invert_no_chrma24(note_list:List[int], time_inversion:int = 1):
    def inv_invert_inner_loop(note_list:List[int]):
        if len(note_list) <= 1:
            return note_list
        note_list.sort()
        new_note_list = [note for note in note_list[0:-1]]
        prev_bass = note_list[0]
        new_bass = note_list[-1]
        while new_bass >= prev_bass:
            new_bass -= 12
        new_note_list.insert(0,new_bass)
        return new_note_list
    
    new_note_list = note_list[:]
    for _ in range(time_inversion):
        new_note_list = inv_invert_inner_loop(new_note_list)
    return new_note_list


def remove_inversion(chord_quality:str) -> str:
    done = False
    splitted = chord_quality.split("-")
    if len(splitted) >= 3:
        if splitted[-2] == "on":
            splitted = splitted[:-2]
    return "-".join(splitted)

def remove_bass(bass_note:int, chroma24:List[int]) -> (int,List[int]):
    if len(chroma24) <= 1:
        return bass_note, []
    first_interval = chroma24[0]
    new_chroma24 = [interval - first_interval for interval in chroma24[1:]]
    new_bass_note = bass_note + first_interval
    return new_bass_note, new_chroma24

'''
    remove note extension from a chord symbol, 
    note that: input should not be inversions (otherwise, it will end with string like "-on-C")
    e.g., given "major-#9", get "major"
'''
def remove_extension(chord_quality:str) -> str:
    done = False
    splitted = chord_quality.split("-")
    while not done:
        if "-"+splitted[-1] in POSSIBLE_EXTS:
            splitted = splitted[:-1]
        else:
            done = True
    return "-".join(splitted)

def get_extensions(chord_quality:str) -> str:
    done = False
    splitted = chord_quality.split("-")
    extension_notes = []
    while not done:
        if "-"+splitted[-1] in POSSIBLE_EXTS:
            extension_notes.append("-"+splitted[-1])
            splitted = splitted[:-1]
        else:
            done = True
    return extension_notes

def remove_inversion_extension(chord_quality:str) -> str:
    invesion_removed = remove_inversion(chord_quality)
    return remove_extension(invesion_removed)

'''
    conversion rules
    returns: if chord detected, return (chord-symbol-name, importance)
             if not, return False
    importance measures: 
        3 - most common; 
        2 - less common; 
        1 - quite not common; 
        0 or less - almost never used
'''
IMP_HIGH = 3
IMP_MID = 2
IMP_LOW = 1
IMP_NA = 0

def get_extra_notes_chroma12(template:List[int], chroma12:List[int], chroma12_is_octave:List[int]) -> List[int]:
    extra_notes = []
    for i in range(len(chroma12)):
        note = chroma12[i]
        is_octave = chroma12_is_octave[i]
        if note not in template:
            extra_notes.append(note + is_octave*12)
    return extra_notes

def create_extension_string_from_notes(extra_notes:List[int], exts:List[int] = INT2EXT) -> str:
    ext_string = ""
    for remaining in extra_notes:
        if remaining in exts:
            ext_string = ext_string + exts[remaining]
    return ext_string

def create_extra_note_extension_chroma12(template:List[int], chroma12:List[int], chroma12_is_octave:List[int], 
    exts: Dict[int,str] = INT2EXT
) -> str:
    extra_notes = []
    if chroma24_contains(chroma12, template):
        extra_notes = get_extra_notes_chroma12(template, chroma12, chroma12_is_octave)
    return create_extension_string_from_notes(extra_notes, exts = exts)

def default_chroma12(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None
) -> (List[int],List[int]):
    if chroma12 is None:
        chroma12 = chroma24
    if chroma12_is_octave is None:
        chroma12_is_octave = [0]*len(chroma12)
    return chroma12, chroma12_is_octave

'''
    Rules begin!!
'''

def is_intervals(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
    if len(chroma12) == 0:
        return INT2NAME[0],IMP_HIGH
    if len(chroma12) == 1:
        interval = chroma12[0] % 12
        if interval in INT2NAME:
            return INT2NAME[interval],IMP_HIGH
    return False


MAJOR_TRIAD_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_5]
]
MAJOR_SECOND_TEMPLATES_CHROMA12 = [
    [INT_M2,INT_M3,INT_5]
]
MAJOR_FLAT5_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_a4]
]
MAJOR_SHARP4_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_a4,INT_5]
]
MAJOR_FOURTH_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_4]
]
MAJOR_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_5,INT_M7], [INT_M3,INT_M7], [INT_5,INT_M7]
]
MAJOR_SIXTH_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_5,INT_M6], [INT_M3,INT_M6]
]
MAJOR_67_TEMPLATES = [
    [INT_M3,INT_5,INT_M6,INT_M7], [INT_M3,INT_M6,INT_M7],
    [INT_5,INT_M6,INT_M7], [INT_M6,INT_M7]
]
MAJOR_69_TEMPLATES_CHROMA12 = [
    [INT_M2,INT_M3,INT_5,INT_M6], [INT_M2,INT_M3,INT_M6],
    [INT_M2,INT_5,INT_M6], [INT_M2,INT_M6]
]
    
def is_major_basics(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_m3 not in chroma24:
        chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
        if chroma12 in MAJOR_TRIAD_TEMPLATES_CHROMA12:
            return MAJOR,IMP_HIGH
        elif chroma12 in MAJOR_SECOND_TEMPLATES_CHROMA12:
            return MAJOR_2,IMP_HIGH
        elif chroma12 in MAJOR_SEVENTH_TEMPLATES_CHROMA12:
            return MAJOR_7,IMP_HIGH
        elif chroma12 in MAJOR_SIXTH_TEMPLATES_CHROMA12 and not inverted:
            return MAJOR_6,IMP_HIGH
        elif chroma12 in MAJOR_69_TEMPLATES_CHROMA12 and not inverted:
            return MAJOR_69,IMP_HIGH
    return False

def is_major_less_basics(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_m3 not in chroma24:
        chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
        if chroma12 in MAJOR_FLAT5_TEMPLATES_CHROMA12:
            return MAJOR_b5,IMP_MID
        elif chroma12 in MAJOR_SHARP4_TEMPLATES_CHROMA12:
            return MAJOR_a4,IMP_MID
        elif chroma12 in MAJOR_FOURTH_TEMPLATES_CHROMA12:
            return MAJOR_4,IMP_MID
        elif chroma24 in MAJOR_67_TEMPLATES and not inverted:
            return MAJOR_67,IMP_MID
    return False

MINOR_TRIAD_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_5]
]
MINOR_SECOND_TEMPLATES_CHROMA12 = [
    [INT_M2,INT_m3]
]
MINOR_FOURTH_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_4]
]
MINOR_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_5,INT_m7], [INT_m3,INT_m7]
]
MINOR_SEVENTH_SIXTH_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_5,INT_M6,INT_m7], [INT_m3,INT_M6,INT_m7], [INT_5,INT_M6,INT_m7]
]
MINOR_MAJOR_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_5,INT_M7], [INT_m3,INT_M7]
]
MINOR_SIXTH_MAJOR_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_5,INT_M6,INT_M7], [INT_m3,INT_M6,INT_M7]
]
MINOR_SIXTH_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_5,INT_M6], [INT_m3,INT_M6]
]
MINOR_69_TEMPLATES = [
    [INT_M2,INT_m3,INT_5,INT_M6], [INT_M2,INT_m3,INT_5,INT_M6,INT_M9], 
    [INT_m3,INT_5,INT_M6,INT_M9], [INT_m3,INT_M6,INT_M9], [INT_m3,INT_M6,INT_M9,INT_12],
    [INT_M6,INT_M9]
]
def is_minor_basics(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_M3 not in chroma24:
        chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
        
        if chroma12 in MINOR_TRIAD_TEMPLATES_CHROMA12:
            return MINOR,IMP_HIGH
        elif chroma12 in MINOR_SEVENTH_TEMPLATES_CHROMA12:
            return MINOR_7,IMP_HIGH
        elif chroma12 in MINOR_MAJOR_SEVENTH_TEMPLATES_CHROMA12:
            return MINOR_M7,IMP_HIGH
        elif chroma12 in MINOR_SIXTH_TEMPLATES_CHROMA12 and not inverted:
            return MINOR_6,IMP_HIGH
        elif chroma24 in MINOR_69_TEMPLATES and not inverted:
            return MINOR_69,IMP_HIGH
        if chroma12 in MINOR_SECOND_TEMPLATES_CHROMA12:
            return MINOR_2,IMP_HIGH
    return False


def is_minor_less_basics(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_M3 not in chroma24:
        chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
        
        if chroma12 in MINOR_FOURTH_TEMPLATES_CHROMA12:
            return MINOR_4,IMP_MID
        elif chroma12 in MINOR_SEVENTH_SIXTH_TEMPLATES_CHROMA12:
            return MINOR_67,IMP_MID
        elif chroma12 in MINOR_SIXTH_MAJOR_SEVENTH_TEMPLATES_CHROMA12:
            return MINOR_6_M7,IMP_LOW
    return False

DOM_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_5,INT_m7], [INT_M3,INT_m7]
]
DOM_SEVENTH_AUG5_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_a5,INT_m7],
]
DOM_SEVENTH_FLAT5_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_a4,INT_m7]
]
DOM_SEVENTH_FLAT_NINTH_TEMPLATES = [
    [INT_M3,INT_5,INT_m7,INT_m9], [INT_M3,INT_m7,INT_m9], 
    [INT_m7,INT_m9], [INT_M3,INT_m9], 
]
def is_dominant_basics(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_m3 not in chroma24:
        chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
        if chroma12 in DOM_SEVENTH_TEMPLATES_CHROMA12:
            return DOM_7,IMP_HIGH
    return False

def is_dominant_less_basics(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_m3 not in chroma24:
        chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
        if chroma12 in DOM_SEVENTH_AUG5_TEMPLATES_CHROMA12:
            return DOM_7_a5,IMP_MID
        elif chroma12 in DOM_SEVENTH_FLAT5_TEMPLATES_CHROMA12:
            return DOM_7_b5,IMP_MID
        elif chroma24 in DOM_SEVENTH_FLAT_NINTH_TEMPLATES:
            return DOM_7b9,IMP_MID
    return False

SUS_TEMPLATES_CHROMA12 = [
    [INT_4,INT_5],
    [INT_M2,INT_4],
    [INT_M2,INT_4,INT_5],
]
SUS2_TEMPLATES_CHROMA12 = [
    [INT_M2,INT_5]
]
SUS_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_M2,INT_4,INT_5,INT_m7],
    [INT_M2,INT_4,INT_m7],
    [INT_4,INT_5,INT_m7],
    [INT_4,INT_m7],
    [INT_5,INT_m7],
]
SUS_MAJOR_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_M2,INT_4,INT_5,INT_M7],
    [INT_M2,INT_4,INT_M7],
    [INT_4,INT_5,INT_M7],
    [INT_4,INT_M7],
    [INT_5,INT_M7],
]
def is_sus_basics(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
    if INT_m3 not in chroma24 and INT_M3 not in chroma24:
        if chroma12 in SUS_TEMPLATES_CHROMA12:
            return SUS,IMP_MID
        elif chroma12 in SUS2_TEMPLATES_CHROMA12:
            return SUS_2,IMP_MID
        elif chroma12 in SUS_SEVENTH_TEMPLATES_CHROMA12:
            return SUS_7,IMP_MID
        elif chroma12 in SUS_MAJOR_SEVENTH_TEMPLATES_CHROMA12:
            return SUS_M7,IMP_MID
    return False


AUG_TRIAD_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_a5]
]
AUG_MAJOR_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_a5,INT_M7], [INT_a5,INT_M7]
]
AUG_MINOR_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_M3,INT_a5,INT_m7]
]
def is_aug_basics(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_m3 not in chroma24:
        chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
        if chroma12 in AUG_TRIAD_TEMPLATES_CHROMA12:
            return AUG,IMP_HIGH
        elif chroma12 in AUG_MAJOR_SEVENTH_TEMPLATES_CHROMA12:
            return AUG_M7,IMP_HIGH
#         elif chroma12 in AUG_MINOR_SEVENTH_TEMPLATES_CHROMA12:
#             return AUG_m7
    return False

DIM_TRIAD_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_a4]
]
DIM_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_a4,INT_M6]
]
HALFDIM_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_a4,INT_m7]
]
DIM_MAJOR_SEVENTH_TEMPLATES_CHROMA12 = [
    [INT_m3,INT_a4,INT_M7]
]
def is_dim_basics(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_M3 not in chroma24:
        chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
        if chroma12 in DIM_TRIAD_TEMPLATES_CHROMA12:
            return DIM,IMP_HIGH
        elif chroma12 in DIM_SEVENTH_TEMPLATES_CHROMA12:
            return DIM_7,IMP_HIGH
        elif chroma12 in HALFDIM_SEVENTH_TEMPLATES_CHROMA12:
            return HALFDIM_7,IMP_HIGH
    return False
def is_dim_less_basics(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_M3 not in chroma24:
        chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
        if chroma12 in DIM_MAJOR_SEVENTH_TEMPLATES_CHROMA12:
            return DIM_M7,IMP_MID
    return False

''' e.g.,
    chroma24 = [4,7,11,14,17,18,23] ([C,E,G,B,D,F,F#,A])
    template_core = [4,7,11] ([C,E,G,B])
    ext_all = [14,17,23] ([D,F,A])
    ext_no_sharp11 = [14,18,23] ([D,F#,A])
    
    return:
    remaining_intervals = chroma24 - template_core = [14,17,18,23]
    ext_removed = remaining_intervals - ext_no_sharp11 = [18]
    ext_components = remaining_intervals - ext_removed = [14,17,23]
'''
def parse_extra_notes_sharp11(chroma24:List[int], 
    template_core:List[int], 
    ext_all:List[int], ext_no_sharp11:List[int], 
    max_extra_ext:int = 1, collisions:List[int] = [INT_11,INT_a11]
) -> (List[int], List[int], List[int]):
    
    remaining_intervals = chroma24_difference(chroma24, template_core)
    if not (collisions[0] in remaining_intervals and collisions[1] in remaining_intervals):
        ext_removed = chroma24_difference(remaining_intervals, ext_all)
    else:
        ext_removed = chroma24_difference(remaining_intervals, ext_no_sharp11)
    if len(ext_removed) <= max_extra_ext:
        ext_components = chroma24_difference(remaining_intervals, ext_removed)
    else:
        ext_removed = []
        ext_components = remaining_intervals[:]
    return remaining_intervals, ext_removed, ext_components

def parse_extra_notes(chroma24:List[int], template_core:List[int], ext_all:List[int], 
    max_extra_ext:int = 1
) -> (List[int], List[int], List[int]):
    
    remaining_intervals = chroma24_difference(chroma24, template_core)
    ext_removed = chroma24_difference(remaining_intervals, ext_all)
    if len(ext_removed) <= max_extra_ext:
        ext_components = chroma24_difference(remaining_intervals, ext_removed)
    else:
        ext_removed = []
        ext_components = remaining_intervals[:]
    return remaining_intervals, ext_removed, ext_components


'''
    altered notes:
    - must have  3 or 7
    - must have  [b5,#5,b9], [b5,b9], [b5,#9], [#5,b9], [#5,#9]
    - , b5 = b12, 5 = #12, #2 = #9
''' 
ALT_CORE_TEMPLATES = [
    [INT_M3,INT_m7], [INT_M3], [INT_m7]
]
ALT_EXT_TEMPLATES = [
    [INT_a2,INT_a4,INT_a5,INT_m9], 
    [INT_a2,INT_a4,INT_a5], [INT_a2,INT_a4,INT_m9], 
    [INT_a2,INT_a5,INT_m9], [INT_a4,INT_a5,INT_m9], 
    [INT_a2,INT_a4], [INT_a2,INT_a5], [INT_a2,INT_a9],
    [INT_a4,INT_a5], [INT_a4,INT_m9], [INT_a5,INT_m9], 
    [INT_a2]
]
ALT_EXT_ALL = [INT_a2,INT_a4,INT_a5,INT_m9]
ALT_REDUCES = [INT_a9,INT_a11,INT_a12]
ALT_REMOVES = [INT_5]
def is_alt(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    chroma24_alt = rectify_chroma24(chroma24, reduces=ALT_REDUCES, removes=ALT_REMOVES)
    is_dim_bool = bool(is_dim_basics(chroma24, chroma12, chroma12_is_octave, inverted))
    is_min_bool = bool(is_minor_basics(chroma24, chroma12, chroma12_is_octave, inverted))
    if not inverted and not is_dim_bool and not is_min_bool:
        for template_core in ALT_CORE_TEMPLATES:
            if chroma24_contains(chroma24_alt, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes(
                    chroma24_alt, template_core, ALT_EXT_ALL, max_extra_ext = 2
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_ALT)
                importance = IMP_MID - len(ext_removed)
                if remaining_intervals in ALT_EXT_TEMPLATES:
                    return ALT + extra_ext_string, importance
    return False


def is_triad_extensions(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if len(chroma12) == 3:
        chroma12, chroma12_is_octave = default_chroma12(chroma24, chroma12, chroma12_is_octave)
        for template in MAJOR_TRIAD_TEMPLATES_CHROMA12:
            ext_string = create_extra_note_extension_chroma12(template, chroma12, chroma12_is_octave, exts = INT2EXT_MAJ)
            sensible = not(len(ext_string)>0 and inverted)
            if len(ext_string) > 0 and sensible:
                return MAJOR + ext_string, IMP_MID
        
        for template in MINOR_TRIAD_TEMPLATES_CHROMA12:
            ext_string = create_extra_note_extension_chroma12(template, chroma12, chroma12_is_octave, exts = INT2EXT_MIN)
            sensible = not(len(ext_string)>0 and inverted)
            if len(ext_string) > 0 and sensible:
                return MINOR + ext_string, IMP_MID
        
        for template in AUG_TRIAD_TEMPLATES_CHROMA12:
            ext_string = create_extra_note_extension_chroma12(template, chroma12, chroma12_is_octave, exts = INT2EXT_AUG)
            sensible = not(len(ext_string)>0 and inverted)
            if len(ext_string) > 0 and sensible:
                return AUG + ext_string, IMP_MID
            
        for template in SUS2_TEMPLATES_CHROMA12:
            ext_string = create_extra_note_extension_chroma12(template, chroma12, chroma12_is_octave, exts = INT2EXT_SUS)
            sensible = not(len(ext_string)>0 and inverted)
            if len(ext_string) > 0 and sensible:
                return SUS_2 + ext_string, IMP_MID
            
        for template in MAJOR_FLAT5_TEMPLATES_CHROMA12:
            ext_string = create_extra_note_extension_chroma12(template, chroma12, chroma12_is_octave, exts = INT2EXT_MAJ_a4)
            sensible = not(len(ext_string)>0 and inverted)
            if len(ext_string) > 0 and sensible:
                return MAJOR_a4 + ext_string, IMP_MID
    
        for template in MINOR_FOURTH_TEMPLATES_CHROMA12:
            ext_string = create_extra_note_extension_chroma12(template, chroma12, chroma12_is_octave, exts = INT2EXT_MIN_4)
            sensible = not(len(ext_string)>0 and inverted)
            if len(ext_string) > 0 and sensible:
                return MINOR_4 + ext_string, IMP_MID
    
    if len(chroma12) == 4:
        for template in MAJOR_SHARP4_TEMPLATES_CHROMA12:
            ext_string = create_extra_note_extension_chroma12(template, chroma12, chroma12_is_octave, exts = INT2EXT_MAJ_a4)
            sensible = not(len(ext_string)>0 and inverted)
            if len(ext_string) > 0 and sensible:
                return MAJOR_a4 + ext_string, IMP_MID
    
    if len(chroma12) >= 3:
        for template in DIM_TRIAD_TEMPLATES_CHROMA12:
            ext_string = create_extra_note_extension_chroma12(template, chroma12, chroma12_is_octave, exts = INT2EXT_MAJ_a4)
            sensible = not(len(ext_string)>0 and inverted)
            if len(ext_string) > 0 and sensible and INT_m7 not in chroma12 and INT_M7 not in chroma12:
                return DIM + ext_string, IMP_MID
            
    return False

MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES = MAJOR_SEVENTH_TEMPLATES_CHROMA12 + [[INT_M7]]
MAJOR_SIXTH_EXTENSION_CORE_TEMPLATES = MAJOR_SIXTH_TEMPLATES_CHROMA12 + [[INT_M6]]
MAJOR_9_EXT_TEMPLATES = [
    [INT_M2]
]
MAJOR_11_EXT_TEMPLATES = [
    [INT_11], [INT_M2,INT_11]
]
MAJOR_a11_EXT_TEMPLATES = [
    [INT_a11], [INT_M2,INT_a11]
]
MAJOR_13_EXT_TEMPLATES = [
    [INT_M2,INT_M6,INT_11], [INT_M6], [INT_M2,INT_M6], [INT_M6,INT_11]
]
MAJOR_13_a11_EXT_TEMPLATES = [
    [INT_M2,INT_M6,INT_a11], [INT_M6,INT_a11]
]
MAJOR_EXT_ALL = [INT_M2,INT_M6,INT_11,INT_a11]
MAJOR_EXT_ALL_NO_a11 = [INT_M2,INT_M6,INT_11]
MAJOR_REDUCES = [INT_M9,INT_M13]
MAJOR_REMOVES = []
def is_major_seventh_sixth_extensions(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_m7 not in chroma24 and (
        INT_m3 not in chroma24 or (INT_M3 in chroma24 and INT_m3 in chroma24)) and (
        INT_a5 not in chroma24 or (INT_a5 in chroma24 and INT_5 in chroma24)):
        chroma24_maj = rectify_chroma24(chroma24, reduces=MAJOR_REDUCES, removes=MAJOR_REMOVES)
        for template_core in MAJOR_SIXTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_maj, template_core) and INT_M13 not in chroma24:
                remaining_intervals, ext_removed, ext_components = parse_extra_notes_sharp11(
                    chroma24_maj, template_core, MAJOR_EXT_ALL, MAJOR_EXT_ALL_NO_a11, max_extra_ext = 1
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_MAJ)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in MAJOR_9_EXT_TEMPLATES:
                        return MAJOR_69 + extra_ext_string, importance
                    elif ext_components in MAJOR_11_EXT_TEMPLATES and INT_M3 in chroma24: # without M3, it is sounds like F6/C (suppose bass is C) 
                        return MAJOR_6_11 + extra_ext_string, importance - 1
                    elif ext_components in MAJOR_a11_EXT_TEMPLATES and INT_M3 in chroma24: # without M3, it is sounds like D7/C (suppose bass is C) 
                        return MAJOR_6_a11 + extra_ext_string, importance - 1
                    elif len(ext_components) == 0 and len(ext_removed) <= 2:
                        return MAJOR_6 + extra_ext_string, importance
                    
        for template_core in MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_maj, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes_sharp11(
                    chroma24_maj, template_core, MAJOR_EXT_ALL, MAJOR_EXT_ALL_NO_a11, max_extra_ext = 2
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_MAJ)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in MAJOR_9_EXT_TEMPLATES:
                        return MAJOR_9 + extra_ext_string, importance
                    elif ext_components in MAJOR_11_EXT_TEMPLATES and INT_M3 in chroma24: # without M3, it is sus-maj
                        return MAJOR_11 + extra_ext_string, importance
                    elif ext_components in MAJOR_a11_EXT_TEMPLATES:
                        return MAJOR_a11 + extra_ext_string, importance
                    elif ext_components in MAJOR_13_EXT_TEMPLATES:
                        return MAJOR_13 + extra_ext_string, importance
                    elif ext_components in MAJOR_13_a11_EXT_TEMPLATES:
                        return MAJOR_13_a11+ extra_ext_string, importance
                    elif len(ext_components) == 0 and len(ext_removed) <= 2:
                        return MAJOR_7 + extra_ext_string, importance
    return False



MINOR_SEVENTH_EXTENSION_CORE_TEMPLATES = MINOR_SEVENTH_TEMPLATES_CHROMA12
MINOR_SIXTH_EXTENSION_CORE_TEMPLATES = MINOR_SIXTH_TEMPLATES_CHROMA12 + MINOR_SEVENTH_SIXTH_TEMPLATES_CHROMA12
MINOR_MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES = MINOR_MAJOR_SEVENTH_TEMPLATES_CHROMA12
MINOR_SIXTH_MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES = MINOR_SIXTH_MAJOR_SEVENTH_TEMPLATES_CHROMA12
MINOR_9_EXT_TEMPLATES = [
    [INT_M2]
]
MINOR_11_EXT_TEMPLATES = [
    [INT_4], [INT_M2,INT_4]
]
MINOR_a11_EXT_TEMPLATES = [
    [INT_a11], [INT_M2,INT_a11]
]
MINOR_13_EXT_TEMPLATES = [
    [INT_M2,INT_4,INT_M13], [INT_M13], [INT_M2,INT_M13], [INT_4,INT_M13]
]
MINOR_13_a11_EXT_TEMPLATES = [
    [INT_M2,INT_a11,INT_M13], [INT_a11,INT_M13]
]
MINOR_EXT_ALL = [INT_M2,INT_4,INT_a11,INT_M13]
MINOR_EXT_ALL_NO_a11 = [INT_M2,INT_4,INT_M13]
MINOR_REDUCES = [INT_M9,INT_11]
MINOR_REMOVES = []
def is_minor_seventh_sixth_extensions(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    is_dim_bool = bool(is_dim_basics(chroma24, chroma12, chroma12_is_octave, inverted))
    if not is_dim_bool and (INT_M3 not in chroma24 or (INT_M3 in chroma24 and INT_m3 in chroma24)):
        chroma24_min = rectify_chroma24(chroma24, reduces=MINOR_REDUCES, removes=MINOR_REMOVES)
        
        for template_core in MINOR_SIXTH_MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_min, template_core) and INT_M13 not in chroma24:
                remaining_intervals, ext_removed, ext_components = parse_extra_notes_sharp11(
                    chroma24_min, template_core, MINOR_EXT_ALL, MINOR_EXT_ALL_NO_a11, max_extra_ext = 2
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_MIN)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in MINOR_9_EXT_TEMPLATES:
                        return MINOR_69_M7 + extra_ext_string, importance
                    elif ext_components in MINOR_11_EXT_TEMPLATES:
                        return MINOR_6_M11 + extra_ext_string, importance
                    elif ext_components in MINOR_a11_EXT_TEMPLATES:
                        return MINOR_6_M7_a11 + extra_ext_string, importance
                    elif len(ext_components) == 0 and len(ext_removed) <= 2:
                        return MINOR_6_M7 + extra_ext_string, importance

        for template_core in MINOR_SIXTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_min, template_core) and INT_M13 not in chroma24:
                remaining_intervals, ext_removed, ext_components = parse_extra_notes_sharp11(
                    chroma24_min, template_core, MINOR_EXT_ALL, MINOR_EXT_ALL_NO_a11, max_extra_ext = 2
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_MIN)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in MINOR_9_EXT_TEMPLATES:
                        return MINOR_69 + extra_ext_string, importance
                    elif ext_components in MINOR_11_EXT_TEMPLATES:
                        return MINOR_6_11 + extra_ext_string, importance
                    elif ext_components in MINOR_a11_EXT_TEMPLATES and INT_5 in chroma24: #if INT_5 not in, then it is dim-9
                        return MINOR_6_a11 + extra_ext_string, importance
                    elif len(ext_components) == 0 and len(ext_removed) <= 2:
                        return MINOR_6 + extra_ext_string, importance

        for template_core in MINOR_SEVENTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_min, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes_sharp11(
                    chroma24_min, template_core, MINOR_EXT_ALL, MINOR_EXT_ALL_NO_a11, max_extra_ext = 2
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_MIN)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in MINOR_9_EXT_TEMPLATES:
                        return MINOR_9 + extra_ext_string, importance
                    elif ext_components in MINOR_11_EXT_TEMPLATES:
                        return MINOR_11 + extra_ext_string, importance
                    elif ext_components in MINOR_a11_EXT_TEMPLATES:
                        return MINOR_a11 + extra_ext_string, importance
                    elif ext_components in MINOR_13_EXT_TEMPLATES:
                        return MINOR_13 + extra_ext_string, importance
                    elif ext_components in MINOR_13_a11_EXT_TEMPLATES and INT_5 in chroma24: #if INT_5 not in, then it is half-dim-9
                        return MINOR_13_a11 + extra_ext_string, importance
                    elif len(ext_components) == 0 and len(ext_removed) <= 2:
                        return MINOR_7 + extra_ext_string, importance

        for template_core in MINOR_MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_min, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes_sharp11(
                    chroma24_min, template_core, MINOR_EXT_ALL, MINOR_EXT_ALL_NO_a11, max_extra_ext = 2
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_MIN)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in MINOR_9_EXT_TEMPLATES:
                        return MINOR_9_M7 + extra_ext_string, importance
                    elif ext_components in MINOR_11_EXT_TEMPLATES:
                        return MINOR_11_M7 + extra_ext_string, importance
                    elif ext_components in MINOR_a11_EXT_TEMPLATES:
                        return MINOR_a11_M7 + extra_ext_string, importance, importance
                    elif ext_components in MINOR_13_EXT_TEMPLATES:
                        return MINOR_13_M7 + extra_ext_string, importance
                    elif ext_components in MINOR_13_a11_EXT_TEMPLATES:
                        return MINOR_13_M7_a11 + extra_ext_string, importance
                    elif len(ext_components) == 0 and len(ext_removed) <= 2:
                        return MINOR_M7 + extra_ext_string, importance
    
    return False


DOM_SEVENTH_EXTENSION_CORE_TEMPLATES = DOM_SEVENTH_TEMPLATES_CHROMA12 
DOM_9_EXT_TEMPLATES = [
    [INT_M2]
]
DOM_b9_EXT_TEMPLATES = [
    [INT_m9]
]
DOM_11_EXT_TEMPLATES = [
    [INT_11], [INT_M2,INT_11]
]
DOM_a11_EXT_TEMPLATES = [
    [INT_a11], [INT_M2,INT_a11]
]
DOM_11_b9_EXT_TEMPLATES = [
    [INT_m9,INT_11]
]
DOM_13_EXT_TEMPLATES = [
    [INT_M2,INT_M6,INT_11], [INT_M6], [INT_M2,INT_M6], [INT_M6,INT_11]
]
DOM_13_a11_EXT_TEMPLATES = [
    [INT_M2,INT_M6,INT_a11], [INT_M6,INT_a11]
]
DOM_13_b9_EXT_TEMPLATES = [
    [INT_M6,INT_m9,INT_11], [INT_M6,INT_m9]
]
DOM_EXT_ALL = [INT_M2,INT_M6,INT_m9,INT_11,INT_a11]
DOM_EXT_ALL_no_b9 = [INT_M2,INT_M6,INT_11,INT_a11]
DOM_EXT_ALL_no_a11 = [INT_M2,INT_M6,INT_m9,INT_11]
DOM_EXT_ALL_normal = [INT_M2,INT_M6,INT_11]

DOM_REDUCES = [INT_M9,INT_M13]
DOM_REMOVES = []

def parse_extra_notes_dom(chroma24:List[int], template_core:List[int], 
    max_extra_ext:int = 1
) -> (List[int], List[int], List[int]):
    remaining_intervals = chroma24_difference(chroma24, template_core)
    if not (INT_11 in remaining_intervals and INT_a11 in remaining_intervals):
        if not (INT_M2 in remaining_intervals and INT_m9 in remaining_intervals):
            ext_removed = chroma24_difference(remaining_intervals, DOM_EXT_ALL)
        else:
            ext_removed = chroma24_difference(remaining_intervals, DOM_EXT_ALL_no_b9)
    else:
        if not (INT_M2 in remaining_intervals and INT_m9 in remaining_intervals):
            ext_removed = chroma24_difference(remaining_intervals, DOM_EXT_ALL_no_a11)
        else:
            ext_removed = chroma24_difference(remaining_intervals, DOM_EXT_ALL_normal)
    if len(ext_removed) <= max_extra_ext:
        ext_components = chroma24_difference(remaining_intervals, ext_removed)
    else:
        ext_removed = []
        ext_components = remaining_intervals[:]
    return remaining_intervals, ext_removed, ext_components

def is_dom_seventh_extensions(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_m3 not in chroma24 or (INT_M3 in chroma24 and INT_m3 in chroma24):
        chroma24_dom = rectify_chroma24(chroma24, reduces=DOM_REDUCES, removes=DOM_REMOVES)
        for template_core in DOM_SEVENTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_dom, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes_dom(
                    chroma24_dom, template_core, max_extra_ext = 2
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_DOM)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in DOM_9_EXT_TEMPLATES:
                        return DOM_9 + extra_ext_string, importance
                    elif ext_components in DOM_11_EXT_TEMPLATES:
                        return DOM_11 + extra_ext_string, importance
                    elif ext_components in DOM_13_EXT_TEMPLATES:
                        return DOM_13 + extra_ext_string, importance
                    elif ext_components in DOM_b9_EXT_TEMPLATES:
                        return DOM_7b9 + extra_ext_string, importance
                    elif ext_components in DOM_11_b9_EXT_TEMPLATES:
                        return DOM_11b9 + extra_ext_string, importance
                    elif ext_components in DOM_13_b9_EXT_TEMPLATES:
                        return DOM_13b9 + extra_ext_string, importance
                    elif ext_components in DOM_a11_EXT_TEMPLATES:
                        return DOM_7_a11 + extra_ext_string, importance
                    elif ext_components in DOM_13_a11_EXT_TEMPLATES:
                        return DOM_13_a11 + extra_ext_string, importance
            
        for template_core in DOM_SEVENTH_AUG5_TEMPLATES_CHROMA12:
            if chroma24_contains(chroma24_dom, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes_dom(
                    chroma24_dom, template_core, max_extra_ext = 1
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_DOM_a5)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in DOM_9_EXT_TEMPLATES:
                        return DOM_a5_9 + extra_ext_string, importance
                    elif ext_components in DOM_11_EXT_TEMPLATES:
                        return DOM_a5_11 + extra_ext_string, importance
                    elif ext_components in DOM_13_EXT_TEMPLATES:
                        return DOM_a5_13 + extra_ext_string, importance
                    elif ext_components in DOM_b9_EXT_TEMPLATES:
                        return DOM_a5_7b9 + extra_ext_string, importance
                    elif ext_components in DOM_11_b9_EXT_TEMPLATES:
                        return DOM_a5_11b9 + extra_ext_string, importance
                    elif ext_components in DOM_13_b9_EXT_TEMPLATES:
                        return DOM_a5_13b9 + extra_ext_string, importance
                    elif ext_components in DOM_a11_EXT_TEMPLATES:
                        return DOM_a5_7_a11 + extra_ext_string, importance
                    elif ext_components in DOM_13_a11_EXT_TEMPLATES:
                        return DOM_a5_13_a11 + extra_ext_string, importance
        
        for template_core in DOM_SEVENTH_FLAT5_TEMPLATES_CHROMA12:
            if chroma24_contains(chroma24_dom, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes_dom(
                    chroma24_dom, template_core, max_extra_ext = 1
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_DOM_b5)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in DOM_9_EXT_TEMPLATES:
                        return DOM_b5_9 + extra_ext_string, importance
                    elif ext_components in DOM_11_EXT_TEMPLATES:
                        return DOM_b5_11 + extra_ext_string, importance
                    elif ext_components in DOM_13_EXT_TEMPLATES:
                        return DOM_b5_13 + extra_ext_string, importance
                    elif ext_components in DOM_b9_EXT_TEMPLATES:
                        return DOM_b5_7b9 + extra_ext_string, importance
                    elif ext_components in DOM_11_b9_EXT_TEMPLATES:
                        return DOM_b5_11b9 + extra_ext_string, importance
                    elif ext_components in DOM_13_b9_EXT_TEMPLATES:
                        return DOM_b5_13b9 + extra_ext_string, importance
            
    return False


SUS_SEVENTH_EXTENSION_CORE_TEMPLATES = SUS_SEVENTH_TEMPLATES_CHROMA12
SUS_MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES = SUS_MAJOR_SEVENTH_TEMPLATES_CHROMA12
SUS_13_EXT_TEMPLATES = [
    [INT_M6]
]
SUS_EXT_ALL = [INT_M6]
SUS_REDUCES = [INT_M9,INT_11,INT_M13]
SUS_REMOVES = []
def is_sus_seventh_extensions(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    # if INT_m3 not in chroma24 or (INT_M3 in chroma24 and INT_m3 in chroma24):
    if INT_m3 not in chroma24 and INT_M3 not in chroma24:
        chroma24_sus = rectify_chroma24(chroma24, reduces=SUS_REDUCES, removes=SUS_REMOVES)
        for template_core in SUS_SEVENTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_sus, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes(
                    chroma24_sus, template_core, SUS_EXT_ALL, max_extra_ext = 1
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_SUS)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in SUS_13_EXT_TEMPLATES:
                        return SUS_13 + extra_ext_string, importance
                    elif len(ext_components) == 0 and len(ext_removed) <= 1:
                        return SUS_7 + extra_ext_string, importance
        
        for template_core in SUS_MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_sus, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes(
                    chroma24_sus, template_core, SUS_EXT_ALL, max_extra_ext = 1
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_SUS)
                importance = IMP_MID- len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in SUS_13_EXT_TEMPLATES:
                        return SUS_M13 + extra_ext_string, importance
                    elif len(ext_components) == 0 and len(ext_removed) <= 1:
                        return SUS_M7 + extra_ext_string, importance
    return False


AUG_MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES = AUG_MAJOR_SEVENTH_TEMPLATES_CHROMA12
AUG_9_EXT_TEMPLATES = [
    [INT_M2]
]
AUG_11_EXT_TEMPLATES = [
    [INT_4], [INT_M2,INT_4]
]
AUG_a11_EXT_TEMPLATES = [
    [INT_a4], [INT_M2,INT_a4]
]
AUG_13_EXT_TEMPLATES = [
    [INT_M2,INT_4,INT_M6], [INT_M6], [INT_M2,INT_M6], [INT_4,INT_M6]
]
AUG_13_a11_EXT_TEMPLATES = [
    [INT_M2,INT_a4,INT_M6], [INT_a4,INT_M6]
]
AUG_EXT_ALL = [INT_M2,INT_4,INT_a4,INT_M6]
AUG_EXT_ALL_NO_a11 = [INT_M2,INT_4,INT_M6]
AUG_REDUCES = [INT_M9,INT_11,INT_a11,INT_M13]
AUG_REMOVES = []
def is_aug_major_seventh_extensions(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    chroma24_aug = rectify_chroma24(chroma24, reduces=AUG_REDUCES, removes=AUG_REMOVES)
    for template_core in AUG_MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES:
        if chroma24_contains(chroma24_aug, template_core):
            remaining_intervals, ext_removed, ext_components = parse_extra_notes_sharp11(
                chroma24_aug, template_core, 
                AUG_EXT_ALL, AUG_EXT_ALL_NO_a11, 
                max_extra_ext = 2, collisions = [INT_4,INT_a4]
            )
            extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_AUG_M7)
            importance = IMP_MID - len(ext_removed)
            sensible = not(len(extra_ext_string)>0 and inverted)
            if sensible:
                if ext_components in AUG_9_EXT_TEMPLATES:
                    return AUG_M7_M9 + extra_ext_string, importance
                elif ext_components in AUG_11_EXT_TEMPLATES:
                    return AUG_M7_M11 + extra_ext_string, importance
                elif ext_components in AUG_a11_EXT_TEMPLATES:
                    return AUG_M7_a11 + extra_ext_string, importance
                elif ext_components in AUG_13_EXT_TEMPLATES:
                    return AUG_M7_M13 + extra_ext_string, importance
                elif ext_components in AUG_13_a11_EXT_TEMPLATES:
                    return AUG_M7_M13_a11+ extra_ext_string, importance
                elif len(ext_components) == 0 and len(ext_removed) <= 2:
                    return AUG_M7 + extra_ext_string, importance
            
    return False

DIM_SEVENTH_EXTENSION_CORE_TEMPLATES = DIM_SEVENTH_TEMPLATES_CHROMA12
DIM_MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES = DIM_MAJOR_SEVENTH_TEMPLATES_CHROMA12 + [[INT_a4,INT_M7]]
DIM_9_EXT_TEMPLATES = [
    [INT_M2]
]
DIM_EXT_ALL = [INT_M2]
DIM_REDUCES = [INT_M9,INT_a11,INT_M13]
DIM_REMOVES = []
def is_dim_seventh_extensions(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_M3 not in chroma24 or (INT_M3 in chroma24 and INT_m3 in chroma24):
        chroma24_dim = rectify_chroma24(chroma24, reduces=DIM_REDUCES, removes=DIM_REMOVES)
        for template_core in DIM_SEVENTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_dim, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes(
                    chroma24_dim, template_core, DIM_EXT_ALL, max_extra_ext = 2
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_DIM)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in DIM_9_EXT_TEMPLATES:
                        return DIM_9 + extra_ext_string, importance
                    elif len(ext_components) == 0 and len(ext_removed) <= 2 and INT_M7 not in ext_removed:
                        return DIM_7 + extra_ext_string, importance

        for template_core in DIM_MAJOR_SEVENTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_dim, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes(
                    chroma24_dim, template_core, DIM_EXT_ALL, max_extra_ext = 2
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_DIM_M7)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in DIM_9_EXT_TEMPLATES:
                        return DIM_M9 + extra_ext_string, importance
                    elif len(ext_components) == 0 and len(ext_removed) <= 2:
                        return DIM_M7 + extra_ext_string, importance
                
    return False

HALFDIM_SEVENTH_EXTENSION_CORE_TEMPLATES = HALFDIM_SEVENTH_TEMPLATES_CHROMA12 + [[INT_a4,INT_m7]]
HALFDIM_9_EXT_TEMPLATES = [
    [INT_M2]
]
HALFDIM_11_EXT_TEMPLATES = [
    [INT_4], [INT_M2,INT_4]
]
HALFDIM_b13_EXT_TEMPLATES = [
    [INT_M2,INT_4,INT_m6], [INT_m6], [INT_M2,INT_m6], [INT_4,INT_m6]
]
HALFDIM_EXT_ALL = [INT_M2,INT_4,INT_m6]
HALFDIM_REDUCES = [INT_M9,INT_11,INT_a11,INT_m13]
HALFDIM_REMOVES = []
def is_halfdim_seventh_extensions(chroma24:List[int], 
    chroma12:List[int] = None, chroma12_is_octave:List[int] = None, inverted:bool = False
) -> Optional[Tuple[str,int]]:
    if INT_M3 not in chroma24 or (INT_M3 in chroma24 and INT_m3 in chroma24):
        chroma24_hdim = rectify_chroma24(chroma24, reduces=HALFDIM_REDUCES, removes=HALFDIM_REMOVES)
        for template_core in HALFDIM_SEVENTH_EXTENSION_CORE_TEMPLATES:
            if chroma24_contains(chroma24_hdim, template_core):
                remaining_intervals, ext_removed, ext_components = parse_extra_notes(
                    chroma24_hdim, template_core, HALFDIM_EXT_ALL, max_extra_ext = 2
                )
                extra_ext_string = create_extension_string_from_notes(ext_removed, exts = INT2EXT_HALFDIM)
                importance = IMP_MID - len(ext_removed)
                sensible = not(len(extra_ext_string)>0 and inverted)
                if sensible:
                    if ext_components in HALFDIM_9_EXT_TEMPLATES:
                        return HALFDIM_9 + extra_ext_string, importance
                    if ext_components in HALFDIM_11_EXT_TEMPLATES:
                        return HALFDIM_11 + extra_ext_string, importance
                    if ext_components in HALFDIM_b13_EXT_TEMPLATES:
                        return HALFDIM_b13 + extra_ext_string, importance
                    elif len(ext_components) == 0 and len(ext_removed) <= 2:
                        return HALFDIM_7 + extra_ext_string, importance
                
    return False


chord_quality_checklist = [
    is_intervals, 
    is_major_basics, 
    is_major_less_basics,
    is_minor_basics, 
    is_minor_less_basics,
    is_dominant_basics,
    is_dominant_less_basics,
    is_sus_basics,
    is_aug_basics,
    is_dim_basics,
    is_dim_less_basics,
    is_alt,
    is_triad_extensions,
    is_major_seventh_sixth_extensions,
    is_halfdim_seventh_extensions,
    is_minor_seventh_sixth_extensions,
    is_dom_seventh_extensions,
    is_sus_seventh_extensions,
    is_aug_major_seventh_extensions,
    is_dim_seventh_extensions,
    #TODO: detect scales
    #TODO: detect multi-intervals (4,5)
]

bass_removed_chord_quality_checklist = [
    is_major_basics, 
    is_minor_basics, 
    is_dominant_basics,
    is_dim_basics,
]

'''
    List all possible / the most probable chord quality given a chroma24
    This is the core function of chord identification, using chord_quality_checklist
    Input: a chroma24 feature
    Output: list of possible chord quality strings, list of importance for each chord quality result
'''
def chroma24_to_chord_quality(chroma24_input:List[int], 
    inverted:bool = False, rectify:bool = True, list_all:bool = True
) -> (List[str], List[int]):
    if rectify:
        chroma24 = rectify_chroma24(chroma24_input)
    else:
        chroma24 = chroma24_input
        
    detected = False
    results = []
    imps = []
    for determine_func in chord_quality_checklist:
        chroma12_input, chroma12_is_octave = chroma24_to_12(chroma24_input)
        detected_and_imp = determine_func(chroma24_input, chroma12_input, chroma12_is_octave, inverted)
        if detected_and_imp:
            detected = detected_and_imp[0]
            imp = detected_and_imp[1]
            if detected not in results:
                results.append(detected)
                imps.append(imp)
                
    if not list_all:
        if len(results) == 0:
            return [UNK_CHORD], [IMP_NA]
        
        max_imp_id = np.argmax(imps)
        return [results[max_imp_id]],[imps[max_imp_id]]
    else:
        if len(results) == 0:
            return [UNK_CHORD], [IMP_NA]
        return results, imps

'''
    Detect chords like G/C, Bdim/C
'''
def is_basic_bass_modified_chords(bass_note:int, chroma24_input:List[int]):
    if len(chroma24_input)>=3:
        new_bass, bass_removed_chroma24 = remove_bass(bass_note, chroma24_input)
        if not is_3rd(new_bass - bass_note):
            for determine_func in bass_removed_chord_quality_checklist:
                chroma12_input, chroma12_is_octave = chroma24_to_12(bass_removed_chroma24)
                detected_and_imp = determine_func(bass_removed_chroma24, chroma12_input, chroma12_is_octave, inverted=False)
                if detected_and_imp:
                    return (new_bass,detected_and_imp[0],bass_note)
    return False

'''
    This is the main function of chord identification
    Iteratively use chroma24_to_chord_quality, where each iter considers a unique inversion
    Input: bass_note, chroma24
    Output: list of possible chord symbols in format (root_note, chord_quality_string, bass_note)
            bass_note = None, when the corresponding chord symbol is not inversion or bass-modified
'''
def bass_chroma24_to_chord_symbol(bass_note:int, chroma24_input:List[int], 
    detect_inversion:bool = False, list_all:bool = True, return_midi_num:bool = True
) -> List[Tuple[int,str,Optional[int]]]:
    
    symbs, imps = chroma24_to_chord_quality(chroma24_input, inverted = False, list_all = list_all)
    root_symb_bass_modified = is_basic_bass_modified_chords(bass_note, chroma24_input)
    root_notes = [bass_note]*len(symbs)
    inversion_bass_notes = [None]*len(symbs)
    if root_symb_bass_modified:
        root_notes.append(root_symb_bass_modified[0])
        symbs.append(root_symb_bass_modified[1])
        inversion_bass_notes.append(root_symb_bass_modified[2])
        imps.append(IMP_HIGH)
    
    if not detect_inversion:
        if not return_midi_num:
            root_notes = [PITCH_NUM_2_NAME[note%12] for note in root_notes]
            bass_note = PITCH_NUM_2_NAME[bass_note%12]
        if list_all:
            return zip(root_notes, symbs, inversion_bass_notes)
        else:
            max_imp_id = np.argmax(imps)
            return [(root_notes[max_imp_id], symbs[max_imp_id], inversion_bass_notes[max_imp_id])]
    
    else:
        results = []
        result_imps = []
        for note, symb, bass, imp in zip(root_notes, symbs, inversion_bass_notes, imps):
            if symb != UNK_CHORD:
                results.append((note,symb,bass))
                result_imps.append(imp)

        new_chroma24 = chroma24_input[:]
        new_bass = bass_note
        for i in range(len(chroma24_input)):
            new_bass, new_chroma24 = inv_invert(new_bass, new_chroma24)
            symbs, imps = chroma24_to_chord_quality(new_chroma24, inverted = True)
            
            for symb, imp in zip(symbs, imps):
                if symb != UNK_CHORD:
                    results.append((new_bass, symb, bass_note))
                    result_imps.append(imp)

        if not return_midi_num:
            bass_name = PITCH_NUM_2_NAME[bass_note%12]
            results = [(PITCH_NUM_2_NAME[note%12],symb,bass_name) for note,symb,_ in results]
            bass_note = PITCH_NUM_2_NAME[bass_note%12]
                    
        if len(results) == 0:
            return [(bass_note,UNK_CHORD,bass_note)]
        
        if list_all:
            return list(dict.fromkeys(results))
        else:
            max_imp_id = np.argmax(result_imps)
            return [results[max_imp_id]]

def notes_to_chord_symbol(chord_notes:List[int], 
    detect_inversion:bool = False, list_all:bool = True, return_midi_num:bool = True
) -> List[Tuple[int,str,Optional[int]]]:
    bass, chroma24 = get_bass_chroma24(chord_notes)
    return bass_chroma24_to_chord_symbol(
        bass, chroma24, detect_inversion, list_all, return_midi_num
    )
        
def form_chord_name(root_note:int, symb:str, bass_note:Optional[int] = None) -> str:
    if type(root_note) != str:
        root_note = PITCH_NUM_2_NAME[root_note%12]
        
    if bass_note is None:
         return root_note + "-" + symb
    else:
        if type(bass_note) != str:
            bass_note = PITCH_NUM_2_NAME[bass_note%12]
        return root_note + "-" + symb + f"-on-" + bass_note

def bass_chroma24_to_chord_name(bass_note:int, chroma24_input:List[int], 
    detect_inversion:bool = False, list_all:bool = True
) -> List[str]:
    name_results = []
    root_symb_bass_results = bass_chroma24_to_chord_symbol(
        bass_note, chroma24_input, detect_inversion, list_all
    )
    for root, symb, bass in root_symb_bass_results:
        name_results.append(form_chord_name(root, symb, bass))
    return name_results

def notes_to_chord_name(chord_notes:List[int],
    detect_inversion:bool = False, list_all:bool = True, return_midi_num:bool = True
) -> List[str]:
    bass, chroma24 = get_bass_chroma24(chord_notes)
    return bass_chroma24_to_chord_name(
        bass, chroma24, detect_inversion, list_all
    )

def chord_to_voicing(root, chord_type, bass, chord_notes = [], invert_voicing_times = 0, bass_max = 50, voicing_min = 50, p_remove_note = 0.0):
    if bass is None:
        bass = root
    
    if UNK_CHORD in chord_type:
        voicing = chord_notes[:]
    else:
        extension_strings = get_extensions(chord_type)
        extension_intervals = []
        for ext_str in extension_strings:
            extension_intervals.append(EXT2INT[ext_str])

        chord_type_no_ext = remove_extension(chord_type)
        if chord_type_no_ext in CHORD_2_VOICING:
            voicing = CHORD_2_VOICING[chord_type_no_ext]
            voicing += extension_intervals
            voicing = [p+bass for p in voicing]
        else:
            voicing = chord_notes[:]
        
    voicing.sort()
    if invert_voicing_times > 0:
        voicing = invert_no_chrma24(voicing, time_inversion = invert_voicing_times)
    elif invert_voicing_times < 0:
        voicing = inv_invert_no_chrma24(voicing, time_inversion = -invert_voicing_times)
    
    j = 0
    while j < len(voicing):
        if np.random.random() < p_remove_note:
            voicing.pop(j)
        if j < len(voicing):
            while voicing[j] < voicing_min:
                voicing[j] = voicing[j] +12
        j += 1
    
    voicing.sort()
    while bass > bass_max:
        bass = bass - 12
    
    return bass, voicing