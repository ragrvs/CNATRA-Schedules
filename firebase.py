
def record_schuedules_for_squadron(squadron_id, new_schedules):
    #TODO implement this
    pass


def get_squadron_dates_missing_schedules():
    #TODO get this from firebase instead of returning hard-coded values
    return [
        {
            'squadron_id': 'vt-9',
            'dates': [
                '2019-04-03',
                # '2019-04-04',
                # '2019-04-05',
                # '2019-04-06',
                # '2019-04-07',
                # '2019-04-08',
                # '2019-04-09'
            ]
        },
        # {
        #     'squadron_id': 'vt-7',
        #     'dates': [
        #         '2019-04-02',
        #         '2019-04-04',
        #         '2019-04-05',
        #         '2019-04-06',
        #         '2019-04-07',
        #         '2019-04-08',
        #         '2019-04-09'
        #     ]
        # }
    ]