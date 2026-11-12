import unittest,datetime
from auto_publish import reconcile,JST
class ReconcileTests(unittest.TestCase):
 def setUp(self):
  self.livers=[{'name':'テスト','x':'https://x.com/testuser'}]
  self.now=datetime.datetime(2026,11,12,tzinfo=JST)
 def row(self,text):
  return {'title':text,'excerpt':'','author':'testuser','url':'https://x.com/testuser/status/123','published_at':'2026-11-12T09:00:00+09:00'}
 def test_update_without_duplicate(self):
  s,e,r=reconcile([self.row('明日12時配信')],self.livers,[],[],self.now)
  self.assertEqual(r['auto_added'],1)
  s,e,r=reconcile([self.row('明日13時配信')],self.livers,s,e,self.now)
  self.assertEqual((len(s),r['auto_updated']), (1,1))
  self.assertIn('13:00',s[0]['start'])
 def test_cancel_only_automatic(self):
  s,e,_=reconcile([self.row('明日12時配信')],self.livers,[],[],self.now)
  s.append({'id':'manual','source_url':'https://x.com/testuser/status/123','auto_imported':False})
  s,e,r=reconcile([self.row('明日の配信中止')],self.livers,s,e,self.now)
  self.assertEqual((len(s),r['auto_cancelled']), (1,1))
  self.assertEqual(s[0]['id'],'manual')
 def test_idempotent(self):
  s,e,_=reconcile([self.row('明日12時配信')],self.livers,[],[],self.now)
  s,e,r=reconcile([self.row('明日12時配信')],self.livers,s,e,self.now)
  self.assertEqual((r['auto_added'],r['auto_updated']), (0,0))
 def test_no_unverified_author(self):
  row=self.row('明日12時配信');row['author']='stranger'
  s,e,r=reconcile([row],self.livers,[],[],self.now)
  self.assertEqual(len(s),0)
if __name__=='__main__':unittest.main()
