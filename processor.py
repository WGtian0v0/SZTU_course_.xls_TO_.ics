import pandas as pd
from config import CONFIG
import utils
from calendar_builder import CalendarManager


def process_all(excel_file: str = CONFIG['excel_file']) -> None:
    """主处理流程：读取 Excel、清理表格、解析课程并构建日历

    Args:
        excel_file (str): 要读取的 Excel 文件路径，默认为 `CONFIG['excel_file']`。

    行为：
        - 读取并修改 DataFrame（局部变量 df）。
        - 调用 CalendarManager.add_event 向日历添加事件。
        - 将最终生成的日历保存为 'courses.ics'。
    """
    # 创建日历管理器实例，负责所有 iCalendar 相关操作
    cal_mgr = CalendarManager()

    # 使用 pandas 读取 Excel 文件
    df = pd.read_excel(excel_file)

    # 从表头推断班级和年级
    try:
        class_and_grade = str(df.iloc[0].iloc[0]).split()[1][3:]
    except Exception:
        class_and_grade = ""

    # 安全获取表格尺寸，用于边界检查
    rows = df.shape[0]
    cols = df.shape[1]

    # 清理：删除/合并相邻重复的课程条目
    for i in range(2, 10):
        for j in range(1, 8):
            if i >= rows or j >= cols:
                continue
            cell1 = df.iat[i, j]
            if pd.isna(cell1):
                continue
            if str(cell1).strip() == '':
                continue

            course_info1 = str(cell1).strip()
            course_info_list1 = course_info1.split('\n')

            # 查看下一行的同一列以判断是否存在重复/重叠信息
            if i + 1 >= rows:
                continue
            cell2 = df.iat[i + 1, j]
            if pd.isna(cell2):
                continue
            course_info2 = str(cell2).strip()
            course_info_list2 = course_info2.split('\n')

            try:
                if ('' in course_info_list1 and '' not in course_info_list2 and course_info_list2 in utils.split_list(
                        course_info_list1, '')) or course_info_list1 == course_info_list2:
                    df.iat[i + 1, j] = ' '
                elif '' not in course_info_list1 and '' in course_info_list2 and course_info_list1 in utils.split_list(
                        course_info_list2, ''):
                    df.iat[i, j] = ' '
                elif '' in course_info_list1 and '' in course_info_list2:
                    for k in utils.split_list(course_info_list1, ''):
                        for l in utils.split_list(course_info_list2, ''):
                            if k == l:
                                tmp = utils.split_list(course_info_list2, '')
                                tmp.remove(l)
                                result = "\n".join(*tmp)
                                df.iat[i + 1, j] = result
            except ValueError:
                # split_list 在找不到分割元素时会抛 ValueError，忽略并继续
                continue

    # 解析单元格并将课程添加到日历
    total_count = 0
    for i in range(2, 10):
        for j in range(1, 8):
            if i >= rows or j >= cols:
                continue
            cell = df.iat[i, j]
            if pd.isna(cell):
                continue
            cell_str = str(cell).strip()
            if cell_str == '' or cell_str == ' ':
                continue

            course_info_list = cell_str.split('\n')
            print('原始课程信息行：', course_info_list)

            infos = utils.get_info(course_info_list, default_class_and_grade=class_and_grade)
            for info in infos:
                course, class_name, teacher, times, numbers, location = info
                print('解析出：', course, class_name, teacher, times, numbers, location)
                #去除times前可能有的逗号
                times = times.lstrip(',')

                saw = utils.start_and_end_week(times)
                if isinstance(saw, tuple):
                    start_week, end_week = saw
                    cal_mgr.add_event(course, class_name, teacher, times, numbers, location, start_week, end_week, j)
                else:
                    for start_week, end_week in zip(*saw):
                        cal_mgr.add_event(course, class_name, teacher, times, numbers, location, start_week, end_week, j)

            print('----------------------')
            total_count += 1

    print(f'课程总数：{total_count}')
    cal_mgr.save()

