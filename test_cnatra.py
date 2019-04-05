from unittest import TestCase
import cnatra

class Test_cnatra(TestCase):
    def test__date_string_to_date_number(self):
        date_string_1 = '2019-04-04'
        date_string_2 = '2015-06-17'
        date_number_1 = cnatra._date_string_to_date_number(date_string_1)
        date_number_2 = cnatra._date_string_to_date_number(date_string_2)
        self.assertEqual(date_number_1, '7033')
        self.assertEqual(date_number_2, '5646')


    def test__get_front_page_url(self):
        vt7 = 'vt-7'
        vt9 = 'vt-9'
        date_1 = '2021-12-18'
        date_2 = '2002-03-21'
        self.assertEqual(cnatra._get_front_page_url(vt7, date_1), 'https://www.cnatra.navy.mil/scheds/tw1/SQ-VT-7/!2021-12-18!VT-7!Frontpage.pdf')
        self.assertEqual(cnatra._get_front_page_url(vt9, date_2), 'https://www.cnatra.navy.mil/scheds/tw1/SQ-VT-9/!2002-03-21!VT-9!Frontpage.pdf')
