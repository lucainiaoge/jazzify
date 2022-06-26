from rules.intervals import *

'''
    extension markers
''' 
EXT_INT = "-interval"
EXT_2ND = "-second"
EXT_4TH = "-fourth"
EXT_6TH = "-sixth"
EXT_7TH = "-seventh"
EXT_MAJ = "-major"
EXT_DOM = "-dominant"
EXT_M7TH = "-major-seventh"
EXT_9TH = "-ninth"
EXT_M9TH = "-major-ninth"
EXT_11TH = "-11th"
EXT_M11TH = "-major-11th"
EXT_13TH = "-13th"
EXT_m13TH = "-minor-13th"
EXT_M13TH = "-major-13th"

EXT_2 = "-2"
EXT_4 = "-4"
EXT_a4 = "-#4"
EXT_b9 = "-b9"
EXT_11 = "-11"
EXT_a11 = "-#11"
EXT_a5 = "-#5"
EXT_b5 = "-b5"
EXT_b13 = "-b13"

INT2NAME = {
    0: "unison-interval",
    INT_m2: "minor-second-interval",
    INT_M2: "major-second-interval",
    INT_m3: "minor-third-interval",
    INT_M3: "major-third-interval",
    INT_4: "fourth-interval",
    INT_a4: "tritone-interval",
    INT_5: "fifth-interval",
    INT_a5: "augmented-fifth-interval",
    INT_M6: "sixth-interval",
    INT_m7: "minor-seventh-interval",
    INT_M7: "major-seventh-interval",
    INT_8: "octave-interval",
    INT_m9: "minor-ninth-interval",
    INT_M9: "major-ninth-interval",
    INT_m10: "minor-third-interval",
    INT_M10: "major-third-interval",
    INT_11: "fourth-interval",
    INT_a11: "tritone-interval",
    INT_12: "fifth-interval",
    INT_m13: "augmented-fifth-interval",
    INT_M13: "sixth-interval",
    INT_m14: "minor-seventh-interval",
    INT_M14: "major-seventh-interval"
}
INT2EXT = {
    INT_m2: "-b2",
    INT_M2: "-2",
    # no thirds
    INT_4: "-4",
    INT_a4: "-#4",
    # no fifth
    INT_a5: "-#5",
    INT_M6: "-6",
    # no seventh
    INT_m9: "-b9",
    INT_M9: "-9",
    INT_a9: "-#9",
    # no 10th
    INT_11: "-11",
    INT_a11: "-#11",
    # no 12th
    INT_m13: "-b13",
    INT_M13: "-13",
    # no 14th
}
INT2EXT_MAJ = {
    INT_m2: "-b2",
    # already considered as major2 chord
    INT_m3: "-minor3",
    INT_4: "-4",
    INT_a4: "-b5",
    # no fifth
    INT_a5: "-#5",
    # no sixth, already considered as individual chord
    # no seventh
    INT_m9: "-b9",
    INT_M9: "-9",
    INT_a9: "-#9",
    # no 10th
    INT_11: "-11",
    INT_a11: "-#11",
    # no 12th
    INT_m13: "-b13",
    INT_M13: "-13",
    # no 14th
}
INT2EXT_MAJ_a4 = {
    INT_m2: "-b2",
    INT_M2: "-2",
    INT_m3: "-minor3",
    INT_4: "-4",
    # no fifth, it will be maj-#4
    # no #5, it will be aug-#4
    # no M-sixth, it will be half-dim
    # no seventh
    INT_m9: "-b9",
    INT_M9: "-9",
    INT_a9: "-#9",
    # no 10th
    INT_11: "-11",
    # no 12th, it will be maj-#4
    # no #12, it will be aug-#4
    # no M-13th, it will be half-dim
    # no 14th
}
INT2EXT_MIN = {
    INT_m2: "-b2",
    INT_M2: "-2",
    INT_M3: "-major3",
    INT_4: "-4",
    INT_a4: "-b5",
    # no fifth
    INT_a5: "-#5",
    # no sixth, already considered as individual chord
    # no seventh
    INT_m9: "-b9",
    INT_M9: "-9",
    INT_M10: "-major10",
    INT_11: "-11",
    INT_a11: "-#11",
    # no 12th
    INT_m13: "-b13",
    INT_M13: "-13",
    # no 14th
}
INT2EXT_MIN_4 = {
    INT_M2: "-2",
    INT_M3: "-major3",
    # no #4(b5), it will be dim-4
    # no fifth
    # no sixth
    INT_M7: "-major7",
    INT_m9: "-b9",
    INT_M9: "-9",
    INT_M10: "-major3",
    # no #11, it will be dim-4
    # no 12th
    # no 13th
    # no 14th
}
INT2EXT_DOM = {
    INT_m2: "-b2",
    INT_M2: "-9",
    INT_m3: "-#9",
    INT_4: "-11",
    INT_a4: "-#11",
    INT_a5: "-#5",
    INT_M6: "-13",
    INT_M7: "-major7",
    INT_m9: "-b9",
    INT_M9: "-9",
    INT_a9: "-#9",
    # no 10th
    INT_11: "-11",
    INT_a11: "-#11",
    INT_a12: "-b13",
    INT_M13: "-13",
    # no 14th
}
INT2EXT_DOM_a5 = {
    INT_m2: "-b2",
    INT_M2: "-9",
    INT_m3: "-#9",
    INT_4: "-11",
    INT_a4: "-#11",
    INT_M6: "-13",
    INT_M7: "-major7",
    INT_m9: "-b9",
    INT_M9: "-9",
    INT_a9: "-#9",
    # no 10th
    INT_11: "-11",
    INT_a11: "-#11",
    INT_M13: "-13",
    # no 14th
}
INT2EXT_DOM_b5 = {
    INT_m2: "-b2",
    INT_M2: "-9",
    INT_m3: "-#9",
    INT_4: "-11",
    INT_a5: "-#5",
    INT_M6: "-13",
    INT_M7: "-major7",
    INT_m9: "-b9",
    INT_M9: "-9",
    INT_a9: "-#9",
    # no 10th
    INT_11: "-11",
    INT_a12: "-b13",
    INT_M13: "-13",
    # no 14th
}
INT2EXT_SUS = {
    INT_m2: "-b2",
    # no 3th
    INT_a4: "-#11",
    INT_a5: "-#5",
    INT_M6: "-13",
    INT_M7: "-major7",
    INT_m9: "-b9",
    # no 10th
    INT_a11: "-#11",
    INT_a12: "-b13",
    INT_M13: "-13",
    # no 14th
}
INT2EXT_AUG = {
    # no b2, becuase it is inversion min-maj
    INT_M2: "-2",
    # no minor thirds, because is is inversion aug-maj
    INT_4: "-11",
    INT_a4: "-#11",
    INT_5: "-add5",
    INT_M6: "-13",
    # no seventh
    INT_m9: "-b9",
    INT_M9: "-9",
    INT_a9: "-#9",
    # no tenth
    INT_11: "-11",
    INT_a11: "-#11",
    INT_12: "-add5",
    INT_M13: "-13",
    # no 14th
}
INT2EXT_AUG_M7 = {
    # no b2, becuase it is inversion min-maj
    INT_M2: "-2",
    INT_a2: "-#9",
    INT_4: "-11",
    INT_a4: "-#11",
    INT_5: "-add5",
    INT_M6: "-13",
    # no seventh
    INT_m9: "-b9",
    INT_M9: "-9",
    INT_a9: "-#9",
    # no tenth
    INT_11: "-11",
    INT_a11: "-#11",
    INT_12: "-add5",
    INT_M13: "-13",
    # no 14th
}
INT2EXT_DIM = {
    INT_m2: "-b2",
    INT_M2: "-9",
    INT_M3: "-major3",
    INT_4: "-11",
    INT_5: "-add5",
    INT_a5: "-b13",
    # no sixth
    INT_M7: "-major7",
    INT_m9: "-b9",
    INT_M9: "-9",
    # 10th = 3th
    INT_11: "-11",
    INT_12: "-add5",
    INT_a12: "-b13",
    # no 13th
    # 14th = 7th
}
INT2EXT_DIM_M7 = {
    INT_m2: "-b2",
    INT_M2: "-9",
    INT_M3: "-major3",
    INT_4: "-11",
    INT_5: "-add5",
    INT_a5: "-b13",
    # no sixth
    # no seventh
    INT_m9: "-b9",
    INT_M9: "-9",
    # 10th = 3th
    INT_11: "-11",
    INT_12: "-add5",
    INT_a12: "-b13",
    # no 13th
    # 14th = 7th
}
INT2EXT_HALFDIM = {
    INT_m2: "-b2",
    INT_M2: "-9",
    INT_M3: "-major3",
    INT_4: "-11",
    INT_5: "-add5",
    INT_a5: "-b13",
    INT_M6: "-13",
    INT_M7: "-major7",
    INT_m9: "-b9",
    INT_M9: "-9",
    # 10th = 3th
    INT_11: "-11",
    INT_12: "-add5",
    INT_a12: "-b13",
    INT_M13:"-13"
    # 14th = 7th
}
INT2EXT_ALT = {
    INT_m2: "-b2",
    INT_M2: "-2",
    INT_4: "-11",
    INT_M6: "-13",
    # no seventh
    INT_M9: "-9",
    INT_11: "-11",
    INT_12: "-add5",
    INT_M13: "-13",
    # no 14th
}

