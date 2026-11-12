import unittest
from collect_github_issues import accepted,extract
from process_inbox import valid
class Tests(unittest.TestCase):
 def test_trusted(self):
  base={'author_association':'OWNER','labels':[{'name':'配信告知'}],'state':'open'}
  self.assertFalse(accepted(base))
  self.assertFalse(accepted({**base,'author_association':'NONE'}))
  self.assertTrue(accepted({**base,'author_association':'NONE','labels':[{'name':'配信告知'},{'name':'掲載承認'}]}))
  self.assertFalse(accepted({**base,'author_association':'NONE','labels':[{'name':'掲載承認'}]}))
  self.assertFalse(accepted({**base,'state':'closed'}))
  self.assertFalse(accepted({**base,'pull_request':{}}))
 def test_form(self):
  body='### X投稿URL\n\nhttps://x.com/example/status/12345\n\n### Xユーザー名（@なし）\n\nexample\n\n### 投稿日時（ISO 8601・タイムゾーン付き）\n\n2026-11-12T20:00:00+09:00\n\n### 投稿本文\n\n明日12時から配信'
  self.assertIsNotNone(valid(extract(body)))
if __name__=='__main__':unittest.main()
