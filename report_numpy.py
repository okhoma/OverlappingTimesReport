from datetime import datetime as dt
import argparse
import numpy as np


def ampm_to_minutes(ampm):
    t = dt.strptime(ampm, "%I:%M%p")
    return t.hour * 60 + t.minute


def minutes_to_ampm(m):
    h = m//60
    m = m%60
    ampm = "am" if h < 12 else "pm"
    if h == 0:
        h = 12
    elif h > 12:
        h -= 12
    return f"{h}:{m:02}{ampm}"


def get_overlapping_times(start, end):
    # assuming sorted!!
    # use broadcasting to compare all starts with all ends
    start_t = start[:, np.newaxis]
    
    # no overlapping would produce upper triangular matrix of True
    # any overlaps would result in True in the lower triangular portion
    group1, group2 = np.tril(start_t < end, k=-1).nonzero()

    # Use overlaps' indices to get actual times
    result = [((start[group1[i]], end[group1[i]]), (start[group2[i]], end[group2[i]])) 
                for i in range(len(group1))]
    return result


def format_overlapping_times(times):
    if times:
        t = minutes_to_ampm
        for (start1, end1), (start2, end2) in times:
            yield f"({t(start1)} - {t(end1)}) and ({t(start2)} - {t(end2)})"


def read_times(file_name):
    start, end = np.genfromtxt(file_name, dtype=int, delimiter=",", names=True, unpack=True,
                               encoding="utf-8", converters={0: ampm_to_minutes, 1: ampm_to_minutes})
    return start, end


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find overlapping times")
    parser.add_argument("file_name", help="File path with times")
    args = parser.parse_args()

    start, end = read_times(args.file_name)
    overlapping = list(get_overlapping_times(start, end))

    if overlapping:
        report = format_overlapping_times(overlapping)
        print("Overlapping times:\n" + "\n".join(report))
    else:
        print("No overlapping times")
