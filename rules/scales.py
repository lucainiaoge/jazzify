from rules.pitch_names import PITCH_NAME_2_NUM, PITCH_NUM_2_NAME

SCALE_INTERVALS = {
    # Major modes
    "Ionian":         [2,2,1,2,2,2,1],
    "Dorian":         [2,1,2,2,2,1,2],
    "Phrigian":       [1,2,2,2,1,2,2],
    "Phrigian#3":     [1,3,1,2,1,2,2],
    "Lydian":         [2,2,2,1,2,2,1],
    "Mixolydian":     [2,2,1,2,2,1,2],
    "Aeolian":        [2,1,2,2,1,2,2],
    "Locrian":        [1,2,2,1,2,2,2],
    # Melodic minor modes
    "melodic_minor":  [2,1,2,2,2,2,1],
    "Phrigidorian":   [1,2,2,2,2,1,2],
    "Lydian_aug":     [2,2,2,2,1,2,1],
    "Lydian_dom":     [2,2,2,1,2,1,2],
    "melodic_major":  [2,2,1,2,1,2,2],
    "half_dim":       [2,1,2,1,2,2,2],
    "alt":            [1,2,1,2,2,2,2],
    # Harmonic minor scale
    "harmonic_minor": [2,1,2,2,1,3,1],
    # Pentatonic modes
    "pent_major":     [2,2,3,2,3],
    "pent_minor":     [3,2,2,3,2],
    # Blues scales
    "blues_major":    [2,1,1,3,2,3],
    "blues_minor":    [3,2,1,1,3,2],
    # Diminished scales:
    "dim_1":          [1,2,1,2,1,2,1,2],
    "dim_2":          [2,1,2,1,2,1,2,1],
    # Whole tone scale:
    "whole_tone":     [2,2,2,2,2,2],
    # Chromatic scale:
    "chromatic":      [1,1,1,1,1,1,1,1,1,1,1,1]
}

def get_scale_pitches(root_note, scale_name):
    scale_multihot = [0]*12
    scale_pitch_nums = []
    if type(root_note) == int:
        this_id = root_note % 12
    elif type(root_note) == str:
        this_id = PITCH_NAME_2_NUM[root_note]
    else:
        raise TypeError("Incorrect format of scale root note.")
    
    scale_pitch_nums.append(this_id)
    intervals = SCALE_INTERVALS[scale_name]
    for step in intervals:
        this_id = this_id + step
        if this_id >= 12:
            this_id = this_id - 12
        scale_multihot[this_id] = 1
        if this_id not in scale_pitch_nums:
            scale_pitch_nums.append(this_id)
    return scale_multihot, scale_pitch_nums