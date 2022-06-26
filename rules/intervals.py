'''
    intervals
'''
INT_m2 = 1
INT_M2 = 2
INT_a2 = 3
INT_m3 = 3
INT_M3 = 4
INT_4 = 5
INT_a4 = 6
INT_5 = 7
INT_a5 = 8
INT_m6 = 8
INT_M6 = 9
INT_m7 = 10
INT_M7 = 11
INT_8 = 12
INT_m9 = 13
INT_M9 = 14
INT_a9 = 15
INT_m10 = 15
INT_M10 = 16
INT_11 = 17
INT_a11 = 18
INT_12 = 19
INT_a12 = 20
INT_m13 = 20
INT_M13 = 21
INT_m14 = 22
INT_M14 = 23

def is_unison(interval):
    return interval%12 == 0

def is_minor_3rd(interval):
    return interval%12 == INT_m3
def is_major_3rd(interval):
    return interval%12 == INT_M3
def is_3rd(interval):
    return is_minor_3rd(interval) or is_major_3rd(interval)

def is_5th(interval):
    return (interval)%12 == INT_5

def is_minor_7th(interval):
    return interval%12 == INT_m7
def is_major_7th(interval):
    return interval%12 == INT_M7
def is_7th(interval):
    return is_minor_7th(interval) or is_major_7th(interval)