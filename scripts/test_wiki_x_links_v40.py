import unittest
from sync_wiki_x_links import extract, x_profile

class WikiLinkV40Tests(unittest.TestCase):
    def test_table_row(self):
        html = '<table><tr><td><a href="/projecti0n/A">A</a></td><td><a href="https://x.com/a_live">X</a></td></tr></table>'
        self.assertEqual(extract(html, {'A'})[0], {'A': 'https://x.com/a_live'})
    def test_separate_rows(self):
        html = '<table><tr><td><a href="/projecti0n/A">A</a></td></tr><tr><td><a href="https://x.com/wrong">X</a></td></tr></table>'
        self.assertEqual(extract(html, {'A'})[0], {})
    def test_next_person_boundary(self):
        html = '<p><a href="/projecti0n/A">A</a><a href="/projecti0n/B">B</a><a href="https://x.com/b_live">X</a></p>'
        self.assertEqual(extract(html, {'A', 'B'})[0], {'B': 'https://x.com/b_live'})
    def test_status_link_not_profile(self):
        self.assertEqual(x_profile('https://x.com/name/status/123'), '')
    def test_query_profile(self):
        self.assertEqual(x_profile('https://twitter.com/name?ref=wiki'), 'https://x.com/name')
    def test_conflicting_links(self):
        html = '<p><a href="/projecti0n/A">A</a><a href="https://x.com/one">X</a><a href="https://x.com/two">X</a></p>'
        self.assertIn('A', extract(html, {'A'})[1])

if __name__ == '__main__': unittest.main()
