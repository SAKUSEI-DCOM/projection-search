import unittest, tempfile, json
from pathlib import Path
from unittest.mock import patch
import sync_wiki_portraits as m

class TestV46(unittest.TestCase):
 def test_approval_is_specific_and_url_locked(self):
  with tempfile.TemporaryDirectory() as t:
   t=Path(t)
   roster=t/'livers.json'; registry=t/'candidates.json'; state=t/'cursor.json'; report=t/'report.json'; approvals=t/'approvals.json'
   roster.write_text(json.dumps([{'id':'p1','name':'A','wiki':'https://wikiwiki.jp/projecti0n/A','status':'active'}]))
   approvals.write_text(json.dumps({'p1':{'approved':True,'image_url':'https://wikiwiki.jp/projecti0n/portrait.png','source_url':'https://wikiwiki.jp/projecti0n/A','rights_confirmed_by':'operator'}}))
   with patch.multiple(m,ROSTER=roster,REGISTRY=registry,STATE=state,REPORT=report,APPROVALS=approvals):
    result=m.run(fetch=lambda url:'<img alt="立ち絵" src="https://wikiwiki.jp/projecti0n/portrait.png">',batch_size=1)
    self.assertEqual(result['filled'],['A'])
    self.assertEqual(json.loads(roster.read_text())[0]['portrait_status'],'wiki_embed_approved_by_operator')
    roster.write_text(json.dumps([{'id':'p1','name':'A','wiki':'https://wikiwiki.jp/projecti0n/A','status':'active'}]))
    result=m.run(fetch=lambda url:'<img alt="立ち絵" src="https://wikiwiki.jp/projecti0n/different.png">',batch_size=1)
    self.assertEqual(result['filled'],[])
    self.assertEqual(result['approval_mismatches'],['A'])
 def test_workflow_persists_registry(self):
  workflow=(Path(__file__).resolve().parents[1]/'.github/workflows/collect.yml').read_text()
  self.assertIn('git add data/x_query_cursor.json data/wiki_portrait_report.json data/wiki_portrait_candidates.json',workflow)
if __name__=='__main__':unittest.main()
