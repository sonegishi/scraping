from datetime import datetime, timedelta
import os
import re
from typing import Dict, List

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

_DEPAUW_URL = 'https://my.depauw.edu'
_SOC_VIEW_URL = f'{_DEPAUW_URL}/e/reg/soc-view/'

_DICT_CLASSIFICATIONS = {
    'FR': 'Freshman',
    'SO': 'Sophomore',
    'JR': 'Junior',
    'SR': 'Senior'
}

_DICT_CLASSIFICATION_NUMBERS = {
    1: 'Freshman',
    2: 'Sophomore',
    3: 'Junior',
    4: 'Senior'
}

_DICT_DAYS = {
    'M': 'Monday',
    'T': 'Tuesday',
    'W': 'Wednesday',
    'R': 'Thursday',
    'F': 'Friday',
    'S': 'Saturday'
}

_DICT_RESTRICTION_DESCRIPTIONS = {
    '+': 'Not offered pass/fail',
    '@': 'Examinations given at night',
    '*': 'Confer with instructor no later than the second day of classes',
    '~': 'Internships are graded S (Satisfactory) or U (Unsatisfactory)',
    '$': 'Additional fees associated with this class will be charged to your tuition account.  Check with the department for the exact amount.',
    '[': 'Will be a competence course pending instructor completing appropriate competence workshop.',
    'S-P': 'SPAC required'
}

_DICT_COURSE_PRIORITY_LEVELS = {
    0: 'Excludes students from the class',
    1: 'Have first access to the class',
    2: 'Have access to the class only after all students fitting priority 1 have had a chance to enroll'
}

_HOME_DIRECTORY = os.path.expanduser('~')
_CHROME_DRIVER_PATH = os.path.join(_HOME_DIRECTORY, 'chromedriver')


def _int_validation(value) -> int:
    if value == '' or value is None:
        return None
    else:
        return int(value)


def _float_validation(value) -> float:
    if value == '' or value is None:
        return None
    else:
        return float(value)


def _string_validation(value) -> str:
    if value == '' or value is None:
        return None
    else:
        return value.strip()


class Course(object):
    def __init__(self, soc_number, department, course, description, credit, method, schedule, area, competency, interdisciplinary_program, pass_fail, enrolled, capacity, instructor, room, restrictions, priorities, book_link) -> None:
        self._soc_number = _int_validation(soc_number)
        self._department = _string_validation(department)
        self._course = _string_validation(course)
        self._description = description
        self._credit = _float_validation(credit)
        self._method = method
        self._schedule = schedule
        self._area = _string_validation(area)
        self._competency = _string_validation(competency)
        self._interdisciplinary_program = _string_validation(interdisciplinary_program)
        self._pass_fail = pass_fail
        self._enrolled = _int_validation(enrolled)
        self._capacity = _int_validation(capacity)
        self._instructor = _string_validation(instructor)
        self._room = _string_validation(room)
        self._restrictions = restrictions
        self._priorities = priorities
        self._book_link = _string_validation(book_link)
        self._lab = None

    @property
    def lab(self) -> object:
        return self._lab

    @lab.setter
    def lab(self, value) -> None:
        self._lab = value

    def __str__(self) -> str:
        return self.detailed_string()

    def __repr__(self) -> str:
        return self.detailed_string()

    def detailed_string(self) -> str:
        return ('Course(\n'
                f'\tSoc#: {self._soc_number},\n'
                f'\tDept: {self._department},\n'
                f'\tCrse: {self._course},\n'
                f'\tDescription: {self._description},\n'
                f'\tCredit: {self._credit},\n'
                f'\tMethod: {self._method},\n'
                f'\tSchedule: {self._schedule},\n'
                f'\tArea: {self._area},\n'
                f'\tCmp: {self._competency},\n'
                f'\tIP: {self._interdisciplinary_program},\n'
                f'\tP/F: {self._pass_fail},\n'
                f'\tEnr: {self._enrolled},\n'
                f'\tEnrCap: {self._capacity},\n'
                f'\tInstr: {self._instructor},\n'
                f'\tRm: {self._room},\n'
                f'\tRestrictions: {self._restrictions},\n'
                f'\tPriorities: {self._priorities},\n'
                f'\tBooks: {self._book_link},\n'
                f'\tLaboratory: {self._lab}\n'
                ')')


