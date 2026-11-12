import unittest
from sync_wiki_profile_x import extract_profile_links

class ProfileXTest(unittest.TestCase):
    def test_single(self):
        self.assertEqual(extract_profile_links('<a href="https://x.com/streamer_1">X</a>'), ['https://x.com/streamer_1'])
    def test_ignores_posts(self):
        self.assertEqual(extract_profile_links('<a href="https://x.com/person/status/123">post</a>'), [])
    def test_duplicates(self):
        self.assertEqual(extract_profile_links('<a href="https://x.com/test">X</a><a href="https://x.com/test">X</a>'), ['https://x.com/test'])
    def test_multiple(self):
        self.assertEqual(len(extract_profile_links('<a href="https://x.com/one">X</a><a href="https://twitter.com/two">X</a>')),2)

if __name__ == '__main__': unittest.main()
