import unittest, pathlib, sys, tempfile
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import build_source_coverage as coverage
class V49Tests(unittest.TestCase):
 def test_api_token_does_not_imply_success(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp); (root/'data').mkdir(); (root/'livers.json').write_text('[]')
   with patch.object(coverage,'ROOT',root),patch.dict('os.environ',{'X_BEARER_TOKEN':'dummy'},clear=True):
    result=coverage.build()
   self.assertTrue(result['x_api_credentials_configured'])
   self.assertFalse(result['x_posts_automatically_available'])
 def test_full_audit_workflow_present(self):
  wf=(pathlib.Path(__file__).resolve().parents[1]/'.github/workflows/wiki-full-audit.yml').read_text()
  self.assertIn('WIKI_PROFILE_BATCH',wf)
  self.assertIn('WIKI_PORTRAIT_BATCH',wf)
if __name__=='__main__':unittest.main()
