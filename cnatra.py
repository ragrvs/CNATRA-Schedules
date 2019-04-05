"""
This module handles interaction with the schedule pages located at https://www.cnatra.navy.mil/scheds/schedule_data.aspx?sq=<squadron id>

In order to get the schedule data for each squadron and day, we use HTTP requests that exactly mimic a user navigating to the page using the UI.
Each request in this chain uses POST data (application/x-form-urlencoded) from the previous page to get the next one.
All requests have, at a minimum, these form values: '__VIEWSTATE', '__VIEWSTATEGENERATOR', and '__EVENTVALIDATION'. In this module, we refer to these values collectively as a page's 'state' or 'state values'.
These state values come from hidden input tags with corresponding ids.
Additionally:
    A) Requests that result from clicking on a date in the date picker widget have these form values:
        a) '__EVENTTARGET'. This is always set to 'ctrlCalendar' for requests that change dates (by clicking a date in the widget).
        b) '__EVENTARGUMENT' This is set to the number of data between January 1, 2000 and the date picked on the calendar widget.
    B) Requests that result from clicking the 'View Schedule' button always have a form value param 'btnViewSched', which is set to 'View Schedule'.
The algorithm for scraping schedule date for all requested days is this:
    1) We first get a squadron's 'base page', meaning the page in its raw state as though a user had typed the squadron's page URL into a browser, and get the state values from that page.
    2) For each requested date:
        A) We 'click the date picker' by requesting the squadron's page and sending form data that includes and '__EVENTTARGET' of 'ctrlCalendar' and an '__EVENTARGUMENT' of the date number for that date.
        B) We get the state values for that page, and use that state the requests the schedule for that date by passing in the state form data and an additional form param of 'btnViewSched' = 'View Schedule'
        C) Then we scrape the data off of the resulting HTML page and return the data as a list of dictionaries, or a single 'None' value if the schedule is not yet published for a given date.
"""

import requests
from lxml import html
from datetime  import datetime
import re

FONT_RE = re.compile(r'</?font.*?>')
BR_RE = re.compile(r'<br>')
BASE_URL = 'https://www.cnatra.navy.mil/scheds/schedule_data.aspx?sq='

DATE_FORMAT = '%Y-%m-%d'
ZERO_DATE = datetime.strptime('2000-01-01', DATE_FORMAT)

def _date_string_to_date_number(date_string: str) -> str:
    """
    Gets the "date number" for the given date string.
    "date number" is defined as the number of days between January 1, 2000 and the given date string.

    Args:
        date_string: The date you want to convert to a number, in the format 'YYYY-MM-DD'
    Returns:
        The number of days between January 1, 2000 and the given date string
    """
    date = datetime.strptime(date_string, DATE_FORMAT)
    return str((date - ZERO_DATE).days)

def _get_front_page_url(squadron_id: str, date_string: str) -> str:
    """
    Gets the URL of the 'front page' PDF for a given squadron and date.

    Args:
        squadron_id: A squadron id
        date_string: A date, in the format 'YYYY-MM-DD'
    Returns:
        The URL to the 'front page' PDF for the squadron and day.
    """
    sid = squadron_id.upper()
    ds = date_string.upper()
    return 'https://www.cnatra.navy.mil/scheds/tw1/SQ-{}/!{}!{}!Frontpage.pdf'.format(sid, ds, sid)

def _get_state_values_from_html(html_string: str) -> dict:
    """
    Gets the state values from an HTML string.

    Args:
        html_string: An HTML string, representing the code for a schedule page.
    Returns:
        A dictionary with the keys '__VIEWSTATE', '__VIEWSTATEGENERATOR', and '__EVENTVALIDATION'.
    """
    html_tree = html.fromstring(html_string)
    view_state = html_tree.cssselect('#__VIEWSTATE')[0].get('value')
    view_state_generator = html_tree.cssselect('#__VIEWSTATEGENERATOR')[0].get('value')
    event_validation = html_tree.cssselect('#__EVENTVALIDATION')[0].get('value')
    return {
        '__VIEWSTATE': view_state,
        '__VIEWSTATEGENERATOR': view_state_generator,
        '__EVENTVALIDATION': event_validation
    }

def _get_page_html(url: str, data: dict=None, headers: dict=None) -> str:
    """
    Get the html for a given URL and data params.

    Args:
        url: The web URL to fetch the page from.
        data: The data payload. This data will be used as 'application/x-form-url-encoded' data passed with the request. The dict should, if present, should have these keys: '__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION'
    Returns:
        The HTML returned from the request.
    """
    response = requests.post(url, data=data, headers=headers) # TODO use a connection pool (single threading it like this is monumentally inefficient)
    content = response.content
    decoded = content.decode('utf-8') #TODO this is an assumption. we should probably get the charset header and use that
    return decoded