class Lab(object):
    def __init__(self, course, description, schedule, room) -> None:
        self._course = _string_validation(course)
        self._description = description
        self._schedule = schedule
        self._room = _string_validation(room)

    def __str__(self) -> str:
        return self.detailed_string()

    def __repr__(self) -> str:
        return self.detailed_string()

    def detailed_string(self) -> str:
        return ('Lab(\n'
                f'\tCrse: {self._course},\n'
                f'\tDescription: {self._description},\n'
                f'\tSchedule: {self._schedule},\n'
                f'\tRoom: {self._room}\n'
                ')')


def _organize_schedules(str_time_days) -> dict:
    list_time_days = str_time_days.split()

    start_time = None
    end_time = None
    days = None

    if len(list_time_days) == 1:
        start_time = None
        end_time = None
        days = []
    elif len(list_time_days) == 2:
        list_time = list_time_days[0].split('-')
        start_time = datetime.strptime(list_time[0], '%H:%M').time()
        if start_time < datetime.strptime('7:00', '%H:%M').time():
            start_time \
                = (datetime.strptime(list_time[0], '%H:%M') + timedelta(hours=12)).time()
        end_time = datetime.strptime(list_time[1], '%H:%M').time()
        if end_time < datetime.strptime('7:00', '%H:%M').time():
            end_time \
                = (datetime.strptime(list_time[1], '%H:%M') + timedelta(hours=12)).time()
        days = list(list_time_days[1])
    elif len(list_time_days) == 3:
        list_time = list_time_days[0].split('-')
        am_pm = list_time_days[1]
        days = list(list_time_days[2])

        if am_pm == 'PM':
            start_time \
                = (datetime.strptime(list_time[0], '%H:%M') + timedelta(hours=12)).time()
            end_time \
                = (datetime.strptime(list_time[1], '%H:%M') + timedelta(hours=12)).time()
        else:
            raise NotImplementedError(f'Error in _organize_schedules: {am_pm}')
    else:
        raise NotImplementedError(f'Error in _organize_schedules: {list_time_days}')

    dict_schedules = {
        _DICT_DAYS[day]: [{
            'start': start_time,
            'end': end_time
        }]
        for day in days
    }

    return dict_schedules


def _explore_notes(url) -> dict:
    request = requests.get(url)
    bs = BeautifulSoup(request.text, 'html.parser')

    list_tables = bs.find_all('table')

    if len(list_tables) == 0:
        return {}

    target_table = list_tables[2].table

    list_trs = target_table.find_all('tr')
    target_tr = list_trs[1]

    list_tds = target_tr.find_all('td')
    target_td = list_tds[2].font

    list_lines = [line.strip() for line in target_td.prettify().split('\n')]

    dict_course_notes = {}
    for line in list_lines:
        match = re.match(r'^[0-9]+.\s.*$', line)
        key = None
        description = None
        if match:
            key = re.match(r'^[0-9]+', line)
            list_description = re.split(r'([A-Z][^\.!?]*[\.!?])', line)
            description = ''.join(list_description[1:])
            dict_course_notes[key.group()] = description

    return dict_course_notes


def _collect_restrictions(list_restrictions: List[str], soc_number: int, dict_notes: Dict, dict_restrictions: Dict) -> dict:
    for restriction in list_restrictions:
        if restriction == 'Fn:':
            continue
        elif restriction in _DICT_RESTRICTION_DESCRIPTIONS.keys():
            dict_restrictions[restriction] = _DICT_RESTRICTION_DESCRIPTIONS[restriction]
        elif restriction in _DICT_COURSE_PRIORITY_LEVELS.keys():
            dict_restrictions[restriction] = _DICT_COURSE_PRIORITY_LEVELS[restriction]
        elif ',' in restriction:
            list_splitted_restrictions = restriction.split(',')
            for _restriction in list_splitted_restrictions:
                if _restriction.isdigit():
                    dict_restrictions[int(_restriction)] = dict_notes[soc_number][_restriction]
                else:
                    dict_restrictions[int(_restriction)] = True
        elif restriction.isdigit():
            dict_restrictions[int(restriction)] = dict_notes[soc_number][restriction]
        else:
            raise ValueError(restriction)


