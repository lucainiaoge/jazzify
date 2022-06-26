'''
    Given triads, extend them into high-level chords and give the corresponding rootless voicing suggestions
'''
from rules.intervals import *
from rules.chord_symbols import *
from rules.chord2symbol import *
from rules.find_key import *


'''
    (key_root_to_chord_root_interval, is_major_key?): ([base_chord_types], [extended_chord_types])
'''
DIM_TONIC = 1
DIM_SUBDOMINANT = 2
DIM_DOMINANT = 3
DIM_DOUBLE_DOMINANT = 4
DIM_OTHER_FUNCS = 5


MAJOR_CHORD_EXTEND_RULES = {
    (0,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[MAJOR_69, MAJOR_9, MAJOR_7]),
    (INT_M2,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[DOM_13, DOM_7]),
    (INT_M2,False): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[DOM_13, DOM_7]),
    (INT_m3,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[ALT]),
    (INT_m3,False): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[MAJOR_69, MAJOR_9, MAJOR_7]),
    (INT_M3,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[ALT]),
    (INT_M3,False): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[DOM_7]),
    (INT_4,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[MAJOR_9, MAJOR_a11]),
    (INT_4,False): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[DOM_13, DOM_7]),
    (INT_a4,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[DOM_13]), # not sure
    (INT_a4,False): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[DOM_13]), # not sure
    (INT_5,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[DOM_13, DOM_7]),
    (INT_5,False): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[ALT]),
    (INT_m6,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[MAJOR_9]),
    (INT_m6,False): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[DOM_13, DOM_7]),
    (INT_M6,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[ALT]),
    (INT_M6,False): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[ALT]),
    (INT_m7,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[MAJOR_9]),
    (INT_m7,False): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[DOM_13, DOM_7]),
    (INT_M7,True): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[MAJOR_9]),
    (INT_M7,False): ([MAJOR,MAJOR_2,MAJOR_6,MAJOR_7],[MAJOR_7]), #or remain as it is
}
MINOR_CHORD_EXTEND_RULES = {
    (0,False): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_M7,MINOR_7],[MINOR_69, MINOR_9_M7]),
    (INT_m2,True): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_M7]),
    (INT_M2,True): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_9]),
    (INT_M2,False): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_9]),
    (INT_m3,True): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_M7]),
    (INT_m3,False): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_M7]),
    (INT_M3,True): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_9]),
    (INT_M3,False): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_M7]),
    (INT_4,True): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_9_M7]),
    (INT_4,False): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_9]),
    (INT_5,True): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_9]),
    (INT_5,False): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_9]),
    (INT_m6,True): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_M7]),
    (INT_m6,False): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_69, MINOR_9_M7, MINOR_M7]),
    (INT_M6,True): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_9]),
    (INT_M6,False): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_M7]),
    (INT_m7,True): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_9]),
    (INT_m7,False): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_9]),
    (INT_M7,True): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_M7]),
    (INT_M7,False): ([MINOR,MAJOR_2,MINOR_4,MINOR_6,MINOR_7],[MINOR_M7]),
}
DOM_CHORD_EXTEND_RULES = {
    (0,True): ([DOM_7,DOM_9,DOM_11],[DOM_13]),
    (0,False): ([DOM_7,DOM_9,DOM_11],[DOM_13]),
    (INT_m2,True): ([DOM_7,DOM_7_a5],[ALT]),
    (INT_m2,False): ([DOM_7,DOM_7_a5],[ALT]),
    (INT_M2,True): ([DOM_7,DOM_9,DOM_11],[DOM_13]),
    (INT_M2,False): ([DOM_7],[DOM_7b9]),
    (INT_m3,False): ([DOM_7,DOM_9,DOM_11],[DOM_13]),
    (INT_M3,True): ([DOM_7,DOM_7_a5],[ALT]),
    (INT_4,True): ([DOM_7,DOM_9,DOM_11],[DOM_13]),
    (INT_4,False): ([DOM_7,DOM_7_a5],[ALT]),
    (INT_5,True): ([DOM_7,DOM_9,DOM_11],[DOM_13]),
    (INT_5,False): ([DOM_7,DOM_7_a5],[ALT, DOM_7b9]),
    (INT_M6,True): ([DOM_7,DOM_7_a5],[ALT]),
    (INT_M6,False): ([DOM_7,DOM_7_a5],[ALT]),
    (INT_m7,True): ([DOM_7,DOM_9,DOM_11],[DOM_13]),
    (INT_m7,False): ([DOM_7,DOM_9,DOM_11],[DOM_13]),
    (INT_M7,True): ([DOM_7,DOM_7_a5],[ALT]),
    (INT_M7,False): ([DOM_7,DOM_7_a5],[ALT]),
}
SUS_CHORD_EXTEND_RULES = {
    (INT_m2,True): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_m2,False): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_M2,True): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_M2,False): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_m3,True): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_m3,False): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_M3,True): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_M3,False): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_4,True): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_4,False): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_5,True): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_5,False): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_m6,True): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_m6,False): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_M6,True): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_M6,False): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_m7,True): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_m7,False): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_M7,True): ([SUS,SUS_2,SUS_7],[SUS_13]),
    (INT_M7,False): ([SUS,SUS_2,SUS_7],[SUS_13]),
}
AUG_CHORD_EXTEND_RULES = {
    (0,True): ([AUG],[AUG_M7]),
    (0,False): ([AUG],[DOM_7_a5]),
    (INT_m2,True): ([AUG],[ALT]),
    (INT_m2,False): ([AUG],[ALT]),
    (INT_M2,True): ([AUG],[ALT]),
    (INT_M2,False): ([AUG],[ALT]),
    (INT_m3,True): ([AUG],[AUG_M7]),
    (INT_m3,False): ([AUG],[AUG_M7]),
    (INT_M3,True): ([AUG],[ALT]),
    (INT_M3,False): ([AUG],[ALT]),
    (INT_4,True): ([AUG],[ALT]),
    (INT_4,False): ([AUG],[ALT]),
    (INT_5,True): ([AUG],[ALT]),
    (INT_5,False): ([AUG],[ALT]),
    (INT_m6,True): ([AUG],[AUG_M7]),
    (INT_m6,False): ([AUG],[AUG_M7]),
    (INT_M6,True): ([AUG],[ALT]),
    (INT_M6,False): ([AUG],[ALT]),
    (INT_M7,True): ([AUG],[ALT]),
    (INT_M7,False): ([AUG],[ALT]),
}
DIM_CHORD_EXTEND_RULES = {
    (0,True): ([DIM],[HALFDIM_7,HALFDIM_9]),
    (0,False): ([DIM],[HALFDIM_7,HALFDIM_9]),
    (INT_m2,True): ([DIM],[DIM_7]),
    (INT_m2,False): ([DIM],[DIM_7]),
    (INT_M2,True): ([DIM],[DIM_7]),
    (INT_M2,False): ([HALFDIM_7,DIM],[HALFDIM_11, HALFDIM_9]),
    (INT_m3,True): ([DIM],[DIM_7]),
    (INT_m3,False): ([DIM],[DIM_7]),
    (INT_M3,True): ([DIM],[DIM_7]),
    (INT_M3,False): ([DIM],[DIM_7]),
    (INT_4,True): ([DIM],[DIM_7]),
    (INT_4,False): ([DIM],[DIM_7]),
    (INT_5,True): ([DIM],[DIM_7]),
    (INT_5,False): ([DIM],[DIM_7]),
    (INT_m6,True): ([DIM],[DIM_7]),
    (INT_m6,False): ([DIM],[DIM_7]),
    (INT_M6,True): ([DIM],[DIM_7]),
    (INT_M6,False): ([DIM],[DIM_7]),
    (INT_m7,True): ([DIM],[DIM_7]),
    (INT_m7,False): ([DIM],[DIM_7]),
    (INT_M7,True): ([DIM],[HALFDIM_7,HALFDIM_9]),
    (INT_M7,False): ([DIM],[HALFDIM_7,HALFDIM_9]),
}

EXTEND_CHORD_RULES = [
    MAJOR_CHORD_EXTEND_RULES,
    MINOR_CHORD_EXTEND_RULES,
    DOM_CHORD_EXTEND_RULES,
    SUS_CHORD_EXTEND_RULES,
    AUG_CHORD_EXTEND_RULES,
    DIM_CHORD_EXTEND_RULES,
]



def extend_chord(chord_type, chord_root, key):
    if type(key) == int:
        key_root = key % 12
        is_major = (key >= 0)
        key_root_to_chord_root = (chord_root - key_root)%12
        for chord_type_ext_rules in EXTEND_CHORD_RULES:
            if (key_root_to_chord_root, is_major) in chord_type_ext_rules:
                basic_chords, extended_chords = chord_type_ext_rules[(key_root_to_chord_root, is_major)]
                if chord_type in basic_chords:
                    return extended_chords
    return [chord_type]
