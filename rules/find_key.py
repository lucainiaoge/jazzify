import music21
from music21 import harmony
from rules.scales import PITCH_NUM_2_NAME
from rules.chord2symbol import get_bass_chroma24, notes_to_chord_symbol
from rules.intervals import *
from rules.chord_symbols import *
import numpy as np

UNKNOWN_KEY = "UNK"
KEY_MINOR_2_PARALLEL_MAJOR = INT_m3

def to_major_key(key_root):
    return key_root%12
# minor keys are negative
def to_minor_key(minor_key_root):
    return (minor_key_root)%12 - 12

def to_canonical_key(key_root):
    if key_root < 0:
        return (key_root + KEY_MINOR_2_PARALLEL_MAJOR)%12
    else:
        return key_root%12

KEY_INTEGER_TO_STRING = {
    -12: "c-minor",
    -11: "c#-minor",
    -10: "d-minor",
    -9: "eb-minor",
    -8: "e-minor",
    -7: "f-minor",
    -6: "f#-minor",
    -5: "g-minor",
    -4: "g#-minor",
    -3: "a-minor",
    -2: "bb-minor",
    -1: "b-minor",
    0: "C-Major",
    1: "Db-Major",
    2: "D-Major",
    3: "Eb-Major",
    4: "E-Major",
    5: "F-Major",
    6: "Gb-Major",
    7: "G-Major",
    8: "Ab-Major",
    9: "A-Major",
    10: "Bb-Major",
    11: "B-Major",
    UNKNOWN_KEY : "unknown"
}
    

# CFG for harmony intro
# https://hellocodeblog.com/post/generating-harmony-using-context-free-grammar/

def find_pos_in_12(pitches):
    return [pitch % 12 for pitch in pitches]

'''
    chord symbol to roman numeric guesses
'''

def is_major_quality(chord_symb):
    return chord_symb[:len(MAJOR)] == MAJOR

def is_minor_quality(chord_symb):
    return chord_symb[:len(MINOR)] == MINOR

def has_7_9_11_13_extension(chord_symb):
    return ("seventh" in chord_symb) or (
        "ninth" in chord_symb) or (
        "11th" in chord_symb) or (
        "#11" in chord_symb) or (
        "13th" in chord_symb)


# I, i
def can_be_major_tonic(chord_symb):
    if is_major_quality(chord_symb):
        return True
    else:
        return False
    
def can_be_minor_tonic(chord_symb):
    if is_minor_quality(chord_symb):
        return True
    else:
        return False

def can_be_major_aug(chord_symb):
    if AUG in chord_symb:
        return True
    else:
        return False
    
# IV, II, iv, ii, N6
def can_be_major_subdominant_IV(chord_symb):
    if is_major_quality(chord_symb):
        return True
    else:
        return False

def can_be_har_major_subdominant_IV(chord_symb):
    if is_minor_quality(chord_symb):
        return True
    else:
        return False
    
def can_be_major_subdominant_ii(chord_symb):
    if is_minor_quality(chord_symb) and EXT_M7TH not in chord_symb:
        return True
    else:
        return False
    
def can_be_har_major_subdominant_ii(chord_symb):
    if HALFDIM in chord_symb or chord_symb == DIM:
        return True
    else:
        return False
    
def can_be_minor_subdominant_iv(chord_symb):
    if is_minor_quality(chord_symb) or DIM in chord_symb:
        return True
    else:
        return False

def can_be_har_minor_subdominant_IV(chord_symb): # this sounds like Dorian
    if can_be_dominant(chord_symb) or (
        is_major_quality(chord_symb) and not has_7_9_11_13_extension(chord_symb)):
        return True
    else:
        return False
    
def can_be_minor_subdominant_ii(chord_symb):
    if DIM in chord_symb:
        return True
    else:
        return False

def can_be_har_minor_subdominant_ii(chord_symb):
    if is_minor_quality(chord_symb) and EXT_M7TH not in chord_symb:
        return True
    else:
        return False
    
def can_be_napoleon(chord_symb): # bii
    if is_minor_quality(chord_symb):
        return True
    else:
        return False
    
# V, vii, bII
DOMINANT_CANDIDATE_LIST = [
    MAJOR,
    # all dominants
]
def can_be_dominant(chord_symb):
    if DOM in chord_symb or SUS in chord_symb or ALT in chord_symb:
        return True
    elif chord_symb in DOMINANT_CANDIDATE_LIST:
        return True
    else:
        return False

def must_be_dominant(chord_symb):
    if DOM in chord_symb or ALT in chord_symb:
        return True
    else:
        return False
    
def can_be_leading(chord_symb):
    if DIM in chord_symb and HALFDIM not in chord_symb:
        return True
    else:
        return False
    
def can_be_leading_major(chord_symb):
    if DIM in chord_symb:
        return True
    else:
        return False
    
def can_be_dominant_tritone(chord_symb):
    if DOM in chord_symb or ALT in chord_symb:
        return True
    else:
        return False

def can_be_v_minor(chord_symb):
    if chord_symb in [MINOR, MINOR_4, MINOR_7, MINOR_9]:
        return True
    else:
        return False
    
# iii, III
MAJOR_MEDIANT_CANDIDATE_LIST = [
    MINOR, MINOR_INT,
    MINOR_4, MINOR_7,
]
def can_be_major_mediant_iii(chord_symb):
    if chord_symb in MAJOR_MEDIANT_CANDIDATE_LIST:
        return True
    else:
        return False

def can_be_minor_mediant_III(chord_symb):
    if is_major_quality(chord_symb) and EXT_a11 not in chord_symb:
        return True
    else:
        return False

# vi, VI/vi
def can_be_major_subdominant_vi(chord_symb):
    if is_minor_quality(chord_symb):
        return True
    else:
        return False

def can_be_minor_subdominant_VI(chord_symb):
    if is_major_quality(chord_symb):
        return True
    else:
        return False


