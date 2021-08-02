import pytest

from report import OverlappingTimesReport

@pytest.fixture
def reporter():
    r = OverlappingTimesReport()
    return r

@pytest.mark.parametrize("ampm,minutes", [
    ("12:00am", 0),
    ("12:00pm", 12*60),
    ("9:00am", 9*60),
    ("9:00pm", 21*60),
    ("12:01am", 1),
    ("12:59pm", 12*60+59),
    ("9:30am", 9*60+30)
])
def test_ampm_to_minutes(reporter, ampm, minutes):
    assert reporter._ampm_to_minutes(ampm) == minutes
    assert reporter._minutes_to_ampm(minutes) == ampm

@pytest.mark.parametrize("content,expected", [
    ("12:00am,12:00pm", [(0, 12*60)]),
    ("9:01am,9:02am\n10:11pm,11:59pm", [(9*60+1, 9*60+2), (22*60+11, 23*60+59)])
])
def test_read_times(reporter, tmpdir, content, expected):
    file_name = tmpdir.join("times")
    with open(file_name, "w") as f:
        f.write("start,end\n")
        f.write(content)
    actual = list(reporter._read_times(file_name))
    assert actual == expected


@pytest.mark.parametrize("content,expected_business_day_range", [
    ("12:00am,12:00pm", None),
    ("#BDAY:9:00am,5:00pm\n9:00am,9:30pm", (9*60, 17*60))
])
def test_read_times_with_business_day_range(reporter, tmpdir, content, expected_business_day_range):
    file_name = tmpdir.join("times")
    with open(file_name, "w") as f:
        f.write("start,end\n")
        f.write(content)
    _ = list(reporter._read_times(file_name))
    
    assert reporter.business_day_range == expected_business_day_range


@pytest.mark.parametrize("times,overlapping", [
    ([(0, 1)], []),
    ([(1, 2), (2, 3), (3, 4)], []),
    ([(5, 10), (1, 2), (3, 6), (6, 7), (7, 12), (15, 20)], 
     [((3, 6), (5, 10)), ((5, 10), (6, 7)), ((5, 10), (7, 12))]),
])
def test_get_overlapping_times(reporter, times, overlapping):
    assert list(reporter._get_overlapping_times(times)) == overlapping

@pytest.mark.parametrize("times,overlapping", [
    ([(0, 1)], []),
    ([(1, 2), (2, 3), (3, 4)], []),
    ([(5, 10), (1, 2), (3, 6), (6, 7), (7, 12), (15, 20)], [((5, 10), (6, 7))]),
])
def test_get_overlapping_times_with_business_day(reporter, times, overlapping):
    reporter.business_day_range = (4, 10)
    assert list(reporter._get_overlapping_times(times)) == overlapping


@pytest.mark.parametrize("overlapping,expected", [
    ([], []),
    ([((9*60, 10*60), (9*60+30, 10*60+30))], ["(9:00am - 10:00am) and (9:30am - 10:30am)"]),
    ([((0, 2), (1, 3)), ((5, 10), (6, 7))], 
        ["(12:00am - 12:02am) and (12:01am - 12:03am)",
         "(12:05am - 12:10am) and (12:06am - 12:07am)"])
])
def test_format_overlapping_times(reporter, overlapping, expected):
    assert list(reporter._format_overlapping_times(overlapping)) == expected