INT2EXT_RULES_ALL = [
    INT2EXT_MAJ,
    INT2EXT_MAJ_a4,
    INT2EXT_MIN,
    INT2EXT_MIN_4,
    INT2EXT_DOM,
    INT2EXT_DOM_a5,
    INT2EXT_DOM_b5,
    INT2EXT_SUS,
    INT2EXT_AUG,
    INT2EXT_AUG_M7,
    INT2EXT_DIM,
    INT2EXT_DIM_M7,
    INT2EXT_HALFDIM,
    INT2EXT_ALT,
]

EXT2INT = {
    EXT_2: INT_M2,
    EXT_4: INT_4,
    EXT_a4: INT_a4,
    EXT_b9: INT_m9,
    EXT_11: INT_11,
    EXT_a11: INT_a11,
    EXT_a5: INT_a5,
    EXT_b5: INT_a4,
    EXT_b13: INT_m13,
}
POSSIBLE_EXTS = []
for int2ext_rules in INT2EXT_RULES_ALL:
    ext2int = {v: k for k, v in int2ext_rules.items()}
    for ext in ext2int:
        if ext not in EXT2INT:
            EXT2INT[ext] = ext2int[ext]
        if ext not in POSSIBLE_EXTS:
            POSSIBLE_EXTS.append(ext)

