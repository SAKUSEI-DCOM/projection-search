import unittest
from hourly_monitor import handle,report
class TestHourlyMonitor(unittest.TestCase):
 def test_url(self):
  self.assertEqual(handle('https://x.com/Example_1'),'example_1')
  self.assertEqual(handle('https://twitter.com/Example_1/'),'example_1')
  self.assertIsNone(handle('https://x.com/a/status/123'))
  self.assertIsNone(handle('https://evil.com/a'))
 def test_no_false_monitoring(self):
  x=report([{'name':'A','x':'https://x.com/a'}],{'handles':['a']},{'feeds':[]},{'api_configured':False}, {})
  self.assertFalse(x['x_monitoring_active'])
  self.assertEqual(x['profiles_with_x_url'],1)
