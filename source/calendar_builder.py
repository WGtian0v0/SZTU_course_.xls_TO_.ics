from datetime import datetime, timedelta
from typing import List
from icalendar import Calendar, Event, Timezone, TimezoneStandard
import pytz
from config import CONFIG, TIME_LIST


class CalendarManager:
    """封装 iCalendar 构建与事件添加的类

    本类将日历相关行为集中管理。其他模块通过调用本类的方法来添加事件或保存日历，而无需知道 icalendar 的 内部细节。
    """

    def __init__(self) -> None:
        self.tz = pytz.timezone('Asia/Shanghai')
        self.calendar = Calendar()
        self.calendar.add('prodid', '-//Course Schedule//')
        self.calendar.add('version', '2.0')
        # 添加时区组件（Asia/Shanghai）到日历对象
        _tz = Timezone()
        _tz.add('TZID', 'Asia/Shanghai')
        _tz_std = TimezoneStandard()
        _tz_std.add('TZOFFSETFROM', timedelta(hours=8))
        _tz_std.add('TZOFFSETTO', timedelta(hours=8))
        _tz_std.add('TZNAME', 'CST')
        _tz_std.add('DTSTART', datetime(1970, 1, 1))
        _tz.add_component(_tz_std)
        self.calendar.add_component(_tz)

        # 用于去重已经添加过的单日事件（以 summary, location, dtstart, dtend 为键）
        self._added = set()

    def add_event(self, course: str, class_name: str, teacher: str, times: str, numbers: List[int],
                  location: str, start_week: int, end_week: int, weekday: int) -> None:
        """向托管的日历添加课程事件（按周逐个生成，并自动去重）。

        为了避免由于表格中相邻单元格重复或重叠周次导致生成重复的重复事件，
        本方法会针对每一周生成独立的单次事件（不使用 RRULE）并在内部追踪已添加的事件，
        以确保同一课程同一日期不会重复出现。

        Args:
            course (str): 课程名称。
            class_name (str): 班级或教学班信息，用于事件描述。
            teacher (str): 任课教师姓名。
            times (str): 原始周次/节次字符串（用于描述及解析）。
            numbers (List[int]): 节次编号列表，例如 [1,2]。
            location (str): 上课地点。
            start_week (int): 起始周（学期第几周，1 基准）。
            end_week (int): 结束周。
            weekday (int): 星期几（1 表示周一，7 表示周日）。

        Returns:
            None。函数将事件添加到 `self.calendar`。
        """
        semester_start = CONFIG['semester_start']
        start_number = numbers[0]
        end_number = numbers[-1]
        start_time = datetime.strptime(TIME_LIST[start_number - 1], "%H:%M").time()
        end_time = (datetime.strptime(TIME_LIST[end_number - 1], "%H:%M") + timedelta(minutes=40)).time()

        # 计算学期第一周对应的目标 weekday 的日期
        target_weekday = weekday - 1
        start_weekday = semester_start.weekday()
        days_diff = (target_weekday - start_weekday) % 7
        first_day = semester_start + timedelta(days=days_diff)

        # 为避免重复，按每周生成独立事件并使用 self._added 去重
        for wk in range(start_week, end_week + 1):
            day = first_day + timedelta(weeks=wk - 1)
            dtstart = self.tz.localize(datetime.combine(day.date(), start_time))
            dtend = self.tz.localize(datetime.combine(day.date(), end_time))

            # 去重键：课程名、地点、开始时间、结束时间（使用 ISO 字符串）
            key = (course, location, dtstart.isoformat(), dtend.isoformat())
            if key in self._added:
                continue
            self._added.add(key)

            event = Event()
            event.add('summary', course)
            event.add('description', location + '\n' + teacher + '\n' + class_name + '\n' + times)
            event.add('location', location)
            event.add('dtstart', dtstart)
            event['dtstart'].params['TZID'] = 'Asia/Shanghai'
            event.add('dtend', dtend)
            event['dtend'].params['TZID'] = 'Asia/Shanghai'
            self.calendar.add_component(event)

    def save(self, filename: str = 'courses.ics') -> None:
        """将构建好的日历写入指定文件（默认 'courses.ics'）。"""
        with open(filename, 'wb') as f:
            f.write(self.calendar.to_ical())
        print(f'日历已保存到 {filename}')