'''
    chord qualities
'''
UNK_CHORD = "unknown"
# Majors
MAJOR = "major"
MAJOR_INT = MAJOR + EXT_INT
MAJOR_2 = MAJOR + EXT_2
MAJOR_4 = MAJOR + EXT_4
MAJOR_b5 = MAJOR + EXT_b5
MAJOR_a5 = MAJOR + EXT_a5
MAJOR_a4 = MAJOR + EXT_a4
MAJOR_6 = MAJOR + EXT_6TH
MAJOR_7 = MAJOR + EXT_7TH
MAJOR_9 = MAJOR + EXT_9TH
MAJOR_67 = MAJOR + EXT_6TH + EXT_7TH
MAJOR_69 = MAJOR + EXT_6TH + EXT_9TH
MAJOR_6_11 = MAJOR + EXT_6TH + EXT_11TH
MAJOR_6_a11 = MAJOR + EXT_6TH + EXT_a11
MAJOR_11 = MAJOR + EXT_11TH
MAJOR_a11 = MAJOR + EXT_7TH + EXT_a11
MAJOR_13 = MAJOR + EXT_13TH
MAJOR_13_a11 = MAJOR + EXT_13TH + EXT_a11
# Minors
MINOR = "minor"
MINOR_INT = MINOR + EXT_INT
MINOR_2 = MINOR + EXT_2
MINOR_4 = MINOR + EXT_4
MINOR_6 = MINOR + EXT_6TH
MINOR_7 = MINOR + EXT_7TH
MINOR_67 = MINOR + EXT_6TH + EXT_7TH
MINOR_9 = MINOR + EXT_9TH
MINOR_69 = MINOR + EXT_6TH + EXT_9TH
MINOR_6_11 = MINOR + EXT_6TH + EXT_11TH
MINOR_6_a11 = MINOR + EXT_6TH + EXT_a11
MINOR_11 = MINOR + EXT_11TH
MINOR_a11 = MINOR + EXT_a11
MINOR_13 = MINOR + EXT_13TH
MINOR_13_a11 = MINOR + EXT_13TH + EXT_a11
# Minor-majors
MINOR_M7 = MINOR + EXT_M7TH
MINOR_6_M7 = MINOR + EXT_6TH + EXT_M7TH
MINOR_69_M7 = MINOR + EXT_6TH + EXT_9TH + EXT_M7TH
MINOR_6_M11 = MINOR + EXT_6TH + EXT_11TH + EXT_M7TH
MINOR_6_M7_a11 = MINOR + EXT_6TH + EXT_M7TH + EXT_a11
MINOR_9_M7 = MINOR + EXT_9TH + EXT_M7TH
MINOR_11_M7 = MINOR + EXT_11TH + EXT_M7TH
MINOR_a11_M7 = MINOR + EXT_M7TH + EXT_a11
MINOR_13_M7 = MINOR + EXT_13TH + EXT_M7TH
MINOR_13_M7_a11 = MINOR + EXT_13TH + EXT_M7TH + EXT_a11
# Dominants
DOM = "dominant"
DOM_7 = DOM + EXT_7TH
DOM_7_a5 = DOM + EXT_7TH + EXT_a5
DOM_7_b5 = DOM + EXT_7TH + EXT_b5
DOM_9 = DOM + EXT_9TH
DOM_11 = DOM + EXT_11TH
DOM_13 = DOM + EXT_13TH
DOM_7b9 = DOM + EXT_7TH + EXT_b9
DOM_11b9 = DOM + EXT_11TH + EXT_b9
DOM_13b9 = DOM + EXT_13TH + EXT_b9
DOM_7_a11 = DOM + EXT_7TH + EXT_a11
DOM_13_a11 = DOM + EXT_13TH + EXT_a11

