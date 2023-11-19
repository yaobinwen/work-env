import csv
import datetime
import enum
import io
import json
import pathlib
import re

from ywen.encoding import PREFERRED_ENCODING


class TaskType(enum.IntEnum):
    UNSPECIFIED = 0
    COORD = 1
    DEV = 2
    SUPPORT = 3
    OPS = 4
    MISC = 5


TASK_TYPE_TO_LETTER = {
    TaskType.COORD: "c",
    TaskType.DEV: "d",
    TaskType.SUPPORT: "s",
    TaskType.OPS: "o",
    TaskType.MISC: "m",
}
TASK_TYPE_LETTERS_GROUP = "".join(TASK_TYPE_TO_LETTER.values())

TASK_LETTER_TO_TYPE = {
    "c": TaskType.COORD,
    "d": TaskType.DEV,
    "s": TaskType.SUPPORT,
    "o": TaskType.OPS,
    "m": TaskType.MISC,
}


REGEX_LINE_DATE = re.compile(r"##\s*(\d{4})-(\d{2})-(\d{2})\s*\((\w{3})\)")
REGEX_LINE_VERSION = re.compile(r"\- version: (.+)")
REGEX_LINE_COORD = re.compile(r"\-\s*coord:")
REGEX_LINE_DEV = re.compile(r"\-\s*dev:")
REGEX_LINE_SUPPORT = re.compile(r"\-\s*support:")
REGEX_LINE_OPS = re.compile(r"\-\s*ops:")
REGEX_LINE_MISC = re.compile(r"\-\s*misc:")
REGEX_LINE_TASK = re.compile(
    rf"\s+-\s+(([{TASK_TYPE_LETTERS_GROUP}])\d+):\s+(\[.+\])*\s*(.*)"
)
REGEX_LINE_TT = re.compile(r"\-\s*tt:")
REGEX_LINE_TIME_TRACK_ENTRY = re.compile(
    r"\s+-\s+((\d{2}):(\d{2}))\s+~\s+((\d{2}):(\d{2})):\s+"
    + rf"(([{TASK_TYPE_LETTERS_GROUP}])\d+)"
)

REGEX_TASK_TAGS = re.compile(r"(\[\w+\])+")


class TaskTimeTrackEntry(object):
    def __init__(
        self, task_id: str, start_time: datetime.time, end_time: datetime.time
    ):
        self._task_id = task_id
        self._start_time = start_time
        self._end_time = end_time

    def __eq__(self, other):
        if isinstance(other, TaskTimeTrackEntry):
            return (self._task_id, self._start_time, self._end_time) == (
                other._task_id,
                other._start_time,
                other._end_time,
            )
        return NotImplemented

    @property
    def task_id(self):
        return self._task_id

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time


class TimeTrackNotes(object):
    def __init__(self, date: datetime.date):
        # Date of the notes.
        self._date = date
        self._version = None
        self._tasks = {}
        self._time_track_entries = {}
        self._statistics = {}

    @property
    def date(self):
        return self._date

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def tasks(self):
        return self._tasks

    def add_task(self, id, type, description, tags):
        if id in self._tasks:
            raise ValueError(f"task {id} had been added already")

        self._tasks[id] = {"type": type, "description": description, "tags": tags}

    @property
    def time_track_entries(self):
        return self._time_track_entries

    def add_time_track_entry(self, task_id, start_time, end_time):
        if task_id not in self._tasks:
            raise ValueError(f"task {task_id} is not found in tasks")

        if task_id not in self._time_track_entries:
            self._time_track_entries[task_id] = []

        self._time_track_entries[task_id].append(
            TaskTimeTrackEntry(
                task_id=task_id, start_time=start_time, end_time=end_time
            )
        )

    def get_task_time_track_entries(self, task_id):
        if task_id not in self._time_track_entries:
            raise ValueError(f"task {task_id} is not found in time track entries")

        return self._time_track_entries[task_id]

    @property
    def time_statistics(self):
        return self._statistics


