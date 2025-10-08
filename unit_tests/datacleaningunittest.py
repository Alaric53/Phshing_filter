import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datacleaning import datacleaning


clean = datacleaning()

#clean.cleanfile("testingdata.txt")
#cleaned_text, emails, domains, urls, ips = clean.cleantext("Hello! Contact me at test@example.com or visit https://192.168.1.2:8080/page." )
#print(cleaned_text)
# print(emails)
# print(ips)
#print(urls)


class TestDataCleaning(unittest.TestCase):
    def test_ips(self):
        #test strings with valid ips and ports
        input_text = "input text here192.168.12.1:8080...192.168.12.2 or 192.168.12.2...http://192.168.1.100:443/banking/login."
        cleaned_text, emails, domains, urls, ips = clean.cleantext(input_text)
        expected_cleaned_text = "input text"
        expected_emails = []
        expected_domains = []
        expected_urls = ["http://192.168.1.100:443/banking/login"]
        expected_ips = ["192.168.12.1:8080","192.168.12.2","192.168.1.100:443"]
        

        self.assertEqual(cleaned_text, expected_cleaned_text)
        self.assertCountEqual(emails, expected_emails)
        self.assertCountEqual(domains, expected_domains)
        self.assertCountEqual(urls, expected_urls)
        self.assertCountEqual(ips, expected_ips)

    def test_emails(self):
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

    def test_urls(self):
        #test strings with valid URLS
        input_text = "my website is https://www.notscam.com!!!https://www.NOTscam.com AND sitewww.sub.domain.co.uk/test!!!! and http://site.org/path?key=value&token=abc123.. and http://bit.ly/abc123."
        cleaned_text, emails, domains, urls, ips = clean.cleantext(input_text)
        expected_cleaned_text = "websit site"
        expected_emails = []
        expected_domains = []
        expected_urls = ["https://www.notscam.com","www.sub.domain.co.uk/test","http://site.org/path?key=value&token=abc123","http://bit.ly/abc123"]
        expected_ips = []

        self.assertEqual(cleaned_text, expected_cleaned_text)
        self.assertCountEqual(emails, expected_emails)
        self.assertCountEqual(domains, expected_domains)
        self.assertCountEqual(urls, expected_urls)
        self.assertCountEqual(ips, expected_ips)

    def test_invalid_formats(self):
        # Test strings that are not valid emails, URLs, or IPs
        input_text = "test@.com @invalid.com this is not an email. Also 999.999.999.999. A fake URL: htts://fake.com Invalid IP: 192.168.1.256"
        cleaned_text, emails, domains, urls, ips = clean.cleantext(input_text)
        
        # Expected output should not contain any of the invalid formats
        expected_cleaned_text = "testcom invalidcom email also 999999999999 fake url httsfakecom invalid ip 1921681256"
        expected_emails = []
        expected_domains = []
        expected_urls = []
        expected_ips = []

        self.assertEqual(cleaned_text, expected_cleaned_text)
        self.assertCountEqual(emails, expected_emails)
        self.assertCountEqual(domains, expected_domains)
        self.assertCountEqual(urls, expected_urls)
        self.assertCountEqual(ips, expected_ips)

    def test_empty(self):
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

    def test_invalidfile(self):
        #cleanfile function ensures that the file provided exists
        output = clean.cleanfile("testingdatas.txt")
        self.assertEqual(output,"File does not exist")

    def test_invalidlabel(self):
        '''
        consists of 1 valid input and 1 invalid input
        No	Contact Me Now to Make $100 Today!
        wrongheader     this is invalid	
        '''
        output = clean.cleanfile("invalid.txt")
        self.assertEqual(output,"Saved 1 rows to cleaned_invalid.csv")
if __name__ == '__main__':
    unittest.main()
