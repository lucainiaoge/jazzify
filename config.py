import numpy as np

class Config:
    def __init__(self):
        # path
        self.dataset_path = "data/nottingham/_converted"
        self.dataset_debug_path = "data/nottingham/debug"
        # data
        self.max_input_length = 76
        self.max_output_length = 453
        # pitch
        self.pitch_min = 49  # 55-6
        self.pitch_max = 93  # 88+5
        self.pitch_num = self.pitch_max - self.pitch_min + 1 + 1  # both ends and rest note
        self.possible_pitches = [-1] + [p for p in range(self.pitch_min, self.pitch_max+1)]
        # duration
        self.possible_durations = [3,4,6,
            8,9,
            12,16,18,
            24,32,36,42,
            48,54,60,
            72,84,
            96,108,
            120,144,168,180,192,240,480,
        ]
        self.duration_2_id = {v: i for i, v in enumerate(self.possible_durations)}
        self.id_2_duration = {i: v for i, v in enumerate(self.possible_durations)}
        self.num_duration_types = len(self.id_2_duration)
        
        self.possible_durations_gen = [6,12,18,24,36,48]
        self.duration_2_id_gen = {v: i for i, v in enumerate(self.possible_durations_gen)}
        self.id_2_duration_gen = {i: v for i, v in enumerate(self.possible_durations_gen)}
        self.gen_dur_id_2_duration_id = {i: self.duration_2_id[self.id_2_duration_gen[i]] for i in self.id_2_duration_gen}
        self.num_duration_types_gen = len(self.id_2_duration_gen)
        
        # time signature
        self.filter_signature = True
        self.time_signatures_filtered = [(4, 4), (3, 4)]
        self.time_signatures_all = [
            (4, 4),
            (3, 4),
            (2, 4),
            (6, 8),
            (2, 2),
            (3, 8),
            (1, 8),
            (9, 8),
            (6, 4),
            (1, 4),
            (3, 2),
            (1, 16),
            (5, 4),
        ]
        if self.filter_signature:
            self.possible_time_signatures = self.time_signatures_filtered
        else:
            self.possible_time_signatures = self.time_signatures_all
        self.time_signature_2_id = {
            v: i for i, v in enumerate(self.possible_time_signatures)
        }
        self.id_2_time_signature = {
            i: v for i, v in enumerate(self.possible_time_signatures)
        }
        self.num_time_signature_types = len(self.possible_time_signatures)

        self.n_gram = 16

config = Config()
