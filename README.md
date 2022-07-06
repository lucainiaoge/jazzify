# Jazzify

This is an open-source rule-based jazzification system. Given a melody track and a chord track, `Jazzify` is able to transfer it into swing jazz style or bossa nova style.

`Jazzify` is rule-based. Apart from its capability to jazzify non-jazz piece, it can also serve as an engine of computational jazz music theory. `Jazzify` is able to accomplish tasks including chord-symbol identification, key detection, chord extension, chord-to-scale, chord-to-voicing, walking-bass generation.

As a bonus, `Jazzify` provides a swingified and a bossaified version of [Nottingham Dataset](https://ifdo.ca/~seymour/nottingham/nottingham.html). `Jazzify` takes the input in [muspy](https://muspy.com/ "muspy")'s format (json). The swingified Nottingham Dataset is saved in ```nottingham_swingified.zip```, and the bossaified Nottingham Dataset is saved in ```nottingham_bossaified.zip```..

## Run the Code

1. Unzip the muspy-formatted Nottingham Dataset in the `data` directory
2. `python jazzify_nottingham.py [out_dir] [style]`, where `[style]` chosen from "swing" and "bossa".

## Features

### Chord Symbol Identification

`Jazzify` is able to convert list of pitches into its corresponding jazz chord symbol, in format "`(root_note, chord_type, bass_note)`". Our system is more accurate and faster than `music21`.

A comprehensive comparison between our system and existing chord symbol identification wheels can be found in `1-chord_test.ipynb`.

### Key Detection

`Jazzify` is able to give the `(function, key)` guesses for each chord, given a chord progression. For example, given chord progression `[C, D, F, G, G-, C7, F]`, `Jazzify` is able to output `[(T,C), (DD,C), (S,C), (D,C), (S,F), (D,F), (T,F)]`.

`Jazzify` takes acccout of tonic (`T`), dominant (`D`), subdominant (`S`), double-dominant (`DD`), Napoleon (`N`) functions. Other functions like the leading seventh can be converted into the existing categories.

Users are free to give feedbacks on this system. It is not complete, in terms of classical harmony analysis. However, it is powerful enough to handle most jazz standards.

A set of examples of key detection can be found in `2-key_finding_test.ipynb`. A lot of chord progressions in jazz standards are incorporated as examples.

### Comping and Melody Swingification

`Jazzify` is able to generate walking bass, piano rootless voicing comping based on the given chord progression. Details are introduced in the documents. The chord-symbol identification and key detection systems are the building blocks of this comping system.

Moreover, `Jazzify` is able to swingify melody. Combining those systems, `Jazzify` is able to swingify the pieces in Nottingham Dataset.

## Json Format
Input piece should in dictionary format
```
{
	"metadata": {
		"title": str,
		...
	}

	"tracks": [
	{
		"notes": [{"time":int, "duration":int, "pitch":int}],
		"chords": [{"time":int, "duration":int, "pitches":int}],
	}]
	"time_signatures": [
		{"time":int, "numinator":int, "denominator":int}
	]
	"tempos": [
		{"time":int, "qpm":float}
	]
	...
}
```

The json files in Nottingham Swingified/Bossaified are in format
```
{
	"metadata": {
		"title": str,
	}

	"tracks": [
	{
		"notes": [{"time":int, "duration":int, "pitch":int}],
		"voicings": [{"time":int, "duration":int, "pitches":int}],
		"basses": [{"time":int, "duration":int, "pitch":int}],
	}]
	"time_signatures": [
		{"time":int, "numinator":int, "denominator":int}
	]
	"tempos": [
		{"time":int, "qpm":float}
	]
	"chord_symbols": [
		(root:int, symbol:str, bass:int/None)
	]
	...
}
```
