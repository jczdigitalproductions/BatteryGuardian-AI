import unittest
from batteryguardian.core import parse_csv, analyze

HEADER = 'timestamp,voltage_v,current_a,temperature_c,soc_pct\n'

class CoreTests(unittest.TestCase):
    def test_normal(self):
        result = analyze(parse_csv(HEADER + 't1,48,2,25,80\n'))
        self.assertEqual(result['status'], 'normal')
        self.assertEqual(result['event_count'], 0)

    def test_critical(self):
        result = analyze(parse_csv(HEADER + 't1,48,2,25,80\nt2,47,2,61,70\n'))
        self.assertEqual(result['status'], 'critical')
        self.assertEqual(result['event_count'], 1)

    def test_voltage_drop(self):
        result = analyze(parse_csv(HEADER + 't1,50,2,25,80\nt2,40,2,25,80\n'))
        self.assertEqual(result['status'], 'warning')

    def test_reject_nan(self):
        with self.assertRaises(ValueError):
            parse_csv(HEADER + 't1,nan,2,25,80\n')

    def test_reject_empty(self):
        with self.assertRaises(ValueError):
            parse_csv(HEADER)

    def test_reject_missing_columns(self):
        with self.assertRaises(ValueError):
            parse_csv('temperature_c\n25\n')

if __name__ == '__main__': unittest.main()