class TimeTrackDayStatistics(object):
    def __init__(self, time_track_notes: TimeTrackNotes):
        self._date = time_track_notes.date
        self._statistics = {}
        self._tracked_mins = 0  # Total tracked time in minutes.

        self._calc_time_statistics(time_track_notes=time_track_notes)

    def _calc_time_statistics(self, time_track_notes: TimeTrackNotes):
        for task_type in [
            TaskType.COORD,
            TaskType.DEV,
            TaskType.SUPPORT,
            TaskType.OPS,
            TaskType.MISC,
        ]:
            self._statistics[task_type] = 0

        time_track_entries = time_track_notes.time_track_entries

        for task_id, time_entries in time_track_entries.items():
            task_type_letter = task_id[0]
            task_type = TASK_LETTER_TO_TYPE[task_type_letter]
            for entry in time_entries:
                start_time = entry.start_time
                end_time = entry.end_time
                start_time_in_min = start_time.hour * 60 + start_time.minute
                end_time_in_min = end_time.hour * 60 + end_time.minute
                duration_min = end_time_in_min - start_time_in_min

                self._statistics[task_type] += duration_min
                self._tracked_mins += duration_min

    @property
    def date(self):
        return self._date

    @property
    def statistics(self):
        return self._statistics

    @property
    def tracked_mins(self):
        return self._tracked_mins


# TODO(ywen): `StatisticsDB` is really not just file-based. However, to get
# things started quickly, I'm making it a file-based DB.
class StatisticsDB(object):
    def __init__(self, db_dpath: pathlib.Path):
        self._db_dpath = db_dpath
        self._file_latest = None

    def _read_next_index(self):
        index = None

        fpath_index = self._db_dpath / "index"
        try:
            index = json.loads(fpath_index.read_text(encoding="utf-8"))
        except FileNotFoundError as ex:
            fpath_index.write_text(data=f"{json.dumps(0)}\n", encoding="utf-8")
            index = self._read_next_index()

        return index

    def _create_new_file(self):
        index = self._read_next_index()

        fname_new_file = f"{index}.csv"
        fpath_new_file = self._db_dpath / fname_new_file

        with io.open(file=fpath_new_file, mode="w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["date", "dev", "support", "ops", "coord", "misc", "tracked_mins"]
            )

        fpath_latest = self._db_dpath / "latest"
        fpath_latest.symlink_to(fname_new_file)

    def open(self):
        fpath_latest = self._db_dpath / "latest"
        try:
            size = fpath_latest.stat().st_size
            if size > 1024 * 1024 * 2:
                self._create_new_file()

            self._file_latest = io.open(file=fpath_latest, mode="a", encoding="utf-8")
        except FileNotFoundError:
            self._create_new_file()
            self.open()

    def close(self):
        self._file_latest.close()

    def append(self, day_statistics: TimeTrackDayStatistics):
        writer = csv.writer(self._file_latest)
        writer.writerow(
            [
                day_statistics.date,
                day_statistics.statistics[TaskType.DEV],
                day_statistics.statistics[TaskType.SUPPORT],
                day_statistics.statistics[TaskType.OPS],
                day_statistics.statistics[TaskType.COORD],
                day_statistics.statistics[TaskType.MISC],
                day_statistics.tracked_mins,
            ]
        )


