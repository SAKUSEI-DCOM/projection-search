import unittest,sys,pathlib,tempfile,json
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import sync_wiki_portraits as portraits
import build_source_coverage as coverage
class V48Tests(unittest.TestCase):
 def test_table_label_detected(self):
  html='<table><tr><td>立ち絵<img src="https://wikiwiki.jp/attach/a.png"></td></tr></table>'
  self.assertEqual(portraits.extract(html,'https://wikiwiki.jp/projecti0n/a'),['https://wikiwiki.jp/attach/a.png'])
 def test_unlabelled_image_rejected(self):
  self.assertEqual(portraits.extract('<img src="https://wikiwiki.jp/attach/a.png">','https://wikiwiki.jp/projecti0n/a'),[])
 def test_external_image_rejected(self):
  self.assertEqual(portraits.extract('<img alt="立ち絵" src="https://elsewhere.example/a.png">','https://wikiwiki.jp/projecti0n/a'),[])
 def test_coverage_without_credentials(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'data').mkdir();(root/'livers.json').write_text('[{"name":"A","x":"https://x.com/a"}]')
   with patch.object(coverage,'ROOT',root),patch.dict('os.environ',{},clear=True):
    result=coverage.build()
   self.assertEqual(result['x_profile_links'],1)
   self.assertFalse(result['x_posts_automatically_available'])
if __name__=='__main__':unittest.main()
