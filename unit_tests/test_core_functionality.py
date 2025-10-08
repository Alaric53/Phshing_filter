import sys
import os
import unittest

# Add parent directory to path
CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from text_processor import OptimizedTextProcessor
from app import app, session_data, session_lock


class TestTextProcessorCore(unittest.TestCase):
    """Tests for text_processor.py - Email parsing with phishing indicator preservation"""
    
    def setUp(self):
        self.processor = OptimizedTextProcessor(cache_size=5)
    
    def test_process_text_basic_email(self):
        """Test basic email component extraction"""
        test_email = """Subject: Weekly Meeting
From: manager@company.com
To: team@company.com
Message-ID: <meeting123@company.com>

Please join Friday at 2 PM."""
        
        result = self.processor.process_text(test_email)
        
        self.assertIn("Subject: Weekly Meeting", result)
        self.assertIn("From: manager@company.com", result)
        self.assertIn("Recipients: TO:team@company.com", result)
        self.assertIn("meeting123@company.com", result)
        self.assertIn("---", result)
    
    def test_phishing_indicators_preserved(self):
        """CRITICAL: Verify phishing red flags are NOT removed"""
        phishing_email = """Subject: URGENT: Account Verification
From: security@suspicious-bank.com
Reply-To: collect@different-domain.com

Your account will be suspended in 24 hours.
Click here: http://192.168.1.100/verify"""
        
        result = self.processor.process_text(phishing_email)
        
        # Critical assertions
        self.assertIn("URGENT", result, "Urgent keyword removed!")
        self.assertIn("different-domain.com", result, "Reply-To mismatch removed!")
        self.assertIn("192.168.1.100", result, "IP URL removed!")
        self.assertIn("suspended", result, "Threat language removed!")
    
    def test_caching_functionality(self):
        """Test cache improves performance for duplicate emails"""
        test_email = "Subject: Test\nFrom: test@example.com\n\nBody"
        
        # First call - cache miss
        self.processor.process_text(test_email)
        self.assertEqual(self.processor.stats['cache_misses'], 1)
        
        # Second call - cache hit
        self.processor.process_text(test_email)
        self.assertEqual(self.processor.stats['cache_hits'], 1)
        self.assertEqual(self.processor.stats['total_processed'], 1)


class TestAppWorkflow(unittest.TestCase):
    """Tests for app.py - Session management and workflow"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with session_lock:
            session_data.clear()
    
    def test_form_submission_creates_session(self):
        """Test form submission → session creation → buffer redirect"""
        test_email = "Subject: Test\nFrom: sender@example.com\n\nContent"
        
        response = self.client.post('/process', 
                                   data={'text_input': test_email},
                                   follow_redirects=False)
        
        # Verify redirect
        self.assertEqual(response.status_code, 302)
        self.assertIn('/buffer', response.location)
        
        # Verify session created
        with self.client.session_transaction() as session:
            session_id = session['session_id']
        
        # Verify session data stored
        with session_lock:
            self.assertIn(session_id, session_data)
            self.assertEqual(session_data[session_id]['status'], 'processing')
            self.assertEqual(session_data[session_id]['input_text'], test_email)
    
    def test_buffer_page_requires_session(self):
        """Test buffer page validates session existence"""
        response = self.client.get('/buffer', follow_redirects=True)
        self.assertIn(b'Session expired', response.data)
    
    def test_api_update_results(self):
        """Test external pipeline can update session with results"""
        session_id = 'test-session'
        with session_lock:
            session_data[session_id] = {
                'status': 'processing',
                'input_text': 'test',
                'timestamp': 123456
            }
        
        # Simulate main.py posting results
        result_data = {
            'risk_score': 75,
            'risk_level': 'High danger',
            'sus_keywords': 5
        }
        
        response = self.client.post('/api/update_results', json=result_data)
        self.assertTrue(response.get_json()['success'])
        
        # Verify session updated
        with session_lock:
            self.assertEqual(session_data[session_id]['status'], 'completed')
            self.assertEqual(session_data[session_id]['result']['risk_score'], 75)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestTextProcessorCore))
    suite.addTests(loader.loadTestsFromTestCase(TestAppWorkflow))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*50)
    print(f"Tests: {result.testsRun} | Pass: {result.testsRun - len(result.failures) - len(result.errors)}")
    print("="*50)