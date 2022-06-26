"""
    Reads out chords from musicXML
    by x.h.
"""

import xml.etree.ElementTree as ET
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--f", type=str, required=True, help="provide a MusicXML file path (relative of absolute)")
opt = parser.parse_args()

file = opt.f
tree = ET.parse(file)
source = tree.getroot()
score = source.find('part')

# start parsing the score
chord_progression = []
bar_cnt = 0

for child in score.findall('measure'):
    chord_progression_this_bar = []

    for sub_child in child.findall('harmony'):
        # get root and chord type
        root = sub_child[0][0].text
        alter = sub_child[0][1].text
        kind = sub_child[1].text

        if alter == '-1':
            alter = 'b'
        elif alter == '1':
            alter = '#'
        else:
            alter = ''

        chord_progression_this_bar.append("{}{} {}".format(root, alter, kind))

    chord_progression.append(chord_progression_this_bar)
    bar_cnt += 1

print("total bars encountered: ", bar_cnt)
print("chord progression: ", chord_progression)