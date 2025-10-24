from datetime import datetime
from typing import List

# 参数配置，输入文件名和学期开始日期（第一周第一天）
CONFIG = {
    'excel_file': '学生个人课表_xxxxxxxxxxxx.xls',
    'semester_start': datetime(2025, 9, 8),
}

# 节次开始时间
TIME_LIST: List[str] = ['08:30', '9:15', '10:15', '11:00', '11:45',
                       '14:00', '14:45', '15:45', '16:30', '17:15',
                       '19:00', '19:40', '20:30', '21:10',
                       '18:00']

