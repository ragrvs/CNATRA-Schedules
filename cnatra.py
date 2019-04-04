import requests
from lxml import html

def _get_base_state_values_for_squadron(squadron_id):
    pass

def _get_state_for_date(squadron_id, date, base_state):
    pass

def _get_schedule_html_for_date(squadron_id, date, date_state):
    pass

def _parse_schedule_data(html_string):
    pass

def get_squadron_schedule_data_for_dates(squadron_id, dates):
    base_state = _get_base_state_values_for_squadron(squadron_id)

    schedules = {}

    for date in dates:
        date_state = _get_state_for_date(squadron_id, date, base_state)
        schedule_html = _get_schedule_html_for_date(squadron_id, date, date_state)
        schedule_data = _parse_schedule_data(schedule_html)
        if schedule_data:
            schedules[date] = schedule_data

    return schedules