DOM_a5_9 = DOM + EXT_9TH + EXT_a5
DOM_a5_11 = DOM + EXT_11TH + EXT_a5
DOM_a5_13 = DOM + EXT_13TH + EXT_a5
DOM_a5_7b9 = DOM + EXT_7TH + EXT_a5 + EXT_b9
DOM_a5_11b9 = DOM + EXT_11TH + EXT_a5 + EXT_b9
DOM_a5_13b9 = DOM + EXT_13TH + EXT_a5 + EXT_b9
DOM_a5_7_a11 = DOM + EXT_7TH + EXT_a11
DOM_a5_13_a11 = DOM + EXT_13TH + EXT_a5 + EXT_a11

DOM_b5_9 = DOM + EXT_9TH + EXT_a5
DOM_b5_11 = DOM + EXT_11TH + EXT_a5
DOM_b5_13 = DOM + EXT_13TH + EXT_a5
DOM_b5_7b9 = DOM + EXT_7TH + EXT_a5 + EXT_b9
DOM_b5_11b9 = DOM + EXT_11TH + EXT_a5 + EXT_b9
DOM_b5_13b9 = DOM + EXT_13TH + EXT_a5 + EXT_b9

# Sus
SUS = "suspended"
SUS_2 = SUS + EXT_2ND
SUS_7 = SUS + EXT_7TH
SUS_M7 = SUS + EXT_M7TH
SUS_13 = SUS + EXT_13TH
SUS_M13 = SUS + EXT_MAJ + EXT_13TH
# Augmented
AUG = "augmented"
AUG_M7 = AUG + EXT_M7TH
AUG_M7_M9 = AUG + EXT_MAJ + EXT_9TH
AUG_M7_M11 = AUG + EXT_MAJ + EXT_11TH
AUG_M7_a11 = AUG + EXT_MAJ + EXT_a11
AUG_M7_M13 = AUG + EXT_MAJ + EXT_13TH
AUG_M7_M13_a11 = AUG + EXT_MAJ + EXT_13TH + EXT_a11
# Diminished
DIM = "diminished"
DIM_7 = DIM + EXT_7TH
DIM_M7 = DIM + EXT_M7TH
DIM_9 = DIM + EXT_9TH
DIM_M9 = DIM + EXT_MAJ + EXT_9TH
# Half-diminished
HALFDIM = "half-diminished"
HALFDIM_7 = HALFDIM + EXT_7TH
HALFDIM_9 = HALFDIM + EXT_9TH
HALFDIM_11 = HALFDIM + EXT_11TH
HALFDIM_b13 = HALFDIM + EXT_b13
# Altered
ALT = "alt"

