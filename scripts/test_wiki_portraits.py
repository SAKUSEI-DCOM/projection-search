import unittest
from sync_wiki_portraits import extract
class TestPortraits(unittest.TestCase):
 def test_explicit(self):
  html='<img alt="立ち絵" src="https://wikiwiki.jp/projecti0n/image.png">'
  self.assertEqual(extract(html,'https://wikiwiki.jp/projecti0n/A'),['https://wikiwiki.jp/projecti0n/image.png'])
 def test_unrelated(self):
  self.assertEqual(extract('<img src="https://wikiwiki.jp/projecti0n/ad.png" alt="広告">','https://wikiwiki.jp/projecti0n/A'),[])
 def test_external(self):
  self.assertEqual(extract('<img src="https://evil.test/portrait.png" alt="立ち絵">','https://wikiwiki.jp/projecti0n/A'),[])
if __name__=='__main__':unittest.main()
