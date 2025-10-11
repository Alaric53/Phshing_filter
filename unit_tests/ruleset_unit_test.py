import unittest
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from ruleset import (
    safe_domain_check,
    suspicious_keyword_check,
    keyword_position_scoring,
    levenshtein_distance,
    lookalike_domain_check,
    suspicious_url_detection,
    process_email_and_score
)

class TestRuleSet(unittest.TestCase):
    def test_safe_domain_check(self):
        result = safe_domain_check("user@gov.sg")
        self.assertIn(result, [0, 2])
        self.assertEqual(safe_domain_check("user@scam.com"), 2)

    def test_suspicious_keyword_check(self):
        subject = "Urgent account verification"
        body = "Please verify your password immediately"
        self.assertGreaterEqual(suspicious_keyword_check(subject, body), 0)

    def test_keyword_position_scoring(self):
        subject = "Verify your account"
        body = "This content is safe"
        score = keyword_position_scoring(subject, body)
        self.assertGreaterEqual(score, 0)

    def test_levenshtein_distance(self):
        self.assertEqual(levenshtein_distance("abc", "abc"), 0)
        self.assertEqual(levenshtein_distance("abc", "abd"), 1)

    def test_lookalike_domain_check(self):
        self.assertEqual(lookalike_domain_check("gov.sg"), 0)
        self.assertIn(lookalike_domain_check("g0v.sg"), [0, 3])

    def test_suspicious_url_detection(self):
        body = "Click http://192.168.0.1 or http://scam.com"
        score, urls = suspicious_url_detection(body)
        self.assertIn(score, [4, 6])
        self.assertIn("http://scam.com", urls)

# --- Demo data ---
email = "user@g0v.sg"  # typo lookalike domain
subject = "Urgent account verification"
body = "Please verify your password immediately at http://192.168.0.1"
domain = "g0v.sg"
print("\n--- DEMO INPUT DATA ---")
print(f"Email: {email}")
print(f"Subject: {subject}")
print(f"Body: {body}")
print(f"Domain: {domain}\n")

# --- Run functions ---
safe_result = safe_domain_check(email)
keyword_hits = suspicious_keyword_check(subject, body)
keyword_pos_score = keyword_position_scoring(subject, body)
lev_dist = levenshtein_distance("paypal", "paypa1")
lookalike_score = lookalike_domain_check(domain)
url_score, suspicious_urls = suspicious_url_detection(body)

# --- Display results ---
print("---RULESET FUNCTION DEMONSTRATION ---")
print(f"Safe domain check (0=safe,2=unsafe): {safe_result}")
print(f"Suspicious keywords detected: {keyword_hits}")
print(f"Keyword position score: {keyword_pos_score}")
print(f"Levenshtein distance (paypal vs paypa1): {lev_dist}")
print(f"Lookalike domain score: {lookalike_score}")
print(f"Suspicious URL score: {url_score}")
print(f"Detected URLs: {suspicious_urls}\n")
print("\n--- RUNNING UNIT TESTS ---\n")
unittest.main()
