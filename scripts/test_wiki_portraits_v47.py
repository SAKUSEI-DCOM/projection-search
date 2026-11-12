import unittest
from sync_wiki_portraits import extract
BASE='https://wikiwiki.jp/projecti0n/A'
class TestV47(unittest.TestCase):
 def test_lazy_image(self):
  self.assertEqual(extract('<img alt="立ち絵" src="data:image/gif;base64,AAA" data-src="https://cdn.wikiwiki.jp/portrait.png">',BASE),['https://cdn.wikiwiki.jp/portrait.png'])
 def test_figure_caption(self):
  self.assertEqual(extract('<figure><img src="https://wikiwiki.jp/projecti0n/p.png"><figcaption>全身立ち絵</figcaption></figure>',BASE),['https://wikiwiki.jp/projecti0n/p.png'])
 def test_no_arbitrary_image(self):
  self.assertEqual(extract('<img src="https://wikiwiki.jp/projecti0n/p.png">',BASE),[])
 def test_external_image_rejected(self):
  self.assertEqual(extract('<img alt="立ち絵" src="https://example.com/p.png">',BASE),[])
 def test_tracking_image_rejected(self):
  self.assertEqual(extract('<img alt="立ち絵" src="https://wikiwiki.jp/projecti0n/banner.png">',BASE),[])
if __name__=='__main__':unittest.main()
