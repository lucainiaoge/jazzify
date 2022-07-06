import os
import sys
import argparse
import numpy as np

from data.data_utils import note_chord_to_midi, note_chord_to_json
from data import NottinghamDataset
from jazzify import Swingifier, Bossaifier

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir', type=str, default="data/nottingham_swingified/")
    parser.add_argument('style', type=str, default="swing")
    args = parser.parse_args()
    out_dir = args.out_dir
    style = args.style

    dataset = NottinghamDataset(aug=False)
    dataset_length = dataset.__len__()
    g_data_perm = np.arange(dataset_length)
    g_data_counter = 0
    while g_data_counter < dataset_length:
        piece = dataset.__getitem__(g_data_perm[g_data_counter])
        name = piece.name[:-5] + "_" + piece.title

        if "swing" in style:
            note_chord_to_midi(
                piece.notes, piece.chords, piece.time_signatures, out_path=os.path.join(out_dir, name+".mid"), resolution=24
            )
            swingifier = Swingifier(piece, bass_max = 52, bass_min = 24, voicing_min = 38, voicing_max = 64, p_remove_note = 0.1, max_voicing_jump = 6, verbose = False)
            swingifier.output_swingified_result(out_dir)
        elif "bossa" in style:
            if piece.time_signatures[0].numerator == 4 and piece.time_signatures[0].denominator == 4:
                note_chord_to_midi(
                    piece.notes, piece.chords, piece.time_signatures, out_path=os.path.join(out_dir, name+".mid"), resolution=24
                )
                bossaifier = Bossaifier(piece, bass_max = 52, bass_min = 24, voicing_min = 38, voicing_max = 64, p_remove_note = 0.1, max_voicing_jump = 6, verbose = False)
                bossaifier.output_bossaified_result(out_dir)
        g_data_counter += 1
