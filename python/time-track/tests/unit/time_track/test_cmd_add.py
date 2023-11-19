import datetime
import unittest
import unittest.mock as mock

from time_track.cmd_add import (
    _process_time_tracking_notes,
    TaskType,
    TaskTimeTrackEntry,
    TimeTrackDayStatistics,
)
from ywen.tempfile import temp_dir


class TestImport(unittest.TestCase):
    def test_import(self):
        import time_track.cmd_add


TT_SAMPLE = """
##2023-11-18(Sat)

- version: 1
- coord:
    - c1: Weekly meeting
- dev:
    - d1: [PR103][J13] HSS
- support:
    - s1: [Nick] Set up laptop.
- ops:
    - o1: [internal][Ricky] Answer questions
- misc:
    - m1: Read review report.
- tt:
    - 09:00 ~ 09:15: c1
    - 09:15 ~ 15:00: d1
    - 15:00 ~ 15:20: s1
    - 15:20 ~ 16:00: d1
    - 16:00 ~ 16:30: o1
    - 16:30 ~ 17:00: m1
"""


# TODO(ywen): Add more negative test cases:
# - 1). Sanity check that there is no time overlap.
# - 2). Detect repeated tags (or maybe just use a set).
# - 3). What if I work into the next day?
# - 4). What if I want to use AM/PM format instead of 24-hour format?


class Test_do_subcmd_add(unittest.TestCase):
    def test(self):
        with temp_dir(prefix="time-track.") as dtemp:
            time_tracking_notes_file = dtemp / "tt.txt"
            time_tracking_notes_file.write_text(TT_SAMPLE)

            logger = mock.Mock()

            tt_notes = _process_time_tracking_notes(
                logger=logger,
                time_tracking_notes_content=time_tracking_notes_file.read_text(),
            )

        self.assertEqual(tt_notes.version, "1")

        # Verify tasks.
        tasks = tt_notes.tasks
        self.assertSetEqual(
            set(list(tasks.keys())), set(["c1", "d1", "s1", "o1", "m1"])
        )
        self.assertDictEqual(
            tasks["c1"],
            {"type": TaskType.COORD, "description": "Weekly meeting", "tags": []},
        )
        self.assertDictEqual(
            tasks["d1"],
            {"type": TaskType.DEV, "description": "HSS", "tags": ["PR103", "J13"]},
        )
        self.assertDictEqual(
            tasks["s1"],
            {
                "type": TaskType.SUPPORT,
                "description": "Set up laptop.",
                "tags": ["Nick"],
            },
        )
        self.assertDictEqual(
            tasks["o1"],
            {
                "type": TaskType.OPS,
                "description": "Answer questions",
                "tags": ["internal", "Ricky"],
            },
        )
        self.assertDictEqual(
            tasks["m1"],
            {"type": TaskType.MISC, "description": "Read review report.", "tags": []},
        )

        # Verify time tracking entries.
        c1_tt_entries = tt_notes.get_task_time_track_entries("c1")
        self.assertEqual(len(c1_tt_entries), 1)
        self.assertEqual(
            c1_tt_entries[0],
            TaskTimeTrackEntry(
                task_id="c1",
                start_time=datetime.time(hour=9, minute=0),
                end_time=datetime.time(hour=9, minute=15),
            ),
        )

        d1_tt_entries = tt_notes.get_task_time_track_entries("d1")
        self.assertEqual(len(d1_tt_entries), 2)
        self.assertEqual(
            d1_tt_entries[0],
            TaskTimeTrackEntry(
                task_id="d1",
                start_time=datetime.time(hour=9, minute=15),
                end_time=datetime.time(hour=15, minute=00),
            ),
        )
        self.assertEqual(
            d1_tt_entries[1],
            TaskTimeTrackEntry(
                task_id="d1",
                start_time=datetime.time(hour=15, minute=20),
                end_time=datetime.time(hour=16, minute=00),
            ),
        )

        s1_tt_entries = tt_notes.get_task_time_track_entries("s1")
        self.assertEqual(len(s1_tt_entries), 1)
        self.assertEqual(
            s1_tt_entries[0],
            TaskTimeTrackEntry(
                task_id="s1",
                start_time=datetime.time(hour=15, minute=00),
                end_time=datetime.time(hour=15, minute=20),
            ),
        )

        o1_tt_entries = tt_notes.get_task_time_track_entries("o1")
        self.assertEqual(len(o1_tt_entries), 1)
        self.assertEqual(
            o1_tt_entries[0],
            TaskTimeTrackEntry(
                task_id="o1",
                start_time=datetime.time(hour=16, minute=00),
                end_time=datetime.time(hour=16, minute=30),
            ),
        )

        m1_tt_entries = tt_notes.get_task_time_track_entries("m1")
        self.assertEqual(len(m1_tt_entries), 1)
        self.assertEqual(
            m1_tt_entries[0],
            TaskTimeTrackEntry(
                task_id="m1",
                start_time=datetime.time(hour=16, minute=30),
                end_time=datetime.time(hour=17, minute=00),
            ),
        )

        day_statistics = TimeTrackDayStatistics(time_track_notes=tt_notes)
        statistics = day_statistics.statistics
        self.assertEqual(statistics[TaskType.COORD], 15)
        self.assertEqual(statistics[TaskType.DEV], 5 * 60 + 45 + 40)
        self.assertEqual(statistics[TaskType.SUPPORT], 20)
        self.assertEqual(statistics[TaskType.OPS], 30)
        self.assertEqual(statistics[TaskType.MISC], 30)
        self.assertEqual(day_statistics.tracked_mins, 480)


if __name__ == "__main__":
    unittest.main()
