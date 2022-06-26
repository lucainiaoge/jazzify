PITCH_NAME_2_NUM = {
    'C': 0, 'B#': 0,
    'C#': 1, 'Db': 1,
    'D': 2,
    'D#': 3, 'Eb': 3,
    'E': 4, 'Fb': 4,
    'F': 5, 'E#': 5,
    'F#': 6, 'Gb': 6,
    'G': 7,
    'G#': 8, 'Ab': 8,
    'A': 9,
    'A#': 10, 'Bb': 10,
    'B': 11, 'Cb': 11
}

PITCH_NUM_2_NAME = {
    0: 'C',
    1: 'Db',
    2: 'D',
    3: 'Eb',
    4: 'E',
    5: 'F',
    6: 'Gb',
    7: 'G',
    8: 'Ab',
    9: 'A',
    10: 'Bb',
    11: 'B',
}

'''
    e.g., input "C4", output ("C",5*12)
    e.g., input "Eb", output ("Eb",5*12)
'''
def parse_pitch_name_with_octave(pitch_name_with_octave, default_bias = 48):
    
    number = ""
    sep = 0
    for char in pitch_name_with_octave:
        if char.isdigit():
            break
        sep += 1
    name = pitch_name_with_octave[:sep]
    if sep == len(pitch_name_with_octave):
        bias = default_bias
    else:
        bias = (int(pitch_name_with_octave[sep:]) + 1) * 12
    return name, bias

'''
    e.g., input ["C4","G4","E4"], ordered = False, output (5*12, 5*12+4, 5*12+7)
    e.g., input ["C","G","E"], ordered = True, output (48+0, 48+7, 48+16)
'''
def list_pitch_name_to_num(list_pitch_name, default_bias = 48, ordered = False):
    list_pitch_num = []
    
    previous_num = default_bias
    for pitch_name in list_pitch_name:
        name, bias = parse_pitch_name_with_octave(pitch_name, default_bias)
        num = PITCH_NAME_2_NUM[name]
        if not ordered:
            list_pitch_num.append(num + bias)
        else:
            this_num = num + default_bias
            while this_num < previous_num:
                this_num += 12
            list_pitch_num.append(this_num)
            previous_num = this_num
    list_pitch_num.sort()
    return list_pitch_num # sort in ascending order
            
            
            
    