def _process_time_tracking_notes(
    logger,
    time_tracking_notes_content: str,
):
    lines = time_tracking_notes_content.splitlines()

    tt_notes = None
    tt_notes_list = []
    tt_notes_begin = False
    task_type_wip = TaskType.UNSPECIFIED

    for line in lines:
        if not line.strip():
            # If a line becomes empty after stripping, that means it is empty.
            # The leading whitespaces are important for the notes, so we do not
            # use the stripped line but the raw line.
            continue

        logger.debug("%s", line)
        m = REGEX_LINE_DATE.fullmatch(line)
        if m:
            if tt_notes:
                tt_notes_list.append(tt_notes)

                tt_notes_begin = False
                tt_notes = None

            tt_notes_begin = True
            tt_year = int(m.group(1))
            tt_month = int(m.group(2))
            tt_day = int(m.group(3))
            tt_day_of_week = m.group(4)

            tt_date = datetime.date(year=tt_year, month=tt_month, day=tt_day)
            weekday_name = tt_date.strftime("%a")
            if weekday_name != tt_day_of_week:
                raise ValueError(f"mismatch")

            tt_notes = TimeTrackNotes(date=tt_date)

            continue

        m = REGEX_LINE_VERSION.fullmatch(line)
        if m:
            if not tt_notes_begin:
                raise ValueError(f"no open time track block")

            version = m.group(1)
            tt_notes.version = version

            continue

        m = REGEX_LINE_COORD.fullmatch(line)
        if m:
            if not tt_notes_begin:
                raise ValueError(f"no open time track block")

            task_type_wip = TaskType.COORD

            continue

        m = REGEX_LINE_DEV.fullmatch(line)
        if m:
            if not tt_notes_begin:
                raise ValueError(f"no open time track block")

            task_type_wip = TaskType.DEV

            continue

        m = REGEX_LINE_SUPPORT.fullmatch(line)
        if m:
            if not tt_notes_begin:
                raise ValueError(f"no open time track block")

            task_type_wip = TaskType.SUPPORT

            continue

        m = REGEX_LINE_OPS.fullmatch(line)
        if m:
            if not tt_notes_begin:
                raise ValueError(f"no open time track block")

            task_type_wip = TaskType.OPS

            continue

        m = REGEX_LINE_MISC.fullmatch(line)
        if m:
            if not tt_notes_begin:
                raise ValueError(f"no open time track block")

            task_type_wip = TaskType.MISC

            continue

        m = REGEX_LINE_TASK.fullmatch(line)
        if m:
            if not tt_notes_begin:
                raise ValueError(f"no open time track block")
            if task_type_wip == TaskType.UNSPECIFIED:
                raise ValueError(f"no open task type")

            task_id = m.group(1)
            task_type_letter = m.group(2)
            task_tags_str = m.group(3)
            task_description = m.group(4)

            if task_type_letter != TASK_TYPE_TO_LETTER[task_type_wip]:
                raise ValueError(
                    f"'{line}': expected task type letter "
                    f"{TASK_TYPE_TO_LETTER[task_type_wip]} but got {task_type_letter}"
                )

            task_tags = (
                re.findall(pattern=r"\w+", string=task_tags_str)
                if task_tags_str
                else []
            )

            tt_notes.add_task(
                id=task_id,
                type=TASK_LETTER_TO_TYPE[task_type_letter],
                description=task_description,
                tags=task_tags,
            )

            continue

        m = REGEX_LINE_TT.fullmatch(line)
        if m:
            if not tt_notes_begin:
                raise ValueError(f"no open time track block")

            continue

        m = REGEX_LINE_TIME_TRACK_ENTRY.fullmatch(line)
        if m:
            if not tt_notes_begin:
                raise ValueError(f"no open time track block")

            t1_H_str = int(m.group(2))
            t1_M_str = int(m.group(3))
            t2_H_str = int(m.group(5))
            t2_M_str = int(m.group(6))
            task_id = m.group(7)

            t1 = datetime.time(hour=t1_H_str, minute=t1_M_str)
            t2 = datetime.time(hour=t2_H_str, minute=t2_M_str)

            tt_notes.add_time_track_entry(task_id=task_id, start_time=t1, end_time=t2)

            continue

        raise ValueError(f"line '{line}' does not match anything")

    if tt_notes:
        tt_notes_list.append(tt_notes)
        tt_notes_begin = False
        tt_notes = None

    return tt_notes_list


def _do_subcmd_add(
    logger,
    subcmd: str,
    time_tracking_notes_file: pathlib.Path,
    statistics_db: pathlib.Path,
) -> int:
    # Open the database of the historical statistics.
    db = StatisticsDB(db_dpath=statistics_db)
    db.open()

    content = time_tracking_notes_file.read_text(encoding=PREFERRED_ENCODING)

    tt_notes_list = _process_time_tracking_notes(
        logger=logger, time_tracking_notes_content=content
    )

    # Append to the statistics database.
    for tt_notes in tt_notes_list:
        db.append(day_statistics=TimeTrackDayStatistics(time_track_notes=tt_notes))

    db.close()

    return 0


def syntax_subcmd_add(subcmds):
    desc = "Add new time tracking notes into database"
    subcmd = subcmds.add_parser("add", description=desc, help=desc)
    subcmd.set_defaults(func=_do_subcmd_add)

    subcmd.add_argument(
        "time_tracking_notes_file",
        metavar="PATH",
        help="File of time tracking notes to be added",
        type=pathlib.Path,
    )

    subcmd.add_argument(
        "statistics_db",
        metavar="PATH",
        help="Path to the historical statistics database folder",
        type=pathlib.Path,
    )
