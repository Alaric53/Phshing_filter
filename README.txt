PHISHING EMAIL DETECTION SYSTEM
================================
Programming Fundamentals - Group P9-7
AY 2025/26 Trimester 1

SYSTEM REQUIREMENTS
-------------------
- Python 3.8 or higher
- Windows/Mac/Linux OS
- 500MB free disk space
- Internet connection (for initial setup)

INSTALLATION INSTRUCTIONS
-------------------------
1. Clone or download the project files to your local machine

2. Navigate to the project directory:
   cd Phishing_filter

3. Create a virtual environment:
   python -m venv venv

4. Activate the virtual environment:
   - Windows: venv\Scripts\activate
   - Mac/Linux: source venv/bin/activate

5. Install required dependencies:
   pip install Flask==2.3.3 Werkzeug==2.3.7 PyPDF2==3.0.1 pdfplumber==0.9.0 beautifulsoup4==4.12.2 extract-msg==0.41.1 pandas==2.0.3 scikit-learn==1.6.0 nltk==3.8.1 joblib regex

6. Download NLTK data:
   python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"

RUNNING THE APPLICATION
-----------------------
1. Ensure virtual environment is activated (see step 4 above)

2. Start the application:
   python app.py

3. Open your web browser and navigate to:
   http://localhost:5000

4. The ML processor (Main.py) will start automatically in the background

USAGE
-----
1. Web Interface:
   - Paste suspicious email text into the input field
   - Click "Load Sample Phishing Email" to test with example
   - Click "Analyze Email Security" to process
   - View risk score, level, and recommendations

2. API Endpoints (for developers):
   - POST /api/process - Simple text processing
   - POST /api/process_detailed - Detailed analysis with metadata
   - GET /api/get_latest_with_risk - Get latest analysis results
   - GET /stats - View performance statistics

FILE STRUCTURE
--------------
Phishing_filter/
├── app.py                 # Flask web application
├── Main.py               # ML processing controller
├── datacleaning.py       # Data preprocessing module
├── ml_processor.py       # Machine learning analysis
├── ml_train.py          # Model training script
├── ruleset.py           # Rule-based detection
├── text_processor.py    # Email text processing
├── model/               # Trained ML models
├── templates/           # HTML templates
├── static/              # CSS and JavaScript
├── cleaned_data/        # Processed datasets
├── testdata/            # Test datasets
└── unit_tests/          # Unit test files

TESTING
-------
Run unit tests:
   python -m unittest discover unit_tests/

TROUBLESHOOTING
---------------
1. If dependencies fail to install:
   - Ensure pip is updated: pip install --upgrade pip
   - Try installing individually: pip install [package_name]

2. If NLTK data download fails:
   - Run Python interpreter: python
   - Import NLTK: import nltk
   - Download manually: nltk.download('stopwords')

3. Port already in use error:
   - Change port in app.py: app.run(port=5001)
   - Or kill existing process using port 5000

4. Model not found error:
   - Run training script first: python ml_train.py
   - Ensure model/ directory exists

SUPPORT
-------
For issues or questions, contact team members:
- Aurelius Ng: 2500612@sit.singaporetech.edu.sg
- Alaric Teo: 2500366@sit.singaporetech.edu.sg
- Reuben Hoh: 2501748@sit.singaporetech.edu.sg
- Wong Yong Quan: 2500377@sit.singaporetech.edu.sg
- Kessler Tan: 2502114@sit.singaporetech.edu.sg

VERSION
-------
Version 1.0 - December 2024