'''
    check if a chord is in the key
'''
DOMINANT_LEADING_STEPS = [
    INT_M7, (INT_M7+INT_m3*1)%12, (INT_M7+INT_m3*2)%12, (INT_M7+INT_m3*2)%12
]
DOUBLE_DOMINANT_LEADING_STEPS = [
    INT_a4, (INT_a4+INT_m3*1)%12, (INT_a4+INT_m3*2)%12, (INT_a4+INT_m3*2)%12
]
DIM_TONIC = 1
DIM_SUBDOMINANT = 2
DIM_DOMINANT = 3
DIM_DOUBLE_DOMINANT = 4
DIM_OTHER_FUNCS = 5
UNARY_FUNCTION_STRING_DICT = {
    DIM_TONIC: "tonic",
    DIM_SUBDOMINANT: "subdominant",
    DIM_DOMINANT: "dominant",
    DIM_DOUBLE_DOMINANT: "double-dominant",
    DIM_OTHER_FUNCS: "unknown-function"
}
def is_in_key_as_given(key_root, chord_root, chord_symb):
    if type(key_root) == str:
        return False
    chord_step = (chord_root - key_root)%12
    # major key
    if key_root >= 0:
        if chord_step == 0 and (can_be_major_tonic(chord_symb) or can_be_major_aug(chord_symb)):
            return DIM_TONIC
        elif chord_step == INT_m2 and can_be_napoleon(chord_symb):
            return DIM_SUBDOMINANT
        elif chord_step == INT_m2 and can_be_dominant(chord_symb):
            return DIM_DOMINANT
        elif chord_step == INT_M2 and (can_be_major_subdominant_ii(chord_symb) or can_be_har_major_subdominant_ii(chord_symb)):
            return DIM_SUBDOMINANT
        elif chord_step == INT_M2 and can_be_dominant(chord_symb):
            return DIM_DOUBLE_DOMINANT
        elif chord_step == INT_M3 and can_be_major_mediant_iii(chord_symb):
            return DIM_OTHER_FUNCS
        elif chord_step == INT_4 and (can_be_major_subdominant_IV(chord_symb) or can_be_har_major_subdominant_IV(chord_symb)):
            return DIM_SUBDOMINANT
        elif chord_step == INT_5 and can_be_dominant(chord_symb):
            return DIM_DOMINANT
        elif chord_step == INT_M6 and can_be_major_subdominant_vi(chord_symb):
            return DIM_SUBDOMINANT
        elif chord_step in DOMINANT_LEADING_STEPS and can_be_leading_major(chord_symb):
            return DIM_DOMINANT
        elif chord_step in DOUBLE_DOMINANT_LEADING_STEPS and can_be_leading_major(chord_symb):
            return DIM_DOUBLE_DOMINANT
        else:
            return False
    # minor key
    else:
        if chord_step == 0 and can_be_minor_tonic(chord_symb):
            return DIM_TONIC
        elif chord_step == INT_m2 and can_be_napoleon(chord_symb):
            return DIM_SUBDOMINANT
        elif chord_step == INT_m2 and can_be_dominant(chord_symb):
            return DIM_DOMINANT
        elif chord_step == INT_M2 and (can_be_minor_subdominant_ii(chord_symb) or can_be_har_minor_subdominant_ii(chord_symb)):
            return DIM_SUBDOMINANT
        elif chord_step == INT_M2 and can_be_dominant(chord_symb):
            return DIM_DOUBLE_DOMINANT
        elif chord_step == INT_m3 and can_be_minor_mediant_III(chord_symb):
            return DIM_OTHER_FUNCS
        elif chord_step == INT_4 and (can_be_minor_subdominant_iv(chord_symb) or can_be_har_minor_subdominant_IV(chord_symb)):
            return DIM_SUBDOMINANT
        elif chord_step == INT_5 and can_be_dominant(chord_symb):
            return DIM_DOMINANT
        elif chord_step == INT_m6 and can_be_minor_subdominant_VI(chord_symb):
            return DIM_SUBDOMINANT
        elif chord_step in DOMINANT_LEADING_STEPS and can_be_leading(chord_symb):
            return DIM_DOMINANT
        elif chord_step in DOUBLE_DOMINANT_LEADING_STEPS and can_be_leading_major(chord_symb):
            return DIM_DOUBLE_DOMINANT
        else:
            return False
    
# TODO: add more roman numeral candidate guesses
# refer to https://www.musictheory.net/calculators/analysis for more roman numeral candidates
'''
    binary chord progression rules
    returns: DIM_in_harmony_func_vector, key_guess
'''

# function hypothesis vector dimension definitions
DIM_STAY = 0
DIM_T2D = 1
DIM_T2S = 2
DIM_D2T = 3
DIM_S2D = 4
DIM_S2T = 5
DIM_T2DD = 6
DIM_S2DD = 7
DIM_DD2D = 8
DIM_DD2S = 9
DIM_OTHER_BINARY_FUNCS = 10
N_DIM_HFUNCTION = 11

BINARY_FUNCTION_STRING_DICT = {
    DIM_STAY: "holding",
    DIM_T2D: "tonic_to_dominant",
    DIM_T2S: "tonic_to_subdominant",
    DIM_D2T: "dominant_to_tonic",
    DIM_S2D: "subdominant_to_dominant",
    DIM_S2T: "subdominant_to_tonic",
    DIM_T2DD: "tonic_to_double_dominant",
    DIM_S2DD: "subdominant_to_double_dominant",
    DIM_DD2D: "double_dominant_to_dominant",
    DIM_OTHER_BINARY_FUNCS: "other_bianry_function"
}
def binary_functions_to_unary_functions(binary_function_list):
    N_chord = len(binary_function_list)
    function_list = [DIM_OTHER_FUNCS]*N_chord
    for i in reversed(range(N_chord)):
        if binary_function_list[i] in [DIM_T2D, DIM_T2S, DIM_T2DD]:
            function_list[i] = DIM_TONIC
        elif binary_function_list[i] in [DIM_S2D, DIM_S2T, DIM_S2DD]:
            function_list[i] = DIM_SUBDOMINANT
        elif binary_function_list[i] in [DIM_D2T]:
            function_list[i] = DIM_DOMINANT
        elif binary_function_list[i] in [DIM_DD2D]:
            function_list[i] = DIM_DOUBLE_DOMINANT
        elif binary_function_list[i] in [DIM_STAY] and i < N_chord - 1:
            function_list[i] = function_list[i+1]
        else:
            function_list[i] = DIM_OTHER_FUNCS
    return function_list

def get_binary_harmony_function_from_unary(function1, function2):
    if function1 == function2:
        return DIM_STAY
    elif function1 == DIM_TONIC and function2 == DIM_DOMINANT:
        return DIM_T2D
    elif function1 == DIM_TONIC and function2 == DIM_SUBDOMINANT:
        return DIM_T2S
    elif function1 == DIM_DOMINANT and function2 == DIM_TONIC:
        return DIM_D2T
    elif function1 == DIM_SUBDOMINANT and function2 == DIM_DOMINANT:
        return DIM_S2D
    elif function1 == DIM_SUBDOMINANT and function2 == DIM_TONIC:
        return DIM_S2T
    elif function1 == DIM_TONIC and function2 == DIM_DOUBLE_DOMINANT:
        return DIM_T2DD
    elif function1 == DIM_SUBDOMINANT and function2 == DIM_DOUBLE_DOMINANT:
        return DIM_S2DD
    elif function1 == DIM_DOUBLE_DOMINANT and function2 == DIM_DOMINANT:
        return DIM_DD2D
    else:
        return DIM_OTHER_BINARY_FUNCS

