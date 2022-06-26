"""Music Structures."""


from typing import List
from pydantic import BaseModel


class Note(BaseModel):
    pitch: int
    duration: int
    time: int = 0


class Chord(BaseModel):
    pitches: List[int]
    duration: int
    time: int


class TimeSignature(BaseModel):
    numerator: int
    denominator: int
    time: int


class Tempo(BaseModel):
    qpm: int
    time: int


class Piece(BaseModel):
    name: str
    title: str
    chords: List[Chord]
    notes: List[Note]
    tempos: List[Tempo]
    time_signatures: List[TimeSignature]
    beats: List = []
