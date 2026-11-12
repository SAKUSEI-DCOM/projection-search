import unittest
from sync_wiki_x_links import extract,x_profile
class WikiLinksTest(unittest.TestCase):
 def test_parse(self):
  html='<p><a href="/projecti0n/A">A</a> / <a href="https://x.com/test_A">■X</a> / <a href="https://web.iriam.app/x">IRIAM</a></p>'
  got,amb=extract(html,{'A'});self.assertEqual(got,{'A':'https://x.com/test_A'});self.assertFalse(amb)
 def test_invalid(self):
  self.assertEqual(x_profile('https://x.com/i'), '')
  self.assertEqual(x_profile('https://evil.com/foo'), '')
 def test_ambiguous(self):
  html='<p><a href="/projecti0n/A">A</a><a href="https://x.com/a1">X</a><a href="https://x.com/a2">X</a></p>'
  got,amb=extract(html,{'A'});self.assertFalse(got);self.assertIn('A',amb)
if __name__=='__main__':unittest.main()
