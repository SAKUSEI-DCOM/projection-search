import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class V42WorkflowTest(unittest.TestCase):
    def test_profile_sync_executed(self):
        workflow=(ROOT/'.github/workflows/collect.yml').read_text()
        self.assertIn('run: python scripts/sync_wiki_profile_x.py',workflow)
        self.assertLess(workflow.index('run: python scripts/sync_wiki_x_links.py'),workflow.index('run: python scripts/sync_wiki_profile_x.py'))
    def test_state_files_committed(self):
        workflow=(ROOT/'.github/workflows/collect.yml').read_text()
        self.assertIn('data/wiki_profile_cursor.json',workflow)
        self.assertIn('data/wiki_profile_x_report.json',workflow)
    def test_hourly_monitor_has_profile_report(self):
        monitor=(ROOT/'scripts/hourly_monitor.py').read_text()
        self.assertIn('wiki_profile_sync',monitor)
if __name__=='__main__': unittest.main()
