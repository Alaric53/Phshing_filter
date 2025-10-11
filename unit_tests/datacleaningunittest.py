import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datacleaning import datacleaning


clean = datacleaning()

#MUST RUN IN /Phishing_filter folder
class TestDataCleaning(unittest.TestCase):
    def test_ips(self):
        print("\n--- Running test_ips ---")
        #test strings with valid ips and ports
        input_text = "input text here192.168.12.1:8080...192.168.12.2 or 192.168.12.2...http://192.168.1.100:443/banking/login."
        cleaned_text, emails, domains, urls, ips = clean.cleantext(input_text)
        expected_cleaned_text = "input text"
        expected_emails = []
        expected_domains = ['192.168.1.100:443']
        expected_urls = ["http://192.168.1.100:443/banking/login"]
        expected_ips = ["192.168.12.1:8080","192.168.12.2","192.168.1.100:443"]
        

        self.assertEqual(cleaned_text, expected_cleaned_text)
        self.assertCountEqual(emails, expected_emails)
        self.assertCountEqual(domains, expected_domains)
        self.assertCountEqual(urls, expected_urls)
        self.assertCountEqual(ips, expected_ips)
        print("✓ test_ips passed")

    def test_emails(self):
        print("\n--- Running test_emails ---")
        #test strings with valid emails
        input_text = "my email is 1002@outlook.com!!!1002@outlook.com or also support@g00gle.com..."
        cleaned_text, emails, domains, urls, ips = clean.cleantext(input_text)
        expected_cleaned_text = "email also"
        expected_emails = ["1002@outlook.com","support@g00gle.com"]
        expected_domains = ["outlook.com","g00gle.com"]
        expected_urls = []
        expected_ips = []
        self.assertEqual(cleaned_text, expected_cleaned_text)
        self.assertCountEqual(emails, expected_emails)
        self.assertCountEqual(domains, expected_domains)
        self.assertCountEqual(urls, expected_urls)
        self.assertCountEqual(ips, expected_ips)
        print("✓ test_emails passed")

    def test_urls(self):
        print("\n--- Running test_urls ---")
        #Checks for any http/https address, www.domains.com and domains.com
        #if it does not have https or www, domains.{valid tld} has to be found
        input_text = "my website is https://www.scam.com AND www.sub.domain.co.uk/test https://www.scam.com and http://site.org/path?key=value&token=abc123... and http://bit.ly/abc123 google.com"
        cleaned_text, emails, domains, urls, ips = clean.cleantext(input_text)
        expected_cleaned_text = "websit"
        expected_emails = []
        expected_domains = ['sub.domain.co.uk', 'site.org', 'bit.ly', 'scam.com', 'google.com']
        expected_urls = ["https://www.scam.com","www.sub.domain.co.uk/test","http://site.org/path?key=value&token=abc123","http://bit.ly/abc123", "google.com"]
        expected_ips = []

        self.assertEqual(cleaned_text, expected_cleaned_text)
        self.assertCountEqual(emails, expected_emails)
        self.assertCountEqual(domains, expected_domains)
        self.assertCountEqual(urls, expected_urls)
        self.assertCountEqual(ips, expected_ips)
        print("✓ test_urls passed")

    def test_invalid_formats(self):
        print("\n--- Running test_invalid_formats ---1 valid line 2 invalid lines")
        # Test strings that are not valid emails, URLs, or IPs exceeding 255
        input_text = "test@.com @invalid.com this is not an email. Also 999.999.999.999. A fake URL: fake.invalidtld Invalid IP: 192.168.1.256"
        cleaned_text, emails, domains, urls, ips = clean.cleantext(input_text)
        
        # Expected output should not contain any of the invalid formats
        expected_cleaned_text = "testcom invalidcom email also 999999999999 fake url fakeinvalidtld invalid ip 1921681256"
        expected_emails = []
        expected_domains = []
        expected_urls = []
        expected_ips = []

        self.assertEqual(cleaned_text, expected_cleaned_text)
        self.assertCountEqual(emails, expected_emails)
        self.assertCountEqual(domains, expected_domains)
        self.assertCountEqual(urls, expected_urls)
        self.assertCountEqual(ips, expected_ips)
        print("✓ test_invalid_formats passed")

    def test_emptytext(self):
        print("\n--- Running test_emptytext ---")
        #test empty input
        input_text = ""
        cleaned_text, emails, domains, urls, ips = clean.cleantext(input_text)
        
        expected_cleaned_text = ""
        expected_emails = []
        expected_domains = []
        expected_urls = []
        expected_ips = []
        
        self.assertEqual(cleaned_text, expected_cleaned_text)
        self.assertCountEqual(emails, expected_emails)
        self.assertCountEqual(domains, expected_domains)
        self.assertCountEqual(urls, expected_urls)
        self.assertCountEqual(ips, expected_ips)
        print("✓ test_emptytext passed")

    def test_missingfile(self):
        print("\n--- Running test_missingfile ---")
        #cleanfile function ensures that the file provided exists
        output = clean.cleanfile("missing.txt")
        self.assertEqual(output,"File does not exist")
        print("✓ test_missingfile passed")

    def test_invalidfile(self):
        print("\n--- Running test_invalidfile ---")
        '''
        consists of 1 valid input, an empty line, and 1 invalid input
        No	Contact Me Now to Make $100 Today!
        wrongheader     this is invalid	
        '''
        output = clean.cleanfile("invalid.txt")
        self.assertEqual(output,"Saved 1 rows to cleaned_invalid.csv")
        print("✓ test_invalidfile passed")

    def test_emptyfile(self):
        print("\n--- Running test_emptyfile ---")
        #cleanfile function ensures that the file provided exists
        output = clean.cleanfile("empty.txt")
        self.assertEqual(output,"Saved 0 rows to cleaned_empty.csv")
        print("✓ test_emptyfile passed")

if __name__ == '__main__':
    unittest.main()