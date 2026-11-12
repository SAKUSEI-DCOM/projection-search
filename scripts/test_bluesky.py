import unittest
from collect_bluesky import parse_posts

class TestBluesky(unittest.TestCase):
    def test_post_and_repost(self):
        p={'feed':[{'post':{'uri':'at://did:plc:abc/app.bsky.feed.post/xyz','author':{'handle':'sample.bsky.social','did':'did:plc:abc'},'record':{'text':'明日12時から配信します','createdAt':'2026-11-12T10:00:00Z'}}},{'reason':{'$type':'app.bsky.feed.defs#reasonRepost'},'post':{'uri':'at://did:plc:abc/app.bsky.feed.post/other','author':{'handle':'sample.bsky.social','did':'did:plc:abc'},'record':{'text':'配信','createdAt':'2026-11-12T10:00:00Z'}}}]}
        rows=parse_posts(p,'sample.bsky.social','sample_x',True,'2026-11-12T10:00:00Z')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['author'],'sample_x')
        self.assertTrue(rows[0]['url'].endswith('/post/xyz'))
    def test_unverified_not_published(self):
        p={'feed':[{'post':{'uri':'at://did:plc:abc/app.bsky.feed.post/xyz','author':{'handle':'sample.bsky.social','did':'did:plc:abc'},'record':{'text':'配信 2026年11月15日20時','createdAt':'2026-11-12T10:00:00Z'}}}]}
        self.assertEqual(parse_posts(p,'sample.bsky.social','sample_x',False,'now')[0]['author'],'')
    def test_wrong_author_ignored(self):
        p={'feed':[{'post':{'uri':'at://did:plc:abc/app.bsky.feed.post/xyz','author':{'handle':'other.bsky.social','did':'did:plc:abc'},'record':{'text':'配信','createdAt':'2026-11-12T10:00:00Z'}}}]}
        self.assertEqual(parse_posts(p,'sample.bsky.social','sample_x',True,'now'),[])
