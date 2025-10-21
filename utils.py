import re
from typing import List, Tuple, TypeVar, Union

T = TypeVar('T')


def split_list(lst: List[T], element: T) -> List[List[T]]:
    """
        分割列表

        简要说明：
            将输入的列表 `lst` 按第一次出现的 `element` 分割成两个子列表并返回。

        Args:
            lst (List[T]): 要分割的列表。
            element (T): 用作分割标识的元素；在第一次出现的位置进行分割。

        Returns:
            List[List[T]]: 返回包含两个子列表的列表 [before, after]，不包含分割元素本身。
                - before: 位于第一个匹配元素之前的元素列表
                - after: 位于第一个匹配元素之后的元素列表

        Raises:
            ValueError: 如果 `element` 不在 `lst` 中，则抛出 ValueError（与 list.index 一致）。

        Examples:
            >>> split_list([1, 2, 0, 3], 0)
            [[1, 2], [3]]

        Notes:
            - 函数只在第一次出现的 `element` 处分割；如果需要对所有匹配位置进行分割，请在调用方实现相应逻辑。
            - 返回值始终为长度为 2 的列表；如果分割元素位于首位或末位，则对应子列表会为空。
        """
    index = lst.index(element)
    return [lst[:index], lst[index + 1:]]


def start_and_end_week(weeks: str) -> Union[Tuple[int, int], List[List[int]]]:
    """
    解析周次字符串，返回开始与结束周信息

    简要说明：
        从像 "1-18([周])[01-02节]" 或 "4-5,8-18([周])[03-04节]" 这样的周次字符串中
        提取出起始周与结束周信息。本函数会处理三种主要模式：
            - 单个周（例如 "13"），返回 (13, 13)
            - 连续区间（例如 "3-8"），返回 (3, 8)
            - 多个区间或单周用逗号分隔（例如 "4-5,8-18"），返回 [[4,8], [5,18]]（两个列表分别为 start_list 和 end_list）

    Args:
        weeks (str): 含有周次的字符串，函数会在第一个 "(" 之前截断并解析。

    Returns:
        Union[Tuple[int, int], List[List[int]]]:
            - 当输入为单个区间或单周时，返回 (start_week, end_week) 的元组（int, int）。
            - 当输入为多个区间/单周（逗号分隔）时，返回 [start_list, end_list]，两项均为 int 列表，
              分别表示每个片段的开始周与结束周；调用方可以使用 zip(*result) 来遍历每个区间。

    Raises:
        ValueError: 当字符串中包含无法解析的数字格式时，int() 转换可能抛出 ValueError。

    Examples:
        >>> start_and_end_week('1-18([周])[01-02节]')
        (1, 18)
        >>> start_and_end_week('4-5,8-18([周])[03-04节]')
        [[4, 8], [5, 18]]

    Notes:
        - 函数会在第一次出现的 '(' 处截断输入（以忽略 '[周]' 等后缀）。
        - 返回类型不定（tuple 或 list），调用方应根据返回值类型进行分支处理。
    """
    weeks = weeks.split('(')[0]

    # 如果有 ',' ，则为“单-多”，或“多-多”
    # 例如：
    #   '3,5-18' 或 '4-5,8-18'
    #   则返回两个列表：
    #   [[3,3],[5,18]] 或 [[4,5],[8,18]]
    if ',' in weeks:
        start_week_results = []
        end_week_results = []
        weeks_list = weeks.split(',')
        for w in weeks_list:
            if '-' not in w:
                start_week_results.append(int(w.strip()))
                end_week_results.append(int(w.strip()))
            else:
                start_week, end_week = map(int, w.split('-'))
                start_week_results.append(start_week)
                end_week_results.append(end_week)

        return [start_week_results, end_week_results]

    # 如果只有 '-' ，则为“多”
    # 例如：
    #   '3-8'
    #   则返回一个元组(3,8)
    elif '-' in weeks and ',' not in weeks:
        start_week = int(weeks.split('-')[0])
        end_week = int(weeks.split('-')[1])
        return start_week, end_week

    # 如果没有链接符号，则为“单”
    # 例如：
    #   '3'
    #   则返回一个元组(3,3)
    else:
        start_week = end_week = int(weeks)
        return start_week, end_week


def get_info(lines: List[str], default_class_and_grade: str = "") -> List[Tuple[str, str, str, str, List[int], str]]:
    """
    提取课程信息

    简要说明：
        从表示单个格子的字符串列表中解析出课程信息并返回元组列表。

    Args:
        lines (List[str]): 表示单个格子的字符串项列表。常见项按顺序为：
            - 课程名
            - 班级名（可能省略或用括号包裹）
            - 教师名
            - 周次原始字符串（例如 '1-18([周])[01-02节]'）
            - 地点
            对于同一格包含多门课的情况，`lines` 会包含多个按课程顺序重复的字段，中间以空字符串 `''` 分隔。
        default_class_and_grade (str): 当 `lines` 中未包含班级名时使用的默认班级与年级字符串（例如教学班名），默认为空字符串。

    Returns:
        List[Tuple[str, str, str, str, List[int], str]]: 返回一个元组列表，每个元组的含义为：
            - 课程名 (str)
            - 班级名 (str)
            - 教师 (str)
            - 周次原始字符串 (str)
            - 节次列表，例如 [1, 2] (List[int])
            - 地点 (str)
    """
    if not lines:
        return []

    course = lines[0]

    # 如果 len(lst) < 5 ，则使用全局班级名，即为本教学班课程
    # 例如：['软件工程', '周老师', '1-18([周])[01-02节]', 'C-5-222']
    if len(lines) < 5:
        class_name = default_class_and_grade
        teacher = lines[1]
        times = lines[2]
        numbers = list(map(int, re.findall(r'\d+', lines[2].split("[")[-1].split("]")[0])))
        location = lines[3]
        return [(course, class_name, teacher, times, numbers, location)]

    # 如果 len(lst) == 5 ，则可在列表中直接提取出班级名
    # 例如：['体育俱乐部 I', '(器械健身大一1班)', '肖老师', '4-5,8-18([周])[03-04节]', '体能中心']
    if len(lines) == 5:
        class_name = lines[1][1:-1]
        teacher = lines[2]
        times = lines[3]
        numbers = list(map(int, re.findall(r'\d+', lines[3].split("[")[-1].split("]")[0])))
        location = lines[4]
        return [(course, class_name, teacher, times, numbers, location)]

    # 如果 len(lst) > 5 ，则说明这个节次有不同的课，需要把不同的课程分开
    # 例如：['形势与政策1', '(25级集成[1-4]班,25级交通[1-2]班,25级龙芯英才班)', '胥老师', '13([周])[13-14节]', 'C-5-106（录播教室）', '',
    #       '形势与政策1', '(25级集成[1-4]班,25级交通[1-2]班,25级龙芯英才班)', '钟老师', '14([周])[13-14节]', 'C-5-106（录播教室）', '',
    #       '形势与政策1', '(25级集成[1-4]班,25级交通[1-2]班,25级龙芯英才班)', '邵老师', '15([周])[13-14节]', 'C-5-106（录播教室）', '',
    #       '形势与政策1', '(25级集成[1-4]班,25级交通[1-2]班,25级龙芯英才班)', '李老师', '16([周])[13-14节]', 'C-5-106（录播教室）']
    # 通过 split_list 函数将不同的课程分开以''分开，再逐一按照上述过程分析
    ls2 = split_list(lines, '')
    results = []
    for l in ls2:
        results.extend(get_info(l, default_class_and_grade))
    return results
