import requests
from lxml import html

BASE_URL = 'https://www.cnatra.navy.mil/scheds/schedule_data.aspx?sq='

#TODO if we object-orient this, can we multi-thread the whole thing

def _date_string_to_date_number(date_string):
    #TODO implement
    return "7030"

def _get_front_page_url(squadron_id, date_string):
    #TODO implement
    return 'https://www.cnatra.navy.mil/scheds/tw1/SQ-VT-7/!2019-04-03!VT-7!Frontpage.pdf'

def _get_state_values_from_html(html_string):
    html_tree = html.fromstring(html_string)
    view_state = html_tree.cssselect('#__VIEWSTATE')[0].get('value')
    view_state_generator = html_tree.cssselect('#__VIEWSTATEGENERATOR')[0].get('value')
    event_validation = html_tree.cssselect('#__EVENTVALIDATION')[0].get('value')
    return {
        '__VIEWSTATE': view_state,
        '__VIEWSTATEGENERATOR': view_state_generator,
        '__EVENTVALIDATION': event_validation
    }

def _get_page_html(url, data=None):
    response = requests.post(url, data=data) # TODO use a connection pool (single threading it like this is monumentally inefficient)
    content = response.content
    decoded = content.decode('utf-8') #TODO this is an assumption. we should probably get the charset header and use that
    return decoded

def _get_base_state_values_for_squadron(squadron_url):
    html_string = _get_page_html(squadron_url)
    state = _get_state_values_from_html(html_string)
    return state

def _get_state_for_date(squadron_url, date_number, base_state):
    state = base_state.copy()#don't mutate the original
    state['__EVENTTARGET'] = 'ctrlCalendar'
    state['__EVENTARGUMENT'] = date_number
    html_string = _get_page_html(squadron_url, state)
    date_state = _get_state_values_from_html(html_string)
    return date_state

def _get_schedule_html_for_date(squadron_url, date_state):
    state = date_state.copy()# don't mutate the original
    state['btnViewSched'] = 'View Scedule'
    html_string = _get_page_html(squadron_url, date_state)
    return html_string

def _parse_schedule_data(html_string):
    #TODO implement this
    return {
        'notes': 'foo',
        'events': [

        ]
    }

def get_squadron_schedule_data_for_dates(squadron_id, dates):
    squadron_url = BASE_URL + squadron_id
    base_state = _get_base_state_values_for_squadron(squadron_url)

    schedules = {}

    for date_string in dates:
        date_number = _date_string_to_date_number(date_string)
        date_state = _get_state_for_date(squadron_url, date_number, base_state)
        schedule_html = _get_schedule_html_for_date(squadron_url, date_state)
        schedule_data = _parse_schedule_data(schedule_html)
        schedule_data['frontPageUrl'] = _get_front_page_url(squadron_id, date_string)
        if schedule_data:
            schedules[date_string] = schedule_data

    return schedules #TODO if there are no new schedules, return None

#########################################
# WORKING CODE FROM BEFORE THE REFACTOR #
#########################################
# PAGE_URL = 'https://www.cnatra.navy.mil/scheds/schedule_data.aspx?sq=vt-9'
#
# def get_data_from_page(url, data = None, headers = None):
#     response = requests.post(url, data=data, headers=headers)
#     return response.text
#
# def get_state_from_html_tree(html_tree):
#     view_state = html_tree.cssselect('#__VIEWSTATE')[0].get('value')
#     view_state_generator = html_tree.cssselect('#__VIEWSTATEGENERATOR')[0].get('value')
#     event_validation = html_tree.cssselect('#__EVENTVALIDATION')[0].get('value')
#     return {
#         '__VIEWSTATE': view_state,
#         '__VIEWSTATEGENERATOR': view_state_generator,
#         '__EVENTVALIDATION': event_validation
#     }
#
# # get base state values from main page
# initial_page_html = get_data_from_page(PAGE_URL)
# initial_state = get_state_from_html_tree(html.fromstring(initial_page_html))
#
# # switch to Monday, April 1, 2019
# initial_state_with_calendar_change = initial_state.copy()
# initial_state_with_calendar_change['__EVENTTARGET'] = 'ctrlCalendar'
# initial_state_with_calendar_change['__EVENTARGUMENT'] = '7030'
# specific_day_page_html = get_data_from_page(PAGE_URL, data=initial_state_with_calendar_change)
# specific_day_state = get_state_from_html_tree(html.fromstring(specific_day_page_html))
#
# # get data for the day
# day_state_with_schedule_request = specific_day_state.copy()
# day_state_with_schedule_request['btnViewSched'] = 'View Schedule'
# day_with_schedule_html = get_data_from_page(PAGE_URL, day_state_with_schedule_request)