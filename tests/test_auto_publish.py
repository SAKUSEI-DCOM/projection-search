import unittest,sys,pathlib,datetime
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from auto_publish import extract,JST
class DateTests(unittest.TestCase):
 def test_tomorrow(self):
  self.assertEqual(extract('明日12時からIRIAM配信','2026-11-12T20:00:00+09:00',now=datetime.datetime(2026,11,12,20,tzinfo=JST)),'2026-11-13T12:00:00+09:00')
 def test_no_anchor(self):self.assertIsNone(extract('明日12時から配信',now=datetime.datetime(2026,11,12,tzinfo=JST)))
 def test_invalid(self):self.assertIsNone(extract('2026年11月31日12時から配信',now=datetime.datetime(2026,11,12,tzinfo=JST)))
if __name__=='__main__':unittest.main()
