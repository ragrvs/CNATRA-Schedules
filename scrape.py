import firebase
import cnatra

squadron_dates_to_check = firebase.get_squadron_dates_missing_schedules()
for squadron in squadron_dates_to_check:
    squadron_id = squadron['squadron_id']
    dates = squadron['dates']
    new_schedules = cnatra.get_squadron_schedule_data_for_dates(squadron_id, dates)
    if new_schedules:
        firebase.record_schuedules_for_squadron(squadron_id, new_schedules)
    #TODO logging
