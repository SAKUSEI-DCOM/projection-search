import unittest,datetime
from auto_publish import reconcile,JST

class CrossPostCancelTests(unittest.TestCase):
 def setUp(self):
  self.livers=[{'name':'テスト','x':'https://x.com/testuser'}]
  self.now=datetime.datetime(2026,11,12,tzinfo=JST)
 def row(self,text,id,author='testuser'):
  return {'title':text,'excerpt':'','author':author,'url':'https://x.com/'+author+'/status/'+id,'published_at':'2026-11-12T09:00:00+09:00'}
 def test_separate_post_cancels_exact_matching_time(self):
  s,e,_=reconcile([self.row('明日12時から配信','1')],self.livers,[],[],self.now)
  s,e,r=reconcile([self.row('明日12時の配信中止','2')],self.livers,s,e,self.now)
  self.assertEqual((len(s),r['auto_cancelled']), (0,1))
 def test_out_of_order_posts_are_chronological(self):
  old=self.row('明日12時から配信','1');old['published_at']='2026-11-12T09:00:00+09:00'
  new=self.row('明日12時の配信中止','2');new['published_at']='2026-11-12T10:00:00+09:00'
  s,e,r=reconcile([new,old],self.livers,[],[],self.now)
  self.assertEqual((len(s),r['auto_cancelled']), (0,1))
 def test_different_time_does_not_cancel(self):
  s,e,_=reconcile([self.row('明日12時から配信','1')],self.livers,[],[],self.now)
  s,e,r=reconcile([self.row('明日13時の配信中止','2')],self.livers,s,e,self.now)
  self.assertEqual((len(s),r['auto_cancelled']), (1,0))
 def test_vague_cancellation_requires_review(self):
  s,e,_=reconcile([self.row('明日12時から配信','1')],self.livers,[],[],self.now)
  s,e,r=reconcile([self.row('明日の配信中止','2')],self.livers,s,e,self.now)
  self.assertEqual((len(s),r['cancellations_needing_review']), (1,1))
 def test_other_author_cannot_cancel(self):
  s,e,_=reconcile([self.row('明日12時から配信','1')],self.livers,[],[],self.now)
  s,e,r=reconcile([self.row('明日12時の配信中止','2','stranger')],self.livers,s,e,self.now)
  self.assertEqual((len(s),r['auto_cancelled']), (1,0))
 def test_manual_record_is_untouched(self):
  s=[{'id':'manual','name':'テスト','start':'2026-11-13T12:00:00+09:00','auto_imported':False}]
  s,e,r=reconcile([self.row('明日12時の配信中止','2')],self.livers,s,[],self.now)
  self.assertEqual((len(s),r['auto_cancelled']), (1,0))
if __name__=='__main__':unittest.main()
