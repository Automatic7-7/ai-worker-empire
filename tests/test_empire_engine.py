import unittest
from empire_engine import build_status, PROPOSALS

class EmpireEngineTests(unittest.TestCase):
    def test_unique_proposals(self):
        self.assertEqual(len({p['id'] for p in PROPOSALS}), len(PROPOSALS))

    def test_no_auto_deploy(self):
        self.assertFalse(build_status()['development']['auto_deployment_enabled'])

    def test_owner_controls(self):
        policy = build_status()['approval_policy']
        for key in ('new_code_deployment', 'outreach', 'spending', 'contracts', 'permission_changes'):
            self.assertEqual(policy[key], 'owner')

    def test_all_candidates_unapproved(self):
        self.assertTrue(all(p['approval'] == 'not granted' for p in build_status()['proposals']))

if __name__ == '__main__':
    unittest.main()
