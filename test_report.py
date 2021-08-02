import pytest

from report import ampm_to_minutes, minutes_to_ampm
from report import get_overlapping_times, read_times, format_overlapping_times

@pytest.mark.parametrize("ampm,minutes", [
    ("12:00am", 0),
    ("12:00pm", 12*60),
    ("9:00am", 9*60),
    ("9:00pm", 21*60),
    ("12:01am", 1),
    ("12:59pm", 12*60+59),
    ("9:30am", 9*60+30)
])
def test_ampm_to_minutes(ampm, minutes):
    assert ampm_to_minutes(ampm) == minutes
    assert minutes_to_ampm(minutes) == ampm

@pytest.mark.parametrize("content,expected", [
    ("12:00am,12:00pm", [(0, 12*60)]),
    ("9:01am,9:02am\n10:11pm,11:59pm", [(9*60+1, 9*60+2), (22*60+11, 23*60+59)])
])
def test_read_times(tmpdir, content, expected):
    file_name = tmpdir.join("times")
    with open(file_name, "w") as f:
        f.write("start,end\n")
        f.write(content)
    actual = list(read_times(file_name))
    assert actual == expected


@pytest.mark.parametrize("times,overlapping", [
    ([(0, 1)], []),
    ([(1, 2), (2, 3), (3, 4)], []),
    ([(5, 10), (1, 2), (3, 6), (6, 7), (7, 12), (15, 20)], 
     [((3, 6), (5, 10)), ((5, 10), (6, 7)), ((5, 10), (7, 12))]),
])
def test_get_overlapping_times(times, overlapping):
    assert list(get_overlapping_times(times)) == overlapping

@pytest.mark.parametrize("overlapping,expected", [
    ([], []),
    ([((9*60, 10*60), (9*60+30, 10*60+30))], ["(9:00am - 10:00am) and (9:30am - 10:30am)"]),
    ([((0, 2), (1, 3)), ((5, 10), (6, 7))], 
        ["(12:00am - 12:02am) and (12:01am - 12:03am)",
         "(12:05am - 12:10am) and (12:06am - 12:07am)"])
])
def test_format_overlapping_times(overlapping, expected):
    assert list(format_overlapping_times(overlapping)) == expected