def _collect_priorities(list_priorities: List[str], dict_priorities: Dict) -> dict:
    for priority in list_priorities:
        list_temp = priority.split('=')

        if list_temp == ['']:
            continue

        priority_key, str_target = list_temp

        list_targets \
            = _organize_priorities(str_target=str_target, dict_final_targets={})

        if isinstance(priority_key, int):
            dict_priorities[int(priority_key)] = list_targets
        else:
            dict_priorities[priority_key] = list_targets


def _organize_priorities(str_target, dict_final_targets={}) -> dict:
    '''Organizes notes.

    Args:
        str_target [str]: Target.
        dict_final_targets [dict]: A dictionary of final targets.
            key [str]: Year.
            value [list]: A list of targets.

    Returns:
        dict_final_targets [dict]: A dictionary of final targets.
            key [str]: Year.
            value [list]: A list of targets.
    '''

    if ';' in str_target:
        for target in str_target.split(';'):
            _organize_priorities(str_target=target, dict_final_targets=dict_final_targets)
    elif ',' in str_target:
        list_str_target_splitted = str_target.split()

        criterion = 'ALL'

        if len(list_str_target_splitted) == 2:
            criterion = list_str_target_splitted[1]

        for target in list_str_target_splitted[0].split(','):
            if _DICT_CLASSIFICATIONS[target] in dict_final_targets:
                dict_final_targets[target].append(criterion)
            else:
                dict_final_targets[target] = [criterion]
    elif 'NEEDS' in str_target:
        year, _, criterion = str_target.split()
        if _DICT_CLASSIFICATIONS[year] in dict_final_targets:
            dict_final_targets[year].append(criterion)
        else:
            dict_final_targets[year] = [criterion]
    elif len(str_target.split()) == 1:
        dict_final_targets[str_target.strip()] = ['ALL']
    elif len(str_target.split()) == 2:
        tmp_year, tmp_criterion = str_target.split()
        if tmp_year in _DICT_CLASSIFICATIONS:
            year, criterion = tmp_year, tmp_criterion
            if _DICT_CLASSIFICATIONS[year] in dict_final_targets:
                dict_final_targets[year].append(criterion)
            else:
                dict_final_targets[year] = [criterion]
        elif tmp_criterion in _DICT_CLASSIFICATIONS:
            year, criterion = tmp_criterion, tmp_year
            if _DICT_CLASSIFICATIONS[year] in dict_final_targets:
                dict_final_targets[year].append(criterion)
            else:
                dict_final_targets[year] = [criterion]
        else:
            raise NotImplementedError(f'ERROR1 in _organize_priorities:\nkey:{tmp_year}, value: {tmp_criterion}')
    elif len(str_target.split()) == 3:
        list_target = str_target.split()
        year, criterion = list_target[0], list_target[1:]
        if _DICT_CLASSIFICATIONS[year] in dict_final_targets:
            dict_final_targets[year].append(criterion)
        else:
            dict_final_targets[year] = [criterion]
    else:
        raise NotImplementedError(f'Error2 in _organize_priorities: {str_target}')

    return dict_final_targets


