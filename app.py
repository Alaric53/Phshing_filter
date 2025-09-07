#!/usr/bin/env python3
"""
app.py - Flask Email Processing Web Application
Calls main.py in the backend to get clean plain text output
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

# Ensure we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the main function that returns clean text
try:
    from main import main as get_clean_text
    HANDLER_AVAILABLE = True
    print("✓ Successfully imported main.py")
except ImportError as e:
    print(f"✗ Failed to import main.py: {e}")
    HANDLER_AVAILABLE = False
    
    def get_clean_text(file_path):
        return f"Error: Could not import main.py - {e}"

app = Flask(__name__)
app.secret_key = 'change-this-in-production'

# Configuration
UPLOAD_FOLDER = './instance/temp'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'eml', 'msg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename):
    """Generate unique filename to avoid conflicts."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    name, ext = os.path.splitext(original_filename)
    safe_name = secure_filename(name)
    return f"{timestamp}_{unique_id}_{safe_name}{ext}"


@app.route('/')
def index():
    """Main page with upload form and text input."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and text input - returns clean text via main.py."""
    try:
        # Check if it's a file upload or text input
        if 'file' in request.files and request.files['file'].filename:
            # Handle file upload
            file = request.files['file']
            
            if file and allowed_file(file.filename):
                # Generate unique filename
                unique_filename = generate_unique_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Save the file
                file.save(file_path)
                
                # Debug info
                print(f"File saved: {file_path}")
                print(f"File size: {os.path.getsize(file_path)} bytes")
                print(f"File exists: {os.path.exists(file_path)}")
                
                # Call main.py to get clean text output
                if HANDLER_AVAILABLE:
                    print("Calling main.py for processing...")
                    clean_text = get_clean_text(file_path)
                    print(f"main.py returned {len(clean_text)} characters")
                    print(f"Preview: {clean_text[:100]}...")
                else:
                    clean_text = "Error: EmailInputHandler not available"
                
                flash(f'File "{file.filename}" processed successfully!', 'success')
                return render_template('result.html', 
                                     filename=file.filename,
                                     saved_as=unique_filename,
                                     result=clean_text,
                                     input_type='file')
            else:
                flash('Invalid file type. Please upload .txt, .pdf, .eml, or .msg files.', 'error')
                return redirect(url_for('index'))
        
        elif 'text_input' in request.form and request.form['text_input'].strip():
            # Handle text input
            text_content = request.form['text_input'].strip()
            
            if text_content:
                # Generate unique filename for text file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                txt_filename = f"text_input_{timestamp}_{unique_id}.txt"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
                
                # Save text to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                print(f"Text saved to: {file_path}")
                
                # Call main.py to get clean text output
                if HANDLER_AVAILABLE:
                    print("Calling main.py for text processing...")
                    clean_text = get_clean_text(file_path)
                    print(f"main.py returned {len(clean_text)} characters")
                else:
                    clean_text = "Error: EmailInputHandler not available"
                
                flash('Text input processed successfully!', 'success')
                return render_template('result.html',
                                     filename='Text Input',
                                     saved_as=txt_filename,
                                     result=clean_text,
                                     input_type='text',
                                     original_text=text_content)
            else:
                flash('Please enter some text or select a file.', 'error')
                return redirect(url_for('index'))
        
        else:
            flash('Please select a file or enter text.', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error processing request: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/api/process', methods=['POST'])
def api_process():
    """API endpoint that returns only clean text (like main.py command line)."""
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                unique_filename = generate_unique_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Call main.py and return only the clean text
                clean_text = get_clean_text(file_path)
                return clean_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
            else:
                return "Invalid file type", 400
        
        elif request.is_json and 'text' in request.json:
            text_content = request.json['text']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            txt_filename = f"api_text_{timestamp}_{unique_id}.txt"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            # Call main.py and return only the clean text
            clean_text = get_clean_text(file_path)
            return clean_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
        else:
            return "No file or text provided", 400
    
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint with JSON response (includes metadata)."""
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                unique_filename = generate_unique_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Call main.py to get clean text
                clean_text = get_clean_text(file_path)
                
                return jsonify({
                    'success': True,
                    'filename': file.filename,
                    'saved_as': unique_filename,
                    'result': clean_text,
                    'length': len(clean_text)
                })
            else:
                return jsonify({'success': False, 'error': 'Invalid file type'})
        
        elif request.is_json and 'text' in request.json:
            text_content = request.json['text']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            txt_filename = f"api_text_{timestamp}_{unique_id}.txt"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            clean_text = get_clean_text(file_path)
            
            return jsonify({
                'success': True,
                'filename': 'API Text Input',
                'saved_as': txt_filename,
                'result': clean_text,
                'length': len(clean_text)
            })
        
        else:
            return jsonify({'success': False, 'error': 'No file or text provided'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/files')
def list_files():
    """List all uploaded files."""
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        files.sort(key=lambda x: x['modified'], reverse=True)
        return render_template('files.html', files=files)
    
    except Exception as e:
        flash(f'Error listing files: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/process_and_analyze', methods=['POST'])
def process_and_analyze():
    """Process email and run datacleaning analysis."""
    try:
        # Import datacleaning function
        from datacleaning import datacleaning
        
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            
            if file and allowed_file(file.filename):
                # Save file
                unique_filename = generate_unique_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Get clean text from main.py
                clean_text = get_clean_text(file_path)
                
                if not clean_text:
                    return jsonify({'success': False, 'error': 'No text extracted from file'})
                
                # Run datacleaning analysis
                df, emails, domains, urls = datacleaning(clean_text)
                
                # Convert DataFrame to dict for JSON response
                tfidf_features = df.to_dict('records')[0] if len(df) > 0 else {}
                
                return jsonify({
                    'success': True,
                    'filename': file.filename,
                    'clean_text': clean_text,
                    'analysis': {
                        'emails_found': emails,
                        'domains_found': domains,
                        'urls_found': urls,
                        'tfidf_features': len(tfidf_features),
                        'top_features': dict(sorted(tfidf_features.items(), key=lambda x: x[1], reverse=True)[:10])
                    }
                })
            else:
                return jsonify({'success': False, 'error': 'Invalid file type'})
        
        elif request.is_json and 'text' in request.json:
            text_content = request.json['text']
            
            # Save text to temp file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            txt_filename = f"api_text_{timestamp}_{unique_id}.txt"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            # Process with main.py
            clean_text = get_clean_text(file_path)
            
            # Run datacleaning analysis
            df, emails, domains, urls = datacleaning(clean_text)
            tfidf_features = df.to_dict('records')[0] if len(df) > 0 else {}
            
            return jsonify({
                'success': True,
                'clean_text': clean_text,
                'analysis': {
                    'emails_found': emails,
                    'domains_found': domains,
                    'urls_found': urls,
                    'tfidf_features': len(tfidf_features),
                    'top_features': dict(sorted(tfidf_features.items(), key=lambda x: x[1], reverse=True)[:10])
                }
            })
        
        else:
            return jsonify({'success': False, 'error': 'No file or text provided'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'})


@app.route('/verify_output')
def verify_output():
    """Verify that main.py output matches expectations."""
    try:
        # Test with sample data (similar to your example)
        test_data = """Subject: RE save our soul
From: kabila72b@37.com

Dear friend, I am Mrs. Deborah Kabila, one of the wives of Late President Laurent D. Kabila of Democratic Republic of Congo (DRC). 

Consequent upon the assassination of my husband, I am in possession of USD 58,000,000 (Fifty Eight Million US Dollars Only) being funds earlier earmarked for special projects.

Please contact me for more details.

Best regards,
Deborah Kabila (Mrs.)"""
        
        # Save test data to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_file = os.path.join(app.config['UPLOAD_FOLDER'], f"verify_test_{timestamp}.txt")
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_data)
        
        # Process with main.py (what Flask does)
        main_output = get_clean_text(test_file)
        
        # Clean up
        os.remove(test_file)
        
        # Return HTML response directly (no separate file needed)
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Output Verification</title>
    <style>
        body {{ font-family: monospace; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        .input-box {{ background: #f5f5f5; padding: 15px; border-radius: 5px; border: 1px solid #ddd; }}
        .output-box {{ background: #e8f5e8; padding: 15px; border-radius: 5px; border: 2px solid green; }}
        .nav-links {{ margin-top: 30px; }}
        .nav-links a {{ color: blue; text-decoration: none; margin-right: 20px; }}
        .status {{ color: green; font-weight: bold; }}
        .error {{ color: red; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>main.py Output Verification</h1>
        
        <h2>Input Data:</h2>
        <pre class="input-box">{test_data}</pre>
        
        <h2>main.py Output (what goes to datacleaning.py):</h2>
        <pre class="output-box">{main_output}</pre>
        
        <h2>Analysis:</h2>
        <ul>
            <li><strong>Output Length:</strong> {len(main_output)} characters</li>
            <li><strong>Contains Subject:</strong> <span class="{'status' if 'save our soul' in main_output.lower() else 'error'}">{'Yes' if 'save our soul' in main_output.lower() else 'No'}</span></li>
            <li><strong>Contains Sender:</strong> <span class="{'status' if 'kabila' in main_output.lower() else 'error'}">{'Yes' if 'kabila' in main_output.lower() else 'No'}</span></li>
            <li><strong>Contains Body:</strong> <span class="{'status' if 'deborah' in main_output.lower() else 'error'}">{'Yes' if 'deborah' in main_output.lower() else 'No'}</span></li>
            <li><strong>Clean Format:</strong> <span class="{'status' if main_output and len(main_output.strip()) > 0 else 'error'}">{'Yes' if main_output and len(main_output.strip()) > 0 else 'No'}</span></li>
        </ul>
        
        <div class="status">
            <p><strong>This output can be fed directly into datacleaning.py</strong></p>
        </div>
        
        <div class="nav-links">
            <a href="/">← Back to Upload</a>
            <a href="/test">Run Basic Test</a>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
        
    except Exception as e:
        return f"""
<!DOCTYPE html>
<html>
<head><title>Verification Error</title></head>
<body style="font-family: Arial; padding: 20px;">
    <h1>Verification Failed</h1>
    <p>Error: {str(e)}</p>
    <a href="/">← Back to Upload</a>
</body>
</html>
        """


@app.route('/test')
def test_handler():
    """Test route to verify main.py is working."""
    if not HANDLER_AVAILABLE:
        return """
<!DOCTYPE html>
<html>
<head><title>Test Failed</title></head>
<body style="font-family: Arial; padding: 20px;">
    <h1>Error</h1>
    <p>main.py could not be imported</p>
    <a href="/">← Back to Upload</a>
</body>
</html>
        """
    
    # Test with a simple text
    test_text = "Subject: Test Email\nFrom: test@example.com\nThis is a test message."
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    test_file = os.path.join(app.config['UPLOAD_FOLDER'], f"test_{timestamp}.txt")
    
    try:
        # Create test file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_text)
        
        # Process with main.py
        result = get_clean_text(test_file)
        
        # Clean up
        os.remove(test_file)
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Results</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        .test-box {{ background: #f0f8ff; padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin: 10px 0; }}
        .result-box {{ background: #f0fff0; padding: 15px; border-radius: 5px; border: 1px solid green; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Test Successful</h1>
        
        <h3>Input:</h3>
        <pre class="test-box">{test_text}</pre>
        
        <h3>Output from main.py:</h3>
        <pre class="result-box">{result}</pre>
        
        <p><strong>Length:</strong> {len(result)} characters</p>
        
        <div style="margin-top: 30px;">
            <a href="/" style="color: blue;">← Back to Upload</a>
            <a href="/verify_output" style="color: blue; margin-left: 20px;">Detailed Verification</a>
        </div>
    </div>
</body>
</html>
        """
    
    except Exception as e:
        return f"""
<!DOCTYPE html>
<html>
<head><title>Test Failed</title></head>
<body style="font-family: Arial; padding: 20px;">
    <h1>Test Failed</h1>
    <p>Error: {str(e)}</p>
    <a href="/">← Back to Upload</a>
</body>
</html>
        """


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    print("=" * 60)
    print("Flask Email Processing App")
    print("=" * 60)
    print(f"Working directory: {os.getcwd()}")
    print(f"Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"Supported files: {', '.join(ALLOWED_EXTENSIONS)}")
    print(f"Handler available: {'Yes' if HANDLER_AVAILABLE else 'No'}")
    print("=" * 60)
    print("Web Interface: http://localhost:5000")
    print("Test endpoint: http://localhost:5000/test")
    print("API Endpoints:")
    print("   • POST /api/process  - Returns plain text only")
    print("   • POST /api/upload   - Returns JSON with metadata")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)