def _get_base_state_values_for_squadron(squadron_url: str) -> dict:
    """
    Gets the state values from squadron's schedule page in its base state, i.e. the state that results from a request to the page that did not include any form data.
    We are simulating typing the URL into the browser and hitting enter.

    Args:
        squadron_url: The URL to a squadron's schedule page.
    Returns:
        A dictionary with the keys '__VIEWSTATE', '__VIEWSTATEGENERATOR', and '__EVENTVALIDATION'.
    """
    html_string = _get_page_html(squadron_url)
    state = _get_state_values_from_html(html_string)
    return state

def _get_state_for_date(squadron_url: str, date_number: str, base_state: dict) -> dict:
    """
    Gets the state values for a page where the calendar widget is set to the given date.
    We simulate navigating there from the squadron's base schedule page by passing in the state values that came from the base schedule page.

    Args:
        squadron_url: The URL for a squadron's schedule page.
        date_number: The date whose page state you want.
        base_state: The state values for the squadron's base schedule page.
    Returns:
        The state values from the page, as though we navigated there by clicking a date on the calendar widget.
    """
    state = base_state.copy()#don't mutate the original
    state['__EVENTTARGET'] = 'ctrlCalendar'
    state['__EVENTARGUMENT'] = date_number
    html_string = _get_page_html(squadron_url, state)
    date_state = _get_state_values_from_html(html_string)
    return date_state

def _get_schedule_html_for_date(squadron_url: str, date_state: str) -> str:
    """
    Gets the HTML from a squadron's schedule page for a given day.
    We are simulating clicking the "View Schedule" page, having previously click on a date in the date widget.

    Args:
        squadron_url: The URL to a squadron's schedule page.
        date_state: The state values from the date picker page.
    Returns:
        The HTML code for the squadron's schedule page for the given date.
    """
    state = date_state.copy()# don't mutate the original
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    state['btnViewSched'] = 'View Schedule'
    html_string = _get_page_html(squadron_url, state, headers=headers)
    return html_string

def _parse_schedule_data(html_string: str) -> dict:
    """
    Gets the schedule data from a schedule page.

    Args:
        html_string: The HTML for a schedule page for a given squadron and date.
    Returns:
        A dictionary with two keys. 'notes' is the test from a page's 'SQUADRON NOTES' section. 'events' is a list of events scheduled for the day.
    """
    tree = html.fromstring(html_string)
    error_message_elements = tree.cssselect('p.messageL')
    if len(error_message_elements): # no schedule data on this page
        return None
    schedule_data = {}
    notes_table_elements = tree.cssselect('table#dgCoversheet')
    if len(notes_table_elements): # because it's possible it there's no "squadron notes" on a page
        innermost_notes_element = notes_table_elements[0].cssselect('td font')[0]
        notes = html.tostring(innermost_notes_element).decode('utf-8')
        notes_without_font_tags = FONT_RE.sub('', notes)
        notes_with_newlines = BR_RE.sub('\n', notes_without_font_tags)
        schedule_data['notes'] = notes_with_newlines
    # TODO parse data from events table
    return schedule_data

def get_squadron_schedule_data_for_dates(squadron_id: str, dates: list) -> dict:
    """
    Gets the schedule data for a squadron for a list of specified dates.

    Args:
        squadron_id: The squadron whose schedules we will retrieve.
        dates: The dates to get the squadron's schedules for.
    Returns:
        The schedules for the specified squadron and days. The keys in this dictionary are date strings. The values are a dictionary containg notes, front page URL, and events for the date.
        Note, if a schedule has not yet been published for a requested data, the returned dictionary will not have a key for that data. (Instead of specifying a key for the date, and the value being 'None')
    """
    squadron_url = BASE_URL + squadron_id
    base_state = _get_base_state_values_for_squadron(squadron_url)
    schedules = {}
    for date_string in dates:
        date_number = _date_string_to_date_number(date_string)
        date_state = _get_state_for_date(squadron_url, date_number, base_state)
        schedule_html = _get_schedule_html_for_date(squadron_url, date_state)
        schedule_data = _parse_schedule_data(schedule_html)
        if schedule_data:
            schedule_data['frontPageUrl'] = _get_front_page_url(squadron_id, date_string)
            schedules[date_string] = schedule_data

    return schedules #TODO if there are no new schedules, return None
