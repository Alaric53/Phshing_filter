import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from ruleset import calculator
from Main import combined_score

class TestScoring(unittest.TestCase):
    #Testing for calculator first one normal input expecting low score
    def test_calculator_safe_domain_no_keywords(self):
        sender = "user@dbs.com.sg"
        subject = "Monthly statement"
        body = "Here is your regular monthly bank statement."
        urlIP = ""
        score, keywords = calculator(sender, subject, body, urlIP)
        self.assertIsInstance(score, float)
        self.assertIsInstance(keywords, int)
        self.assertLessEqual(score, 10.0) 

    #check for high score
    def test_calculator_high_keyword_and_ip(self):
        sender = "fraud@evil.com"
        subject = "URGENT! WIN big money now"
        body = "Click to claim your FREE prize. Transfer funds now."
        urlIP = "192.168.22.22, 209.122.28.10"
        score, keywords = calculator(sender, subject, body, urlIP)
        self.assertGreater(score, 50.0)
        self.assertGreaterEqual(keywords, 1)

    #check for empty inputs
    def test_calculator_empty_inputs(self):
        score, keywords = calculator("", "", "", "")
        self.assertEqual(score, 0.0)
        self.assertEqual(keywords, 0)

    #testing for combined score
    def test_combined_score_safe(self):
        risk, level = combined_score(0, 0)
        self.assertEqual(risk, 0.0)
        self.assertEqual(level, "SAFE")

    #check for level = correct danger level
    def test_combined_score_low_medium_high(self):
        risk, level = combined_score(20, 0.10)
        self.assertEqual(level, "Low danger")

        risk, level = combined_score(80, 0.20)
        self.assertEqual(level, "Medium danger")

        risk, level = combined_score(90, 0.90)
        self.assertEqual(level, "High danger")

    #Empty input
    def test_combined_score_missing_values(self):   
        risk, level = combined_score(None, None)
        self.assertEqual(risk, 0.0)
        self.assertEqual(level, "SAFE")


if __name__ == "__main__":
    unittest.main()
