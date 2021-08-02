from datetime import datetime as dt
import argparse

class OverlappingTimesReport:
    def __init__(self, business_day_range = None):
        self.business_day_range = business_day_range

    @staticmethod
    def _ampm_to_minutes(ampm):
        t = dt.strptime(ampm, "%I:%M%p")
        return t.hour * 60 + t.minute

    @staticmethod
    def _minutes_to_ampm(m):
        h = m//60
        m = m%60
        ampm = "am" if h < 12 else "pm"
        if h == 0:
            h = 12
        elif h > 12:
            h -= 12
        return f"{h}:{m:02}{ampm}"

    def _eliminate_events_within_business_hours(self, times):
        if self.business_day_range is None:
            return times

        result = []
        bd_start, bd_end = self.business_day_range
        for start, end in times:
            if start >= bd_start and end <= bd_end:
                result.append((start, end))
        return result


    def _get_overlapping_times(self, times):
        sorted_times = sorted(times)
        remaining_times = self._eliminate_events_within_business_hours(sorted_times)
        num_times = len(remaining_times)
        if remaining_times:
            for i in range(num_times):
                start1, end1 = remaining_times[i]
                
                for j in range(i+1, num_times):
                    start2, end2 = remaining_times[j]
                    if start2 >= end1:
                        break
                    
                    if end2 > start1:
                        yield (start1, end1), (start2, end2)


    def _format_overlapping_times(self, times):
        if times:
            t = self._minutes_to_ampm
            for (start1, end1), (start2, end2) in times:
                yield f"({t(start1)} - {t(end1)}) and ({t(start2)} - {t(end2)})"


    def _read_times(self, file_name):
        times = []
        with open(file_name) as f:
            _ = f.readline()  # skip header
            for line in f:
                start, end = line.split(",")
                if start.startswith("#BDAY:"):
                    start = start[6:]
                    self.business_day_range = (self._ampm_to_minutes(start), self._ampm_to_minutes(end.strip("\n")))
                else:
                    times.append((self._ampm_to_minutes(start), self._ampm_to_minutes(end.strip("\n"))))
        return times

    def generate_report(self, file_name):
        times = self._read_times(file_name)
        overlapping = list(self._get_overlapping_times(times))
        report = self._format_overlapping_times(overlapping) if overlapping else None
        return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find overlapping times")
    parser.add_argument("file_name", help="File path with times")
    args = parser.parse_args()

    report_generator = OverlappingTimesReport()

#     _ = list(report_generator._get_overlapping_times([(5, 10), (1, 2), (3, 6), (6, 7), (7, 12), (15, 20)]))

    report = report_generator.generate_report(args.file_name)

    if report:
        print("Overlapping times:\n" + "\n".join(report))
    else:
        print("No overlapping times")
