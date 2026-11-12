import datetime,unittest
from auto_publish import extract,JST,reconcile

class ShortDateTests(unittest.TestCase):
 def setUp(self):self.now=datetime.datetime(2026,11,12,tzinfo=JST)
 def test_month_day(self):
  self.assertEqual(extract('11月15日20時から配信','2026-11-12T09:00:00+09:00',self.now),'2026-11-15T20:00:00+09:00')
 def test_new_year_rollover(self):
  self.assertEqual(extract('1月2日 12:30から配信','2026-12-25T09:00:00+09:00',datetime.datetime(2026,12,25,tzinfo=JST)),'2027-01-02T12:30:00+09:00')
 def test_no_publication_timestamp(self):
  self.assertIsNone(extract('11月15日20時から配信','',self.now))
 def test_invalid_date(self):
  self.assertIsNone(extract('11月31日20時から配信','2026-11-12T09:00:00+09:00',self.now))
 def test_end_to_end_new_post_and_cancellation(self):
  liver=[{'name':'テスト','x':'https://x.com/testuser'}]
  base={'author':'testuser','published_at':'2026-11-12T09:00:00+09:00','excerpt':''}
  original={**base,'title':'11月15日20時から配信','url':'https://x.com/testuser/status/1'}
  cancel={**base,'title':'11月15日20時の配信中止','url':'https://x.com/testuser/status/2','published_at':'2026-11-12T10:00:00+09:00'}
  schedules,events,report=reconcile([original],liver,[],[],self.now)
  self.assertEqual(len(schedules),1)
  schedules,events,report=reconcile([original,cancel],liver,schedules,events,self.now)
  self.assertEqual(len(schedules),0)
  self.assertEqual(report['auto_cancelled'],1)
if __name__=='__main__':unittest.main()
