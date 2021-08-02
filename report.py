from datetime import datetime as dt
import argparse


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


def get_overlapping_times(times):
    num_times = len(times)
    sorted_times = sorted(times)
    for i in range(num_times):
        start1, end1 = sorted_times[i]
        
        for j in range(i+1, num_times):
            start2, end2 = sorted_times[j]
            if start2 >= end1:
                break
            
            if end2 > start1:
                yield (start1, end1), (start2, end2)


def format_overlapping_times(times):
    if times:
        t = minutes_to_ampm
        for (start1, end1), (start2, end2) in times:
            yield f"({t(start1)} - {t(end1)}) and ({t(start2)} - {t(end2)})"


def read_times(file_name):
    times = []
    with open(file_name) as f:
        _ = f.readline()  # skip header
        for line in f:
            start, end = line.split(",")
            times.append((ampm_to_minutes(start), ampm_to_minutes(end.strip("\n"))))
    return times


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find overlapping times")
    parser.add_argument("file_name", help="File path with times")
    args = parser.parse_args()

    times = read_times(args.file_name)
    overlapping = list(get_overlapping_times(times))

    if overlapping:
        report = format_overlapping_times(overlapping)
        print("Overlapping times:\n" + "\n".join(report))
    else:
        print("No overlapping times")
