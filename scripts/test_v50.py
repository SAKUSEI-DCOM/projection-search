import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import sync_wiki_portraits as m

class TestApprovedImageAudit(unittest.TestCase):
    def test_approved_image_change_is_reported_without_overwriting(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); data=root/'data';data.mkdir()
            roster=[{'id':'1','name':'Alice','wiki':'https://wikiwiki.jp/projecti0n/Alice',
                     'image':'https://wikiwiki.jp/projecti0n/old.png',
                     'portrait_status':'wiki_embed_approved_by_operator'}]
            (root/'livers.json').write_text(json.dumps(roster),encoding='utf-8')
            paths={'ROSTER':root/'livers.json','REPORT':data/'report.json','STATE':data/'cursor.json',
                   'REGISTRY':data/'registry.json','APPROVALS':data/'approvals.json'}
            with patch.multiple(m,**paths):
                report=m.run(fetch=lambda url:'<img alt="立ち絵" src="https://wikiwiki.jp/projecti0n/new.png">',batch_size=1)
                saved=json.loads(paths['ROSTER'].read_text())
            self.assertEqual(saved[0]['image'],roster[0]['image'])
            self.assertEqual(report['previously_approved_changed'],['Alice'])
            self.assertEqual(report['checked'],1)
    def test_empty_roster_is_safe(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);data=root/'data';data.mkdir()
            (root/'livers.json').write_text('[]',encoding='utf-8')
            paths={'ROSTER':root/'livers.json','REPORT':data/'report.json','STATE':data/'cursor.json',
                   'REGISTRY':data/'registry.json','APPROVALS':data/'approvals.json'}
            with patch.multiple(m,**paths):
                report=m.run(batch_size=200)
            self.assertEqual(report['checked'],0)

if __name__=='__main__':unittest.main()