def entry_point():
    '''Entry point.'''

    driver = webdriver.Chrome(executable_path=_CHROME_DRIVER_PATH)
    # driver.implicitly_wait(10)
    driver.get(_SOC_VIEW_URL)

    try:
        # Move to the course list page
        submit_button = driver.find_element_by_xpath("//input[@name='submit' and @value='Submit']")
        submit_button.click()

        # Get a table with courses listed
        list_tables = driver.find_elements_by_tag_name('table')
        table = list_tables[2]

        # Get a list of courses
        list_trs = table.find_elements_by_tag_name('tr')

        list_courses = []

        for _, tr in enumerate(list_trs[2:]):  # Avoid 2 header lines
            list_tds = tr.find_elements_by_tag_name('td')
            list_contents = [td.text for td in list_tds]

            if tr.get_property('attributes'):
                if list_contents[0] == '':
                    pass
                else:
                    soc_number = list_contents[0]
                    print('soc_number:', soc_number)

                    department_course = list_contents[1]
                    department_abbrev = ' '.join(department_course.split()[:-1])
                    course_abbrev = department_course.split()[-1]

                    description = list_contents[2]
                    credit = list_contents[3]
                    method = list_contents[4]

                    str_time_days = list_contents[5]
                    dict_schedules = _organize_schedules(str_time_days=str_time_days)

                    area = list_contents[6]
                    competency = list_contents[7]
                    interdisciplinary_program = list_contents[8]
                    pass_fail = list_contents[9]

                    list_statuses = list_contents[10].split()
                    enrolled = None
                    capacity = None
                    if len(list_statuses) == 1:
                        list_enrollments = list_statuses[0].split('/')
                        enrolled = list_enrollments[0]
                        capacity = list_enrollments[1]
                    elif len(list_statuses) == 2:
                        list_enrollments = list_statuses[0].split('/')
                        # fill = list_statuses[1]
                        enrolled = list_enrollments[0]
                        capacity = list_enrollments[1]

                    list_instructor_room = list_contents[11].split('\n')
                    instructor = list_instructor_room[0]
                    room = list_instructor_room[1]

                    notes = list_contents[12].split('\n')
                    str_restrictions = notes[0].strip()
                    list_restrictions = str_restrictions.split()
                    if len(notes) < 2:
                        list_priorities = []
                    else:
                        list_priorities = notes[1].strip().split('/')

                    notes_link = None
                    dict_notes = {}
                    try:
                        list_links = tr.find_element_by_link_text(str_restrictions)
                        for link in list_links.get_property('attributes'):
                            if link['nodeName'] == 'href':
                                notes_link = _SOC_VIEW_URL + link['value']
                                dict_notes[soc_number] = _explore_notes(url=notes_link)
                                break
                    except NoSuchElementException:
                        continue

                    dict_restrictions = {}
                    _collect_restrictions(list_restrictions=list_restrictions,
                                          soc_number=soc_number,
                                          dict_notes=dict_notes,
                                          dict_restrictions=dict_restrictions)

                    dict_priorities = {}
                    _collect_priorities(list_priorities=list_priorities, dict_priorities=dict_priorities)

                    book_link = None
                    try:
                        list_links = tr.find_element_by_link_text(department_course)
                        for link in list_links.get_property('attributes'):
                            if link['nodeName'] == 'href':
                                book_link = _DEPAUW_URL + link['value']
                                break
                    except NoSuchElementException:
                        break

                    course = Course(soc_number=soc_number,
                                    department=department_abbrev,
                                    course=course_abbrev,
                                    description=description,
                                    credit=credit,
                                    method=method,
                                    schedule=dict_schedules,
                                    area=area,
                                    competency=competency,
                                    interdisciplinary_program=interdisciplinary_program,
                                    pass_fail=pass_fail,
                                    enrolled=enrolled,
                                    capacity=capacity,
                                    instructor=instructor,
                                    room=room,
                                    restrictions=dict_restrictions,
                                    priorities=dict_priorities,
                                    book_link=book_link)
                    list_courses.append(course)
            else:
                if list_contents == ['']:
                    continue
                else:
                    course = list_contents[1]
                    description = list_contents[2]

                    str_time_days = list_contents[5]
                    dict_schedules = _organize_schedules(str_time_days=str_time_days)

                    room = list_contents[10]

                    if list_courses[-1].lab is None:
                        lab = Lab(course=course,
                                  description=description,
                                  schedule=dict_schedules,
                                  room=room)
                        list_courses[-1].lab = lab
                    else:
                        raise NotImplementedError('Lab already exists.')
    except:
        pass
    else:
        return list_courses
    finally:
        driver.quit()


if __name__ == '__main__':
    '''Local development'''

    entry_point()
