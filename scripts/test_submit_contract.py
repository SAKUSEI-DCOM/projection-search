import pathlib,re,unittest
from collect_github_issues import extract
from process_inbox import valid
ROOT=pathlib.Path(__file__).resolve().parents[1]
class SubmitContract(unittest.TestCase):
 def test_issue_template_labels_match_parser(self):
  template=(ROOT/'.github/ISSUE_TEMPLATE/stream.yml').read_text(encoding='utf8')
  for label in ['X投稿URL','Xユーザー名（@なし）','投稿日時（ISO 8601・タイムゾーン付き）','投稿本文']:
   self.assertIn('label: '+label,template)
  sample='### X投稿URL\n\nhttps://x.com/example/status/12345\n\n### Xユーザー名（@なし）\n\nexample\n\n### 投稿日時（ISO 8601・タイムゾーン付き）\n\n2026-11-12T20:00:00+09:00\n\n### 投稿本文\n\n明日12時から配信'
  self.assertTrue(valid(extract(sample)))
 def test_submit_uses_issue_template_not_incompatible_plain_issue(self):
  page=(ROOT/'submit.html').read_text(encoding='utf8')
  self.assertIn('issues/new?template=stream.yml',page)
  self.assertNotIn('new URLSearchParams({title:',page)
if __name__=='__main__':unittest.main()