# Half-dim rootless voicing grip inversions
# ROOTLESS_GRIP_1 = "rootless-type1"
# PHRIGIAN = "phrigian"
# ROOTLESS_GRIP_2 = "rootless-type2"

# voicings
CHORD_2_VOICING = {
    MAJOR: [INT_M3,INT_5,INT_8],
    MAJOR_INT: [INT_M3,INT_8,INT_M10],
    MAJOR_2: [INT_M2,INT_M3,INT_5],
    MAJOR_4: [INT_M3,INT_4,INT_5,INT_8],
    MAJOR_b5: [INT_M3,INT_a4,INT_8],
    MAJOR_a5: [INT_M3,INT_5,INT_a5,INT_8],
    MAJOR_a4: [INT_M3,INT_a4,INT_5,INT_8],
    MAJOR_6: [INT_M3,INT_5,INT_M6,INT_8],
    MAJOR_7: [INT_M3,INT_5,INT_M7,INT_8],
    MAJOR_9: [INT_M3,INT_5,INT_M7,INT_M9],
    MAJOR_67: [INT_M3,INT_5,INT_M6,INT_M7],
    MAJOR_69: [INT_M3,INT_5,INT_M6,INT_M9],
    MAJOR_6_11: [INT_M3,INT_5,INT_M6,INT_M9,INT_11],
    MAJOR_6_a11: [INT_M3,INT_5,INT_M6,INT_M9,INT_a11],
    MAJOR_11: [INT_M3,INT_5,INT_M7,INT_M9,INT_11],
    MAJOR_a11: [INT_M3,INT_5,INT_M7,INT_M9,INT_a11],
    MAJOR_13: [INT_M3,INT_5,INT_M7,INT_M9,INT_11,INT_M13],
    MAJOR_13_a11: [INT_M3,INT_5,INT_M7,INT_M9,INT_a11,INT_M13],
    
    MINOR: [INT_m3,INT_5,INT_8],
    MINOR_INT: [INT_m3,INT_8,INT_m10],
    MINOR_2: [INT_M2,INT_m3,INT_5],
    MINOR_4: [INT_m3,INT_4,INT_5,INT_8],
    MINOR_6: [INT_m3,INT_5,INT_M6,INT_8],
    MINOR_7: [INT_m3,INT_5,INT_m7,INT_8],
    MINOR_67: [INT_m3,INT_5,INT_M6,INT_m7],
    MINOR_9: [INT_m3,INT_5,INT_m7,INT_M9],
    MINOR_69: [INT_m3,INT_5,INT_M6,INT_M9],
    MINOR_6_11: [INT_m3,INT_5,INT_M6,INT_M9,INT_11],
    MINOR_6_a11: [INT_m3,INT_5,INT_M6,INT_M9,INT_a11],
    MINOR_11: [INT_m3,INT_5,INT_m7,INT_M9,INT_11],
    MINOR_a11: [INT_m3,INT_5,INT_m7,INT_M9,INT_a11],
    MINOR_13: [INT_m3,INT_5,INT_m7,INT_M9,INT_11,INT_M13],
    MINOR_13_a11: [INT_m3,INT_5,INT_m7,INT_M9,INT_a11,INT_M13],

    MINOR_M7: [INT_m3,INT_5,INT_M7],
    MINOR_6_M7: [INT_m3,INT_5,INT_M6,INT_M7],
    MINOR_69_M7: [INT_m3,INT_5,INT_M6,INT_M7,INT_M9],
    MINOR_6_M11: [INT_m3,INT_5,INT_M6,INT_M7,INT_11],
    MINOR_6_M7_a11: [INT_m3,INT_5,INT_M6,INT_M7,INT_a11],
    MINOR_9_M7: [INT_m3,INT_5,INT_M7,INT_M9],
    MINOR_11_M7: [INT_m3,INT_5,INT_M7,INT_M9,INT_11],
    MINOR_a11_M7: [INT_m3,INT_5,INT_M7,INT_M9,INT_a11],
    MINOR_13_M7: [INT_m3,INT_5,INT_M6,INT_M7,INT_M9,INT_11],
    MINOR_13_M7_a11: [INT_m3,INT_5,INT_M6,INT_M7,INT_M9,INT_a11],
    
    DOM_7: [INT_M3,INT_5,INT_m7,INT_8],
    DOM_7_a5: [INT_M3,INT_a5,INT_m7,INT_8],
    DOM_7_b5: [INT_M3,INT_a4,INT_m7,INT_8],
    DOM_9: [INT_M3,INT_5,INT_m7,INT_M9],
    DOM_11: [INT_5,INT_m7,INT_M9,INT_M10],
    DOM_13: [INT_M3,INT_M6,INT_m7,INT_M9],
    DOM_7b9: [INT_M3,INT_5,INT_m7,INT_m9],
    DOM_11b9: [INT_M3,INT_5,INT_m7,INT_m9,INT_11],
    DOM_13b9: [INT_M3,INT_M6,INT_m7,INT_m9],
    DOM_7_a11: [INT_M3,INT_m7,INT_M9,INT_a11],
    DOM_13_a11: [INT_M3,INT_M6,INT_m7,INT_M9,INT_a11],

    DOM_a5_9: [INT_M3,INT_a5,INT_m7,INT_M9],
    DOM_a5_11: [INT_M3,INT_a5,INT_m7,INT_M9,INT_11],
    DOM_a5_13: [INT_M3,INT_a5,INT_m7,INT_M9,INT_M13],
    DOM_a5_7b9: [INT_M3,INT_a5,INT_m7,INT_m9],
    DOM_a5_11b9: [INT_M3,INT_a5,INT_m7,INT_m9,INT_11],
    DOM_a5_13b9: [INT_M3,INT_a5,INT_m7,INT_m9,INT_M13],
    DOM_a5_7_a11: [INT_M3,INT_a5,INT_m7,INT_M9,INT_a11],
    DOM_a5_13_a11: [INT_M3,INT_a5,INT_m7,INT_M9,INT_a11,INT_M13],

    DOM_b5_9: [INT_M3,INT_a4,INT_m7,INT_M9],
    DOM_b5_11: [INT_M3,INT_a4,INT_m7,INT_M9,INT_11],
    DOM_b5_13: [INT_M3,INT_a4,INT_m7,INT_M9,INT_M13],
    DOM_b5_7b9: [INT_M3,INT_a4,INT_m7,INT_m9],
    DOM_b5_11b9: [INT_M3,INT_a4,INT_m7,INT_m9,INT_11],
    DOM_b5_13b9: [INT_M3,INT_a4,INT_m7,INT_m9,INT_M13],
    
    SUS: [INT_M2,INT_4,INT_M6],
    SUS_2: [INT_M2,INT_5],
    SUS_7: [INT_4,INT_5,INT_m7,INT_M9],
    SUS_M7: [INT_4,INT_5,INT_M7,INT_M9],
    SUS_13: [INT_4,INT_M6,INT_m7,INT_M9],
    SUS_M13: [INT_4,INT_M6,INT_M7,INT_M9],
    
    AUG: [INT_M3,INT_a5,INT_8],
    AUG_M7: [INT_M3,INT_a5,INT_M7],
    AUG_M7_M9: [INT_M3,INT_a5,INT_M7,INT_M9],
    AUG_M7_M11: [INT_M3,INT_a5,INT_M7,INT_M9,INT_11],
    AUG_M7_a11: [INT_M3,INT_a5,INT_M7,INT_M9,INT_a11],
    AUG_M7_M13: [INT_M3,INT_a5,INT_M6,INT_M7,INT_M9],
    AUG_M7_M13_a11: [INT_M3,INT_a5,INT_M6,INT_M7,INT_M9,INT_a11],
    
    DIM: [INT_m3,INT_a4,INT_8],
    DIM_7: [INT_m3,INT_a4,INT_M6,INT_8],
    DIM_M7: [INT_m3,INT_a4,INT_M7],
    DIM_9: [INT_m3,INT_a4,INT_M6,INT_M9],
    DIM_M9: [INT_m3,INT_a4,INT_M7,INT_M9],
    
    HALFDIM_7: [INT_m3,INT_a4,INT_m7],
    HALFDIM_9: [INT_m3,INT_a4,INT_m7,INT_M9],
    HALFDIM_11: [INT_a4,INT_m7,INT_8,INT_11],
    HALFDIM_b13: [INT_a4,INT_m7,INT_M9,INT_11,INT_m13],
    
    ALT: [INT_M3,INT_a5,INT_m7,INT_m10],
    
    INT2NAME[0]: [INT_8],
    INT2NAME[INT_m2]: [INT_m9],
    INT2NAME[INT_M2]: [INT_M9],
    INT2NAME[INT_m3]: [INT_m3],
    INT2NAME[INT_M3]: [INT_M3],
    INT2NAME[INT_4]: [INT_4],
    INT2NAME[INT_a4]: [INT_a4],
    INT2NAME[INT_5]: [INT_5],
    INT2NAME[INT_a5]: [INT_a5],
    INT2NAME[INT_M6]: [INT_M6],
    INT2NAME[INT_m7]: [INT_m7],
    INT2NAME[INT_M7]: [INT_M7],
    INT2NAME[INT_8]: [INT_8],
    INT2NAME[INT_m9]: [INT_m9],
    INT2NAME[INT_M9]: [INT_M9],
    INT2NAME[INT_m10]: [INT_m10],
    INT2NAME[INT_M10]: [INT_M10],
    INT2NAME[INT_11]: [INT_11],
    INT2NAME[INT_a11]: [INT_a11],
    INT2NAME[INT_12]: [INT_12],
    INT2NAME[INT_m13]: [INT_m13],
    INT2NAME[INT_M13]: [INT_M13],
    INT2NAME[INT_m14]: [INT_m14],
    INT2NAME[INT_M14]: [INT_M14],
}


