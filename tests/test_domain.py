import copy
import unittest
from app import domain
from app.service import load_study


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.data = load_study()
        self.request = {'operation': 'contrast', 'component': 'practice', 'level_a': 'guided', 'level_b': 'independent'}

    def test_repeated_outcome_does_not_increase_count(self):
        data = copy.deepcopy(self.data)
        before = domain.baseline(data)
        data['outcomes'].append(copy.deepcopy(data['outcomes'][0]))
        self.assertEqual(before, domain.baseline(data))

    def test_conflicting_outcome_is_not_selected(self):
        data = copy.deepcopy(self.data)
        record = copy.deepcopy(data['outcomes'][0])
        record['result'] += 1
        data['outcomes'].append(record)
        with self.assertRaises(ValueError):
            domain.baseline(data)

    def test_raw_difference_is_explicitly_descriptive(self):
        result = domain.act(self.data, self.request)
        self.assertEqual(result['kind'], 'raw_difference')
        self.assertEqual(sum(result['counts'].values()), len(self.data['assignments']))


if __name__ == '__main__':
    unittest.main()