def must_be_repeating_chord(this_root, root_step, this_symb, next_symb):
    if root_step == 0 and this_symb == next_symb:
        return DIM_STAY, UNKNOWN_KEY
    return False

V_I_STEP = (-INT_5) % 12
I_IV_STEP = (-INT_5) % 12
II_V_STEP = (INT_4) % 12
II_I_STEP = (-INT_M2) % 12
def can_be_V_I_major(this_root, root_step, this_symb, next_symb):
    if root_step == V_I_STEP:
        if can_be_dominant(this_symb) and can_be_major_tonic(next_symb):
            return DIM_D2T, to_major_key(this_root+root_step)
    return False

def can_be_V_i_minor(this_root, root_step, this_symb, next_symb):
    if root_step == V_I_STEP:
        if can_be_dominant(this_symb) and can_be_minor_tonic(next_symb):
            return DIM_D2T, to_minor_key(this_root+root_step)
    return False

def can_be_v_i_minor(this_root, root_step, this_symb, next_symb):
    if root_step == V_I_STEP:
        if can_be_v_minor(this_symb) and can_be_minor_tonic(next_symb):
            return DIM_D2T, to_minor_key(this_root+root_step)
    return False

def can_be_I_IV_major(this_root, root_step, this_symb, next_symb):
    if root_step == I_IV_STEP:
        if can_be_major_tonic(this_symb) and can_be_major_subdominant_IV(next_symb):
            return DIM_T2S, to_major_key(this_root)
    return False

def can_be_i_iv_minor(this_root, root_step, this_symb, next_symb):
    if root_step == I_IV_STEP:
        if can_be_minor_tonic(this_symb) and can_be_minor_subdominant_iv(next_symb):
            return DIM_T2S, to_minor_key(this_root)
    return False

