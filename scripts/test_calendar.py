import unittest
from collect_calendars import parse_ics, date_iso

class CalendarTests(unittest.TestCase):
    def test_ics(self):
        events=list(parse_ics('BEGIN:VCALENDAR\nBEGIN:VEVENT\nUID:abc\nDTSTART:20261113T120000Z\nSUMMARY:配信\nSTATUS:CANCELLED\nEND:VEVENT\nEND:VCALENDAR'))
        self.assertEqual(events[0]['STATUS'],'CANCELLED')
        self.assertEqual(date_iso(events[0]['DTSTART']),'2026-11-13T21:00:00+09:00')
    def test_invalid(self):
        self.assertIsNone(date_iso('2026/11/13'))
if __name__=='__main__':unittest.main()
