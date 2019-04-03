import requests
from lxml import html

PAGE_URL = 'https://www.cnatra.navy.mil/scheds/schedule_data.aspx?sq=vt-9'

def get_data_from_page(url, data = None, headers = None):
    response = requests.post(url, data=data, headers=headers)
    return response.text

def get_state_from_html_tree(html_tree):
    view_state = html_tree.cssselect('#__VIEWSTATE')[0].get('value')
    view_state_generator = html_tree.cssselect('#__VIEWSTATEGENERATOR')[0].get('value')
    event_validation = html_tree.cssselect('#__EVENTVALIDATION')[0].get('value')
    return {
        '__VIEWSTATE': view_state,
        '__VIEWSTATEGENERATOR': view_state_generator,
        '__EVENTVALIDATION': event_validation
    }

# get base state values from main page
initial_page_html = get_data_from_page(PAGE_URL)
initial_state = get_state_from_html_tree(html.fromstring(initial_page_html))

# switch to Monday, April 1, 2019
initial_state_with_calendar_change = initial_state.copy()
initial_state_with_calendar_change['__EVENTTARGET'] = 'ctrlCalendar'
initial_state_with_calendar_change['__EVENTARGUMENT'] = '7030'
specific_day_page_html = get_data_from_page(PAGE_URL, data=initial_state_with_calendar_change)
specific_day_state = get_state_from_html_tree(html.fromstring(specific_day_page_html))

# get data for the day
day_state_with_schedule_request = specific_day_state.copy()
day_state_with_schedule_request['btnViewSched'] = 'View Schedule'
day_with_schedule_html = get_data_from_page(PAGE_URL, day_state_with_schedule_request)

print(day_with_schedule_html)
