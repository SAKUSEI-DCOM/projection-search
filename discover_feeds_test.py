import unittest,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).parent/'scripts'))
from discover_feeds import extract
class FeedDiscoveryTest(unittest.TestCase):
 def test_feed_and_calendar(self):
  a=extract('<a href="https://example.org/feed.xml">RSS</a><a href="https://example.org/live.ics">予定</a>','https://wikiwiki.jp/projecti0n/a')
  self.assertEqual(len(a),2)
  self.assertEqual({x['kind'] for x in a},{'feed','calendar'})
 def test_ignore_x_and_unrelated(self):
  a=extract('<a href="https://x.com/a">RSS</a><a href="https://example.org/about">RSS</a>','https://wikiwiki.jp/projecti0n/a')
  self.assertEqual(a,[])
if __name__=='__main__':unittest.main()
