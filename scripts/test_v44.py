import unittest
from sync_wiki_portraits import extract
class TestV44(unittest.TestCase):
 def test_portrait_label(self):
  html='<img alt="立ち絵" src="https://wikiwiki.jp/img/portrait.png">'
  self.assertEqual(len(extract(html,'https://wikiwiki.jp/projecti0n/A')),1)
 def test_unlabelled(self):
  self.assertEqual(extract('<img src="https://wikiwiki.jp/img/p.png">','https://wikiwiki.jp/projecti0n/A'),[])
if __name__=='__main__':unittest.main()