def can_be_II_V_major(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if can_be_major_subdominant_ii(this_symb) and can_be_dominant(next_symb):
            return DIM_S2D, to_major_key(this_root+II_I_STEP)
    return False

def can_be_ii_V_minor(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if can_be_minor_subdominant_ii(this_symb) and can_be_dominant(next_symb):
            return DIM_S2D, to_minor_key(this_root+II_I_STEP)
    return False

def can_be_ii_v_minor(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if can_be_minor_subdominant_ii(this_symb) and can_be_v_minor(next_symb):
            return DIM_S2D, to_minor_key(this_root+II_I_STEP)
    return False

def can_be_DD_V_major(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if can_be_dominant(this_symb) and can_be_dominant(next_symb):
            return DIM_DD2D, to_major_key(this_root+II_I_STEP)
    return False

def can_be_DD_V_minor(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if can_be_dominant(this_symb) and can_be_dominant(next_symb):
            return DIM_DD2D, to_minor_key(this_root+II_I_STEP)
    return False

# New
VI_I_STEP = INT_m3
def can_be_vi_ii_major(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if  can_be_major_subdominant_vi(this_symb) and can_be_major_subdominant_ii(next_symb):
            return DIM_STAY, to_major_key(this_root+VI_I_STEP)
    return False

def can_be_vi_DD_major(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if  can_be_major_subdominant_vi(this_symb) and can_be_dominant(next_symb):
            return DIM_S2DD, to_major_key(this_root+VI_I_STEP)
    return False

# musts
def must_be_V_I_major(this_root, root_step, this_symb, next_symb):
    if root_step == V_I_STEP:
        if must_be_dominant(this_symb) and can_be_major_tonic(next_symb):
            return DIM_D2T, to_major_key(this_root+root_step)
    return False

def must_be_V_i_minor(this_root, root_step, this_symb, next_symb):
    if root_step == V_I_STEP:
        if must_be_dominant(this_symb) and can_be_minor_tonic(next_symb):
            return DIM_D2T, to_minor_key(this_root+root_step)
    return False

def must_be_II_V_major(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if can_be_major_subdominant_ii(this_symb) and must_be_dominant(next_symb):
            return DIM_S2D, to_major_key(this_root+II_I_STEP)
    return False

def must_be_ii_V_minor(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if can_be_minor_subdominant_ii(this_symb) and must_be_dominant(next_symb):
            return DIM_S2D, to_minor_key(this_root+II_I_STEP)
    return False

def must_be_DD_V_major(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if must_be_dominant(this_symb) and can_be_dominant(next_symb):
            return DIM_DD2D, to_major_key(this_root+II_I_STEP)
    return False

def must_be_DD_V_minor(this_root, root_step, this_symb, next_symb):
    if root_step == II_V_STEP:
        if must_be_dominant(this_symb) and can_be_dominant(next_symb):
            return DIM_DD2D, to_minor_key(this_root+II_I_STEP)
    return False

I_V_STEP = (INT_5) % 12
IV_I_STEP = (INT_5) % 12
def can_be_IV_I_major(this_root, root_step, this_symb, next_symb):
    if root_step == IV_I_STEP:
        if can_be_major_subdominant_IV(this_symb) and can_be_major_tonic(next_symb):
            return DIM_T2S, to_major_key(this_root+root_step)
    return False

def can_be_iv_i_minor(this_root, root_step, this_symb, next_symb):
    if root_step == IV_I_STEP:
        if can_be_minor_subdominant_iv(this_symb) and can_be_minor_tonic(next_symb):
            return DIM_T2S, to_minor_key(this_root+root_step)
    return False

def can_be_I_V_major(this_root, root_step, this_symb, next_symb):
    if root_step == I_V_STEP:
        if can_be_major_tonic(this_symb) and can_be_dominant(next_symb):
            return DIM_T2D, to_major_key(this_root)
    return False

def can_be_i_V_minor(this_root, root_step, this_symb, next_symb):
    if root_step == I_V_STEP:
        if can_be_minor_tonic(this_symb) and can_be_dominant(next_symb):
            return DIM_T2D, to_minor_key(this_root)
    return False

def can_be_i_v_minor(this_root, root_step, this_symb, next_symb):
    if root_step == I_V_STEP:
        if can_be_minor_tonic(this_symb) and can_be_v_minor(next_symb):
            return DIM_T2D, to_minor_key(this_root)
    return False

def must_be_I_V_major(this_root, root_step, this_symb, next_symb):
    if root_step == I_V_STEP:
        if can_be_major_tonic(this_symb) and must_be_dominant(next_symb):
            return DIM_T2D, to_major_key(this_root)
    return False

def must_be_i_V_minor(this_root, root_step, this_symb, next_symb):
    if root_step == I_V_STEP:
        if can_be_minor_tonic(this_symb) and must_be_dominant(next_symb):
            return DIM_T2D, to_minor_key(this_root)
    return False

I_II_STEP = (INT_M2) % 12
IV_V_STEP = (INT_M2) % 12
def can_be_I_ii_major(this_root, root_step, this_symb, next_symb):
    if root_step == I_II_STEP:
        if can_be_major_tonic(this_symb) and can_be_major_subdominant_ii(next_symb):
            return DIM_T2S, to_major_key(this_root)
    return False

def can_be_i_II_minor(this_root, root_step, this_symb, next_symb):
    if root_step == I_II_STEP:
        if can_be_minor_tonic(this_symb) and can_be_minor_subdominant_ii(next_symb):
            return DIM_T2S, to_minor_key(this_root)
    return False

def can_be_IV_V_major(this_root, root_step, this_symb, next_symb):
    if root_step == IV_V_STEP:
        if can_be_major_subdominant_IV(this_symb) and can_be_dominant(next_symb):
            return DIM_S2D, to_major_key(this_root + IV_I_STEP)
    return False

def can_be_iv_V_minor(this_root, root_step, this_symb, next_symb):
    if root_step == IV_V_STEP:
        if can_be_minor_subdominant_iv(this_symb) and can_be_dominant(next_symb):
            return DIM_S2D, to_minor_key(this_root + IV_I_STEP)
    return False

def can_be_iv_v_minor(this_root, root_step, this_symb, next_symb):
    if root_step == IV_V_STEP:
        if can_be_minor_subdominant_iv(this_symb) and can_be_v_minor(next_symb):
            return DIM_S2D, to_minor_key(this_root + IV_I_STEP)
    return False

def must_be_IV_V_major(this_root, root_step, this_symb, next_symb):
    if root_step == IV_V_STEP:
        if can_be_major_subdominant_IV(this_symb) and must_be_dominant(next_symb):
            return DIM_S2D, to_major_key(this_root + IV_I_STEP)
    return False

def must_be_iv_V_minor(this_root, root_step, this_symb, next_symb):
    if root_step == IV_V_STEP:
        if can_be_minor_subdominant_iv(this_symb) and must_be_dominant(next_symb):
            return DIM_S2D, to_minor_key(this_root + IV_I_STEP)
    return False

def can_be_T_DD_major(this_root, root_step, this_symb, next_symb):
    if root_step == I_II_STEP:
        if can_be_major_tonic(this_symb) and can_be_dominant(next_symb):
            return DIM_T2DD, to_major_key(this_root)
    return False

def can_be_t_DD_minor(this_root, root_step, this_symb, next_symb):
    if root_step == I_II_STEP:
        if can_be_minor_tonic(this_symb) and can_be_dominant(next_symb):
            return DIM_T2DD, to_minor_key(this_root)
    return False

def must_be_T_DD_major(this_root, root_step, this_symb, next_symb):
    if root_step == I_II_STEP:
        if can_be_major_tonic(this_symb) and must_be_dominant(next_symb):
            return DIM_T2DD, to_major_key(this_root)
    return False

def must_be_t_DD_minor(this_root, root_step, this_symb, next_symb):
    if root_step == I_II_STEP:
        if can_be_minor_tonic(this_symb) and must_be_dominant(next_symb):
            return DIM_T2DD, to_minor_key(this_root)
    return False

VII_I_STEP = (INT_m2) % 12
LEAD_I_STEPS = [
    VII_I_STEP, (VII_I_STEP + INT_m3) % 12, 
    (VII_I_STEP + INT_m3*2) % 12, 
    (VII_I_STEP + INT_m3*3) % 12
]
def can_be_vii_I_major(this_root, root_step, this_symb, next_symb):
    if root_step in LEAD_I_STEPS:
        if can_be_leading(this_symb) and can_be_major_tonic(next_symb):
            return DIM_D2T, to_major_key(this_root+root_step)
    return False
def can_be_vii_i_minor(this_root, root_step, this_symb, next_symb):
    if root_step in LEAD_I_STEPS:
        if can_be_leading(this_symb) and can_be_minor_tonic(next_symb):
            return DIM_D2T, to_minor_key(this_root+root_step)
    return False

I_IILEAD_STEPS = [
    INT_a4, (INT_a4 + INT_m3) % 12, 
    (INT_a4 + INT_m3*2) % 12, 
    (INT_a4 + INT_m3*3) % 12
]
def can_be_T_DDvii_major(this_root, root_step, this_symb, next_symb):
    if root_step in I_IILEAD_STEPS:
        if (can_be_minor_tonic(this_symb) or can_be_major_tonic(this_symb)) and can_be_leading(next_symb):
            return DIM_T2DD, to_major_key(this_root)
    return False

def can_be_t_DDvii_minor(this_root, root_step, this_symb, next_symb):
    if root_step in I_IILEAD_STEPS:
        if (can_be_minor_tonic(this_symb) or can_be_major_tonic(this_symb)) and can_be_leading(next_symb):
            return DIM_T2DD, to_minor_key(this_root)
    return False

IILEAD_V_STEPS = [
    INT_m2, (INT_m2 + INT_m3) % 12, 
    (INT_m2 + INT_m3*2) % 12, 
    (INT_m2 + INT_m3*3) % 12
]
def can_be_DDvii_V_major(this_root, root_step, this_symb, next_symb):
    if root_step in IILEAD_V_STEPS:
        if can_be_leading(this_symb) and can_be_dominant(next_symb):
            return DIM_DD2D, to_major_key(this_root + root_step + V_I_STEP)
    return False

def can_be_DDvii_V_minor(this_root, root_step, this_symb, next_symb):
    if root_step in IILEAD_V_STEPS:
        if can_be_leading(this_symb) and can_be_dominant(next_symb):
            return DIM_DD2D, to_minor_key(this_root + root_step + V_I_STEP)
    return False

def must_be_DDvii_V_major(this_root, root_step, this_symb, next_symb):
    if root_step in IILEAD_V_STEPS:
        if can_be_leading(this_symb) and must_be_dominant(next_symb):
            return DIM_DD2D, to_major_key(this_root + root_step + V_I_STEP)
    return False

def must_be_DDvii_V_minor(this_root, root_step, this_symb, next_symb):
    if root_step in IILEAD_V_STEPS:
        if can_be_leading(this_symb) and must_be_dominant(next_symb):
            return DIM_DD2D, to_minor_key(this_root + root_step + V_I_STEP)
    return False

N_T_STEP = (-INT_m2) % 12
T_N_STEP = (INT_m2) % 12
N_K_STEP = (-INT_M2) % 12
N_V_STEP = (INT_a4) % 12
def must_be_N_D_major(this_root, root_step, this_symb, next_symb):
    if root_step == N_K_STEP: #bii->K46
        if can_be_napoleon(this_symb) and is_major_quality(next_symb):
            return DIM_S2D, to_major_key(this_root + N_T_STEP)
    if root_step == N_V_STEP % 12: #bii->V
        if can_be_napoleon(this_symb) and can_be_dominant(next_symb):
            return DIM_S2D, to_major_key(this_root + N_T_STEP)
    return False

def must_be_N_D_minor(this_root, root_step, this_symb, next_symb):
    if root_step == N_K_STEP: #bii->K46
        if can_be_napoleon(this_symb) and is_minor_quality(next_symb):
            return DIM_S2D, to_minor_key(this_root + N_T_STEP)
    if root_step == N_V_STEP % 12: #bii->V
        if can_be_napoleon(this_symb) and can_be_dominant(next_symb):
            return DIM_S2D, to_minor_key(this_root + N_T_STEP)
    return False

def must_be_tritone_I_major(this_root, root_step, this_symb, next_symb):
    if root_step == N_T_STEP: #bII->I
        if can_be_dominant_tritone(this_symb) and can_be_major_tonic(next_symb):
            return DIM_D2T, to_major_key(this_root + N_T_STEP)
        
def must_be_tritone_i_minjor(this_root, root_step, this_symb, next_symb):
    if root_step == N_T_STEP: #bII->I
        if can_be_dominant_tritone(this_symb) and can_be_minor_tonic(next_symb):
            return DIM_D2T, to_minor_key(this_root + N_T_STEP)
        

# new
I_vi_STEP = (-INT_m3) % 12
i_VI_STEP = (-INT_M3) % 12

def can_be_I_vi_major(this_root, root_step, this_symb, next_symb):
    if root_step == I_vi_STEP:
        if can_be_major_tonic(this_symb) and can_be_major_subdominant_vi(next_symb):
            return DIM_T2S, to_major_key(this_root)
    return False

def can_be_VI_iv_minor(this_root, root_step, this_symb, next_symb):
    if root_step == I_vi_STEP:
        if can_be_minor_subdominant_VI(this_symb) and can_be_minor_subdominant_iv(next_symb):
            return DIM_STAY, to_minor_key(this_root - i_VI_STEP)
    return False

def can_be_i_VI_minor(this_root, root_step, this_symb, next_symb):
    if root_step == i_VI_STEP:
        if can_be_minor_tonic(this_symb) and can_be_minor_subdominant_VI(next_symb):
            return DIM_T2S, to_minor_key(this_root)
    return False

def can_be_vi_IV_major(this_root, root_step, this_symb, next_symb):
    if root_step == i_VI_STEP:
        if can_be_major_subdominant_vi(this_symb) and can_be_major_subdominant_IV(next_symb):
            return DIM_STAY, to_major_key(this_root - I_vi_STEP )
    return False

# new
def can_be_ii_IV_major(this_root, root_step, this_symb, next_symb):
    if root_step == VI_I_STEP:
        if  can_be_major_subdominant_ii(this_symb) and can_be_major_subdominant_IV(next_symb):
            return DIM_STAY, to_major_key(this_root+II_I_STEP)
    return False

def can_be_DD_IV_major(this_root, root_step, this_symb, next_symb):
    if root_step == VI_I_STEP:
        if  can_be_dominant(this_symb) and can_be_major_subdominant_IV(next_symb):
            return DIM_DD2S, to_major_key(this_root+II_I_STEP)
    return False

def can_be_ii_iv_minor(this_root, root_step, this_symb, next_symb):
    if root_step == VI_I_STEP:
        if  can_be_minor_subdominant_ii(this_symb) and can_be_minor_subdominant_iv(next_symb):
            return DIM_STAY, to_minor_key(this_root+II_I_STEP)
    return False

def can_be_DD_iv_minor(this_root, root_step, this_symb, next_symb):
    if root_step == VI_I_STEP:
        if  can_be_dominant(this_symb) and can_be_minor_subdominant_iv(next_symb):
            return DIM_DD2S, to_minor_key(this_root+II_I_STEP)
    return False

# TODO: consider more tuple progressions

def get_root_symb_bass_from_progression(chord_list):
    n_chord = len(chord_list)
    root_list = [None]*n_chord
    symb_list = [None]*n_chord
    bass_list = [None]*n_chord
    for i,chord in enumerate(chord_list):
        root_list[i], symb_list[i], bass_list[i] = notes_to_chord_symbol(chord, detect_inversion = True, list_all = False)[0]
    return root_list, symb_list, bass_list

def get_root_steps(root_list):
    root_vector = np.array(root_list + [root_list[-1]])
    return (root_vector[1:] - root_vector[:-1]) % 12

# binary rules that are able to determine key
binary_harmony_checklist_musts_V_I_FAMILY = [
    # V_I_STEP or II_V_STEP
    must_be_V_I_major,
    must_be_V_i_minor,
    must_be_II_V_major,
    must_be_ii_V_minor,
    must_be_DD_V_major,
    must_be_DD_V_minor,
]
binary_harmony_checklist_musts_I_V_FAMILY = [
    # I_V_STEP or IV_I_STEP
    must_be_I_V_major,
    must_be_i_V_minor,
]
binary_harmony_checklist_musts_IV_V_FAMILY = [
    # IV_V_STEP or I_II_STEP
    must_be_IV_V_major,
    must_be_iv_V_minor,
    must_be_T_DD_major,
    must_be_t_DD_minor,
]
binary_harmony_checklist_musts_IILEAD_V = [
    # IILEAD_V_STEPS
    must_be_DDvii_V_major,
    must_be_DDvii_V_minor,
]
binary_harmony_checklist_musts_N_D = [
    # N_K_STEP or N_V_STEP
    must_be_N_D_major,
    must_be_N_D_minor,
]
binary_harmony_checklist_musts_tritone_I = [
    # N_T_STEP
    must_be_tritone_I_major,
    must_be_tritone_i_minjor,
]

binary_harmony_checklist_musts = [
    ([0], [must_be_repeating_chord]),
    ([V_I_STEP], binary_harmony_checklist_musts_V_I_FAMILY),
    ([I_V_STEP], binary_harmony_checklist_musts_I_V_FAMILY),
    ([IV_V_STEP], binary_harmony_checklist_musts_IV_V_FAMILY),
    (IILEAD_V_STEPS, binary_harmony_checklist_musts_IILEAD_V),
    ([N_K_STEP, N_V_STEP], binary_harmony_checklist_musts_N_D),
    ([N_T_STEP],binary_harmony_checklist_musts_tritone_I),
]

# binary rules that can give key guesses
binary_harmony_checklist_cans_V_I_FAMILY = [
    # V_I_STEP or II_V_STEP
    can_be_V_I_major,
    can_be_V_i_minor,
    can_be_v_i_minor,
    can_be_I_IV_major,
    can_be_i_iv_minor,
    can_be_II_V_major,
    can_be_ii_V_minor,
    can_be_ii_v_minor,
    can_be_DD_V_major,
    can_be_DD_V_minor,
    can_be_vi_ii_major,
    can_be_vi_DD_major,
]
binary_harmony_checklist_cans_I_V_FAMILY = [
    # I_V_STEP or IV_I_STEP
    can_be_IV_I_major,
    can_be_iv_i_minor,
    can_be_I_V_major,
    can_be_i_V_minor,
    can_be_i_v_minor,
]
binary_harmony_checklist_cans_IV_V_FAMILY = [
    # IV_V_STEP or I_II_STEP
    can_be_I_ii_major,
    can_be_i_II_minor,
    can_be_IV_V_major,
    can_be_iv_V_minor,
    can_be_iv_v_minor,
    can_be_T_DD_major,
    can_be_t_DD_minor,
]
binary_harmony_checklist_cans_LEAD_I = [
    # LEAD_I_STEPS
    can_be_vii_I_major,
    can_be_vii_i_minor,
]
binary_harmony_checklist_cans_I_IILEAD = [
    # I_IILEAD_STEPS
    can_be_T_DDvii_major,
    can_be_t_DDvii_minor,
]
binary_harmony_checklist_cans_IILEAD_V = [
    # IILEAD_V_STEPS
    can_be_DDvii_V_major,
    can_be_DDvii_V_minor,
]
binary_harmony_checklist_cans_I_vi = [
    # I_vi_STEP
    can_be_I_vi_major,
    can_be_VI_iv_minor,
]
binary_harmony_checklist_cans_i_VI = [
    # i_VI_STEP
    can_be_i_VI_minor,
    can_be_vi_IV_major,
]
binary_harmony_checklist_cans_ii_IV = [
    # VI_I_STEP
    can_be_ii_IV_major,
    can_be_DD_IV_major,
    can_be_ii_iv_minor,
    can_be_DD_iv_minor,
]
binary_harmony_checklist_cans = [
    ([V_I_STEP], binary_harmony_checklist_cans_V_I_FAMILY),
    ([I_V_STEP], binary_harmony_checklist_cans_I_V_FAMILY),
    ([IV_V_STEP], binary_harmony_checklist_cans_IV_V_FAMILY),
    (LEAD_I_STEPS, binary_harmony_checklist_cans_LEAD_I),
    (I_IILEAD_STEPS, binary_harmony_checklist_cans_I_IILEAD),
    (IILEAD_V_STEPS, binary_harmony_checklist_cans_IILEAD_V),
    ([I_vi_STEP], binary_harmony_checklist_cans_I_vi),
    ([i_VI_STEP], binary_harmony_checklist_cans_i_VI),
    ([VI_I_STEP], binary_harmony_checklist_cans_ii_IV)
]

'''
round 1: detect progressions that must determine key
round 2: detect progressions that may determine key (list all candidate keys along with functions)
round 3: decide keys based on the observed hypothesis (e.g., ii-V-I)
round 4: for each hypothesis, try to complete the whole chord progression with keys
round 5: select the most probable key decision track

e.g. given a chord transition C -> G
function_key_tuples = [(DIM_T2D, 0), (DIM_S2T, 7)]
'''

def get_binary_harmony_functions(this_root, root_step, this_symb, next_symb):
    function_key_tuples = []
    root_step = root_step % 12
    for root_step_choices, checker_rules in binary_harmony_checklist_musts:
        if root_step in root_step_choices:
            for checker_rule in checker_rules:
                checker_result = checker_rule(this_root, root_step, this_symb, next_symb)
                if checker_result:
                    function_key_tuples.append((checker_result[0], checker_result[1]))
                    return function_key_tuples
                
    for root_step_choices, checker_rules in binary_harmony_checklist_cans:
        if root_step in root_step_choices:
            for checker_rule in checker_rules:
                checker_result = checker_rule(this_root, root_step, this_symb, next_symb)
                if checker_result:
                    if (checker_result[0], checker_result[1]) not in function_key_tuples:
                        function_key_tuples.append((checker_result[0], checker_result[1]))
#             break
    return function_key_tuples


#     root_list, symb_list, bass_list = get_root_symb_bass_from_progression(chord_list)
def get_binary_progression_key_guesses(root_list, symb_list):
    N_chord = len(root_list)
    assert N_chord == len(symb_list), "Input length should be the same"
    if N_chord <= 1:
        return [[] for _ in range(N_chord)]
    
    root_step_list = get_root_steps(root_list)
    function_key_tuples_list = [None] * N_chord
    function_key_tuples_list[-1] = [(DIM_STAY, UNKNOWN_KEY)]
    for i in range(N_chord - 1):
        function_key_tuples_list[i] = get_binary_harmony_functions(
            root_list[i], root_step_list[i], symb_list[i], symb_list[i+1]
        )
    
    return function_key_tuples_list # list[list[(FUNC_DIM,KEY)]]

QUATERNERY_KEY_DETERMINE_TRANSITIONS = [
    (DIM_T2S, DIM_S2D, DIM_D2T),
    (DIM_STAY, DIM_S2D, DIM_D2T),
    (DIM_T2S, DIM_S2DD, DIM_DD2D),
    (DIM_T2DD, DIM_DD2D, DIM_D2T),
    (DIM_T2DD, DIM_DD2S, DIM_S2D),
    (DIM_T2D, DIM_D2T, DIM_T2D), # not quite sure
    (DIM_T2S, DIM_S2T, DIM_T2S),
]

TERNERY_KEY_DETERMINE_TRANSITIONS = [
    (DIM_S2D, DIM_D2T),
    (DIM_S2DD, DIM_DD2D),
    (DIM_DD2D, DIM_D2T),
    (DIM_T2S, DIM_S2D),
]

def rectify_in_deterministic_key(function_key_tuples_list, root_list, symb_list, chord_index, hop):
    modified = False
    target_index = chord_index + hop
    N_chords = len(function_key_tuples_list)
    if target_index < 0 or target_index >= N_chords:
        return modified, function_key_tuples_list

    function_key_tuples = function_key_tuples_list[target_index]
    if len(function_key_tuples) != 1:
        return modified, function_key_tuples_list

    key_root = function_key_tuples[0][1]
    target_function = is_in_key_as_given(key_root, root_list[target_index], symb_list[target_index])
    if key_root != UNKNOWN_KEY:
        function = is_in_key_as_given(key_root, root_list[chord_index], symb_list[chord_index])
    else:
        function = False

    if hop == 1:
        binary_function = get_binary_harmony_function_from_unary(function, target_function)
    else:
        binary_function = DIM_OTHER_BINARY_FUNCS

    if function:
        function_key_tuples_list[chord_index] = [(binary_function, key_root)]
        modified = True

    return modified, function_key_tuples_list

# this function implements the inertia of key perception
def visit_nearby_deterministic_key(function_key_tuples_list, root_list, symb_list, chord_index, hopps = [-1,-2,1,2,-3,3,-4,4]):
    modified = False
    resulting_hop = hopps[0]
    for hop in hopps:
        resulting_hop = hop
        modified, function_key_tuples_list = rectify_in_deterministic_key(function_key_tuples_list, root_list, symb_list, chord_index, hop)
        if modified:
            break
    return modified, function_key_tuples_list, resulting_hop

def rectify_sandwiched_chord(function_key_tuples_list, root_list, symb_list, chord_index):
    N_chords = len(function_key_tuples_list)
    modified = False
    if chord_index < 1 or chord_index >= N_chords - 1:
        return modified, function_key_tuples_list

    function_key_tuples_left = function_key_tuples_list[chord_index-1]
    function_key_tuples_right = function_key_tuples_list[chord_index+1]
    function_key_tuples_this = function_key_tuples_list[chord_index]
    if len(function_key_tuples_left) == 1 and len(function_key_tuples_right) == 1:
        key_left = function_key_tuples_left[0][1]
        key_right = function_key_tuples_right[0][1]
        if key_left == key_right and len(function_key_tuples_this) == 0:
            function_key_tuples_list[chord_index] = [(DIM_OTHER_BINARY_FUNCS, key_left)]
            modified = True
    return modified, function_key_tuples_list

# this function could rewrite function_key_tuples1, function_key_tuples2
def rectify_quaternery_transition(function_key_tuples1, function_key_tuples2, function_key_tuples3):
    if len(function_key_tuples1) > 0 and len(function_key_tuples2) > 0 and len(function_key_tuples3) > 0:
        functions1, keys1 = tuple(zip(*function_key_tuples1)) #unzip
        functions2, keys2 = tuple(zip(*function_key_tuples2)) #unzip
        functions3, keys3 = tuple(zip(*function_key_tuples3)) #unzip
        for quaternery_rule in QUATERNERY_KEY_DETERMINE_TRANSITIONS:
            if quaternery_rule[0] in functions1 and quaternery_rule[1] in functions2 and quaternery_rule[2] in functions3:
                index1 = functions1.index(quaternery_rule[0])
                index2 = functions2.index(quaternery_rule[1])
                index3 = functions3.index(quaternery_rule[2])
                if keys1[index1] == keys2[index2] and keys2[index2] == keys3[index3]:
                    function_key_tuples1 = [function_key_tuples1[index1]]
                    function_key_tuples2 = [function_key_tuples2[index2]]
                    function_key_tuples3 = [function_key_tuples3[index3]]
                    return function_key_tuples1, function_key_tuples2, function_key_tuples3
    return False

# this function could rewrite function_key_tuples1, function_key_tuples2
def rectify_ternery_transition(function_key_tuples1, function_key_tuples2):
    if len(function_key_tuples1) > 0 and len(function_key_tuples2) > 0:
        functions1, keys1 = tuple(zip(*function_key_tuples1)) #unzip
        functions2, keys2 = tuple(zip(*function_key_tuples2)) #unzip
        for ternery_rule in TERNERY_KEY_DETERMINE_TRANSITIONS:
            if ternery_rule[0] in functions1 and ternery_rule[1] in functions2:
                index1 = functions1.index(ternery_rule[0])
                index2 = functions2.index(ternery_rule[1])
                if keys1[index1] == keys2[index2]:
                    function_key_tuples1 = [function_key_tuples1[index1]]
                    function_key_tuples2 = [function_key_tuples2[index2]]
                    return function_key_tuples1, function_key_tuples2
    return False

def rectify_key_list_with_quaternery_transitions(function_key_tuples_list):
    N_chord = len(function_key_tuples_list)
    if N_chord <= 3:
        return function_key_tuples_list
    i = 0
    while i < (N_chord - 3):
        bias1 = 1
        bias2 = 2
        while i < (N_chord - 3) and function_key_tuples_list[i] == [(DIM_STAY, UNKNOWN_KEY)]:
            i += 1
        while i + bias1 < (N_chord - 2) and function_key_tuples_list[i+bias1] == [(DIM_STAY, UNKNOWN_KEY)]:
            bias1 += 1
            bias2 += 1
        while i + bias2 < (N_chord - 1) and function_key_tuples_list[i+bias2] == [(DIM_STAY, UNKNOWN_KEY)]:
            bias2 += 1
        rectified = rectify_quaternery_transition(
            function_key_tuples_list[i], function_key_tuples_list[i+bias1], function_key_tuples_list[i+bias2]
        )
        if rectified:
            function_key_tuples_list[i], function_key_tuples_list[i+bias1], function_key_tuples_list[i+bias2] = rectified
        i += 1
    return function_key_tuples_list

def rectify_key_list_with_ternery_transitions(function_key_tuples_list, root_list, symb_list, verbose = False):
    N_chord = len(function_key_tuples_list)
    if N_chord <= 2:
        return function_key_tuples_list
    i = 0
    while i < (N_chord - 2):
        bias1 = 1
        while i < (N_chord - 2) and function_key_tuples_list[i] == [(DIM_STAY, UNKNOWN_KEY)]:
            i += 1
        while i + bias1 < (N_chord - 1) and function_key_tuples_list[i+bias1] == [(DIM_STAY, UNKNOWN_KEY)]:
            bias1 += 1
            fk_tuples_before_modify = function_key_tuples_list[i+bias1][:]

            modified, function_key_tuples_list, resulting_hop = visit_nearby_deterministic_key(
                function_key_tuples_list, root_list, symb_list, i+bias1, hopps = [-1,-2,-3,-4,-5,-6]
            )
            fk_tuples_after_modify = function_key_tuples_list[i+bias1][:]
        if not modified:
            rectified = rectify_ternery_transition(
                function_key_tuples_list[i], function_key_tuples_list[i+bias1]
            )
            if rectified:
                function_key_tuples_list[i], function_key_tuples_list[i+bias1] = rectified
                fk_tuples_after_modify = function_key_tuples_list[i+bias1][:]
        if verbose:
            print("at step", i, ", modify", fk_tuples_before_modify, " into ", fk_tuples_after_modify)
        
        i += 1
    return function_key_tuples_list

def rectify_key_list_with_ternery_transitions(function_key_tuples_list, root_list, symb_list, verbose = False):
    N_chord = len(function_key_tuples_list)
    if N_chord <= 2:
        return function_key_tuples_list
    for i in range(N_chord - 2):
        fk_tuples_before_modify = function_key_tuples_list[i+1][:]
        
        modified, function_key_tuples_list, resulting_hop = visit_nearby_deterministic_key(
            function_key_tuples_list, root_list, symb_list, i+1, hopps = [-1,-2,-3,-4,-5,-6]
        )
        fk_tuples_after_modify = function_key_tuples_list[i+1][:]
        if not modified:
            rectified = rectify_ternery_transition(
                function_key_tuples_list[i], function_key_tuples_list[i+1]
            )
            if rectified:
                function_key_tuples_list[i], function_key_tuples_list[i+1] = rectified
                fk_tuples_after_modify = function_key_tuples_list[i+1][:]
        if verbose:
            print("at step", i, ", modify", fk_tuples_before_modify, " into ", fk_tuples_after_modify)
    return function_key_tuples_list

def rectify_key_list_with_repeatition_rewrite(function_key_tuples_list):
    def is_repeating(function_key_tuples):
        return len(function_key_tuples) == 1 and function_key_tuples[0] == (DIM_STAY, UNKNOWN_KEY)
    
    N_chord = len(function_key_tuples_list)
    for i in range(N_chord):
        if is_repeating(function_key_tuples_list[i]) and i < N_chord - 1:
            id_next_no_rep = i
            for j in range(i + 1, N_chord):
                if not is_repeating(function_key_tuples_list[j]):
                    id_next_no_rep = j
                    break
            
            function_key_tuples_list[i] = []
            for function_key_tuple in function_key_tuples_list[id_next_no_rep]:
                function_key_tuples_list[i].append((DIM_STAY, function_key_tuple[1]))
    return function_key_tuples_list
    
def align_chord_with_detected_keys(function_key_tuples_list, root_list, symb_list):    
    N_chord = len(function_key_tuples_list)
    assert N_chord == len(root_list), "Input length should be the same"
    assert N_chord == len(symb_list), "Input length should be the same"
    # process unrecognized and ambiguous chord: raw
    for i in range(N_chord):
        function_key_tuples = function_key_tuples_list[i]
        if len(function_key_tuples) == 0 or len(function_key_tuples) >= 2:
            modified, function_key_tuples_list, resulting_hop = visit_nearby_deterministic_key(
                function_key_tuples_list, root_list, symb_list, i, hopps = [-1,-2,-3,-4,-5,-6]
            )
    # process unrecognized and ambiguous chord (in reversed order)
    for i in reversed(range(N_chord - 1)):
        function_key_tuples = function_key_tuples_list[i]
        if len(function_key_tuples) != 1 or (len(function_key_tuples) == 1 and function_key_tuples[0]==(DIM_OTHER_BINARY_FUNCS,UNKNOWN_KEY)):
            modified, function_key_tuples_list, resulting_hop = visit_nearby_deterministic_key(
                function_key_tuples_list, root_list, symb_list, i, hopps = [j+1 for j in range(N_chord - i)] + [-1]
            )
    # process unrecognized and ambiguous chord (in normal order)
    for i in range(N_chord - 1):
        function_key_tuples = function_key_tuples_list[i]
        if len(function_key_tuples) != 1 or (len(function_key_tuples) == 1 and function_key_tuples[0]==(DIM_OTHER_BINARY_FUNCS,UNKNOWN_KEY)):
            modified, function_key_tuples_list, resulting_hop = visit_nearby_deterministic_key(
                function_key_tuples_list, root_list, symb_list, i,hopps = [-j-1 for j in range(i)] + [1]
            )
            
    # process still unrecognized chords, but sandwiched by recognized chords
    for i in range(N_chord):
        function_key_tuples = function_key_tuples_list[i]
        if len(function_key_tuples) == 0:
            modified, function_key_tuples_list = rectify_sandwiched_chord(
                function_key_tuples_list, root_list, symb_list, i
            )
    # modify the last chord function-key for completeness
    if N_chord > 1 and len(function_key_tuples_list[-2]) == 1:
        function_key_tuples_list[-1] = [(DIM_STAY, function_key_tuples_list[-2][0][1])]
    
    return function_key_tuples_list

'''
    Input: List[List[Tuple(FUNCTION, KEY)]]
    Output: List[Tuple(FUNCTION, KEY)]
'''
def prune_function_key_tuples_list(function_key_tuples_list):
    N_chord = len(function_key_tuples_list)
    function_key_list = [None] * N_chord
    for i in range(N_chord):
        function_key_tuples = function_key_tuples_list[i]
        if len(function_key_tuples) == 0:
            function_key_list[i] = (DIM_OTHER_BINARY_FUNCS, UNKNOWN_KEY)
        elif len(function_key_tuples) == 1:
            function_key_list[i] = function_key_tuples[0]
        else: # for fussy resuls, we have to sacrifise a little
            function_key_list[i] = function_key_tuples[0]
            
    for i in range(N_chord - 1):
        function_key_tuples = function_key_tuples_list[i]
        if len(function_key_tuples) == 0:
            function_key_list[i] = (DIM_OTHER_BINARY_FUNCS, UNKNOWN_KEY)
        elif len(function_key_tuples) == 1:
            function_key_list[i] = function_key_tuples[0]
        else: # for fussy resuls, we have to sacrifise a little
            function_key_list[i] = function_key_tuples[0]
    return function_key_list


def find_key_given_chord_track(chords):
    root_list, symb_list, bass_list = get_root_symb_bass_from_progression(chords)
    function_key_tuples_list = get_binary_progression_key_guesses(root_list, symb_list)
    function_key_tuples_list = rectify_key_list_with_quaternery_transitions(function_key_tuples_list)
    function_key_tuples_list = rectify_key_list_with_ternery_transitions(function_key_tuples_list, root_list, symb_list)
    function_key_tuples_list = rectify_key_list_with_repeatition_rewrite(function_key_tuples_list)
    function_key_tuples_list =  align_chord_with_detected_keys(function_key_tuples_list, root_list, symb_list)
    return prune_function_key_tuples_list(function_key_tuples_list)


def function_key_tuples_to_string_tuples(function_key_tuples, root_list, symb_list):
    binary_function_list, keys = tuple(zip(*function_key_tuples))
    unary_function_list = binary_functions_to_unary_functions(binary_function_list)
    for i in range(len(unary_function_list)):
        if unary_function_list[i] == DIM_OTHER_FUNCS:
            function = is_in_key_as_given(keys[i], root_list[i], symb_list[i])
            if function:
                unary_function_list[i] = function
    
    unary_function_string_list = [UNARY_FUNCTION_STRING_DICT[func] for func in unary_function_list]
    key_string_list = [KEY_INTEGER_TO_STRING[key] for key in keys]
    return list(zip(unary_function_string_list, key_string_list))