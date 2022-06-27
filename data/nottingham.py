import os
import json
from pathlib import Path
import random
# from torch.utils.data import Dataset

from .data_utils import insert_rests, rectify_times, rectify_note_durs, rectify_chord_durs, get_max_time

from music_struct import Piece, Chord, Note, TimeSignature, Tempo
from config import config
from slugify import slugify


class NottinghamDataset: #(Dataset):
    def __init__(self, aug=False, logger=None, debug=False):
        ### the min interval of duration, assume is 12
        self.names = []
        self.aug = aug
        if not debug:
            self.root_path = Path(config.dataset_path)
        else:
            self.root_path = Path(config.dataset_debug_path)
        
        for name in os.listdir(self.root_path):
            if name.endswith(".json"):
                with open(str(self.root_path / name)) as f:
                    piece = json.load(f)
                    if "chords" not in piece["tracks"][0]:
                        continue
                    elif "notes" not in piece["tracks"][0]:
                        continue
                    elif len(piece["tracks"]) > 1:
                        continue
                    else:
                        is_frequent = True
                        if config.filter_signature:
                            for time_signature in piece["time_signatures"]:
                                numerator = time_signature["numerator"]
                                denominator = time_signature["denominator"]
                                time_signature = (numerator, denominator)
                                is_frequent_local = (
                                    time_signature in config.possible_time_signatures
                                )
                                is_frequent = is_frequent and is_frequent_local
                        if not is_frequent:
                            continue
                        else:
                            self.names.append(name)
        if logger is None:
            print(f"finished loading dataset, total number: {len(self.names)}")
        else:
            logger.info(f"finished loading dataset, total number: {len(self.names)}")

    def __len__(self):
        return len(self.names)

    def __getitem__(self, idx) -> Piece:
        name = self.names[idx]
        with open(str(self.root_path / name)) as f:
            piece = json.load(f)
        piece["tracks"][0]["notes"] = rectify_note_durs(piece["tracks"][0]["notes"])
        piece["tracks"][0]["notes"] = rectify_times(piece["tracks"][0]["notes"])
        piece["tracks"][0]["chords"] = rectify_times(piece["tracks"][0]["chords"])
        piece["tracks"][0]["notes"] = insert_rests(piece["tracks"][0]["notes"])
        max_time = get_max_time(piece["tracks"][0]["notes"], piece["tracks"][0]["chords"])
        piece["tracks"][0]["chords"] = rectify_chord_durs(piece["tracks"][0]["chords"], max_time, resolution=24)
        if "metadata" in piece:
            title = slugify(piece["metadata"]["title"])
        else:
            title = "unknown"
            
        # data augmentation
        if self.aug:
            pitch_shift = random.randint(-5, 6)
            aug_flag = True
            for t in range(len(piece["tracks"][0]["notes"])):
                if piece["tracks"][0]["notes"][t]["pitch"] <= 5 and piece["tracks"][0]["notes"][t]["pitch"] > 0:
                    aug_flag = False
            for t in range(len(piece["tracks"][0]["chords"])):
                if len(piece["tracks"][0]["chords"][t]["pitches"]) > 0:
                    if min(piece["tracks"][0]["chords"][t]["pitches"]) <= 5:
                        aug_flag = False
            if aug_flag:
                for t in range(len(piece["tracks"][0]["notes"])):
                    if piece["tracks"][0]["notes"][t]["pitch"] > 0:
                        piece["tracks"][0]["notes"][t]["pitch"] += pitch_shift
                for t in range(len(piece["tracks"][0]["chords"])):
                    if len(piece["tracks"][0]["chords"][t]["pitches"]) > 0:
                        for p in range(len(piece["tracks"][0]["chords"][t]["pitches"])):
                            piece["tracks"][0]["chords"][t]["pitches"][p] += pitch_shift

        tempo_list = []
        time_signature_list = []
        chord_list = []
        note_list = []
        
        if "tempos" in piece:
            for tempo in piece["tempos"]:
                tempo_list.append(Tempo(**tempo))
        else:
            tempo_list.append(Tempo(**{'time': 0, 'qpm': 120.0}))
        for time_signature in piece["time_signatures"]:
            time_signature_list.append(TimeSignature(**time_signature))
        for chord in piece["tracks"][0]["chords"]:
            chord_list.append(Chord(**chord))
        for note in piece["tracks"][0]["notes"]:
            note_list.append(Note(**note))

        if "beats" in piece.keys():
            beat_list = piece["beats"]
        else:
            beat_list = []
        
#         print(note_list)
        piece = Piece(
            name=name,
            title=title,
            chords=chord_list,
            notes=note_list,
            tempos=tempo_list,
            time_signatures=time_signature_list,
            beats=beat_list,
        )

        return piece
