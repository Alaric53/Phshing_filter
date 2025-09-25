from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import time
import json

# Import our email processor
try:
    from text_processor import process_email_text, get_processor
    PROCESSOR_AVAILABLE = True
    print("✓ Email processor loaded successfully")
except ImportError as e:
    print(f"✗ Failed to load email processor: {e}")
    PROCESSOR_AVAILABLE = False
    
    # Create a fake function if the real one failed to load
    def process_email_text(text, debug=False):
        return f"Error: Could not load email processor - {e}"

# Global variable to store the latest processed text for pipeline access
latest_processed_text = ""
latest_risk_analysis = {}  # Store risk analysis results
processing_queue = []  # Queue for multiple texts if needed

def store_processed_text(processed_text: str, original_length: int, processing_time: float):
    """
    Store processed text for external pipeline access.
    This function makes the cleaned text available for other programs via multiple methods.
    """
    global latest_processed_text, processing_queue
    
    # Store the latest processed text globally (for same-process access)
    latest_processed_text = processed_text
    
    # Add to processing queue with metadata
    processing_queue.append({
        'text': processed_text,
        'timestamp': time.perf_counter(),
        'original_length': original_length,
        'processed_length': len(processed_text),
        'processing_time': processing_time
    })
    
    # Keep only last 10 processed texts in queue
    if len(processing_queue) > 10:
        processing_queue.pop(0)
    
    # ALSO save to file for cross-process access
    try:
        # Write processed text to file
        with open('processed_text.txt', 'w', encoding='utf-8') as f:
            f.write(processed_text)
        
        # Write metadata to separate file
        metadata = {
            'timestamp': time.time(),
            'original_length': original_length,
            'processed_length': len(processed_text),
            'processing_time': processing_time
        }
        with open('processing_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Processed text stored for pipeline access: {len(processed_text)} characters")
        print("✓ Text also saved to files for cross-process access")
        
    except Exception as e:
        print(f"Warning: Could not save to files: {e}")

def store_risk_analysis(risk_data: dict):
    """
    Store risk analysis results for display
    """
    global latest_risk_analysis
    latest_risk_analysis = risk_data
    print(f"✓ Risk analysis stored: {risk_data.get('risk_level', 'Unknown')} - {risk_data.get('risk_score', 0)}%")
    
def get_latest_processed_text() -> str:
    """
    Function for external programs to get the latest processed text.
    Your pipeline can import this function from app.py
    """
    global latest_processed_text
    return latest_processed_text

def get_processing_queue() -> list:
    """
    Get all recent processed texts with metadata.
    Useful for batch processing or pipeline monitoring.
    """
    global processing_queue
    return processing_queue.copy()  # Return copy to prevent external modification

def clear_processing_queue():
    """Clear the processing queue (useful for pipeline cleanup)."""
    global processing_queue, latest_processed_text, latest_risk_analysis
    processing_queue.clear()
    latest_processed_text = ""
    latest_risk_analysis = {}
    print("Processing queue cleared")

# Create the Flask application
app = Flask(__name__)

# Set a secret key (used for security features like flash messages)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-in-production')

# Configure the application
app.config.update({
    'MAX_CONTENT_LENGTH': 1 * 1024 * 1024,  # 1MB limit for text input
    'SEND_FILE_MAX_AGE_DEFAULT': 31536000    # Cache static files for 1 year
})

# Statistics to track how the application is performing
request_stats = {
    'total_requests': 0,        # How many requests we've handled
    'total_processing_time': 0, # Total time spent processing
    'average_text_length': 0,   # Average length of text processed
    'max_text_length': 0        # Longest text we've processed
}

@app.before_request
def before_request():
    """
    This function runs BEFORE each request is processed.
    
    Like starting a stopwatch when someone asks you a question.
    """
    request.start_time = time.perf_counter()

@app.after_request
def after_request(response):
    """
    This function runs AFTER each request is processed.
    
    Like stopping the stopwatch and recording how long it took.
    """
    if hasattr(request, 'start_time'):
        processing_time = time.perf_counter() - request.start_time
        request_stats['total_requests'] += 1
        request_stats['total_processing_time'] += processing_time
    return response

@app.route('/')
def index():
    """
    This handles requests to the home page (/).
    
    When someone visits your website, this function runs and
    shows them the main page with the input form.
    """
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    """
    This handles when users submit email text for processing.
    
    It takes the text, processes it, and automatically stores the result
    for external pipeline access.
    """
    try:
        # Start timing this request
        processing_start = time.perf_counter()
        
        # Get the text the user submitted
        text_content = request.form.get('text_input', '').strip()
        
        # Check if they actually entered something
        if not text_content:
            flash('Please enter some email text to process.', 'error')
            return redirect(url_for('index'))
        
        # Update our statistics
        text_length = len(text_content)
        request_stats['max_text_length'] = max(request_stats['max_text_length'], text_length)
        
        # Calculate running average of text length
        total_requests = request_stats['total_requests']
        if total_requests > 0:
            current_avg = request_stats['average_text_length']
            request_stats['average_text_length'] = (
                (current_avg * (total_requests - 1) + text_length) / total_requests
            )
        else:
            request_stats['average_text_length'] = text_length
        
        # Process the email text
        if PROCESSOR_AVAILABLE:
            clean_text = process_email_text(text_content, debug=False)
        else:
            clean_text = "Error: Email processor not available"
        
        # Calculate how long processing took
        processing_time = time.perf_counter() - processing_start
        
        # Store processed text for external pipeline access
        store_processed_text(clean_text, text_length, processing_time)
        
        # Wait a moment for Main.py to process and return results
        time.sleep(0.5)  # Give Main.py time to analyze
        
        # Show success message
        flash('Email text processed successfully and analyzed for security risks!', 'success')
        
        # Show the results page with risk analysis
        return render_template('result.html',
                             original_text=text_content[:500] + ('...' if len(text_content) > 500 else ''),
                             result=clean_text,
                             processing_time=f"{processing_time:.4f}s",
                             input_length=f"{text_length:,} characters",
                             output_length=f"{len(clean_text):,} characters",
                             throughput=f"{text_length / processing_time / 1000:.1f} KB/s" if processing_time > 0 else "N/A",
                             risk_analysis=latest_risk_analysis)
    
    except Exception as e:
        flash(f'Error processing text: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/process', methods=['POST'])
def api_process():
    """
    API endpoint that returns just the processed text and stores it for pipeline access.
    
    This is for other programs that want to use our email processor
    without the web interface.
    """
    try:
        processing_start = time.perf_counter()
        
        # Handle different ways of sending data
        if request.is_json:
            # JSON data (from programs)
            data = request.get_json()
            text_content = data.get('text', '')
        else:
            # Form data (from web forms)
            text_content = request.form.get('text', '')
        
        # Check if they sent any text
        if not text_content.strip():
            return "No text provided", 400  # 400 = Bad Request
        
        text_length = len(text_content)
        
        # Process the text
        if PROCESSOR_AVAILABLE:
            clean_text = process_email_text(text_content.strip(), debug=False)
        else:
            clean_text = "Error: Processor not available"
        
        # Calculate processing time and store for pipeline access
        processing_time = time.perf_counter() - processing_start
        store_processed_text(clean_text, text_length, processing_time)
        
        # Return just the processed text
        return clean_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    except Exception as e:
        return f"Error: {str(e)}", 500  # 500 = Internal Server Error

@app.route('/api/process_detailed', methods=['POST'])
def api_process_detailed():
    """
    API endpoint that returns detailed information about processing and stores for pipeline access.
    
    This includes the processed text plus statistics and metadata.
    """
    try:
        processing_start = time.perf_counter()
        
        # Get the input text
        if request.is_json:
            data = request.get_json()
            text_content = data.get('text', '')
        else:
            text_content = request.form.get('text', '')
        
        if not text_content.strip():
            return jsonify({'success': False, 'error': 'No text provided'})
        
        text_content = text_content.strip()
        text_length = len(text_content)
        
        # Process the text and get detailed stats
        if PROCESSOR_AVAILABLE:
            processor = get_processor()
            clean_text = processor.process_text(text_content, debug=False)
            stats = processor.get_performance_stats()
        else:
            clean_text = "Error: Processor not available"
            stats = {}
        
        processing_time = time.perf_counter() - processing_start
        
        # Store processed text for pipeline access
        store_processed_text(clean_text, text_length, processing_time)
        
        # Return detailed JSON response
        return jsonify({
            'success': True,
            'input_length': text_length,
            'output_length': len(clean_text),
            'result': clean_text,
            'processing_time': f"{processing_time:.4f}s",
            'throughput_kbps': text_length / processing_time / 1000 if processing_time > 0 else 0,
            'processor_stats': stats,
            'stored_for_pipeline': True  # Indicate text is available for pipeline access
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/update_results', methods=['POST'])
def update_results():
    """
    API endpoint for Main.py to send back risk analysis results
    """
    try:
        if request.is_json:
            risk_data = request.get_json()
            store_risk_analysis(risk_data)
            return jsonify({'success': True, 'message': 'Risk analysis updated'})
        else:
            return jsonify({'success': False, 'error': 'JSON data required'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_latest', methods=['GET'])
def get_latest():
    """
    API endpoint for external programs to get the latest processed text.
    Your pipeline can call this to get the most recent processed result.
    """
    global latest_processed_text
    
    if latest_processed_text:
        return jsonify({
            'success': True,
            'text': latest_processed_text,
            'length': len(latest_processed_text),
            'timestamp': time.time()
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No processed text available'
        })

@app.route('/api/get_latest_with_risk', methods=['GET'])
def get_latest_with_risk():
    """
    API endpoint to get latest processed text with risk analysis
    """
    global latest_processed_text, latest_risk_analysis
    
    return jsonify({
        'success': True,
        'text': latest_processed_text,
        'risk_analysis': latest_risk_analysis,
        'timestamp': time.time()
    })

@app.route('/api/get_queue', methods=['GET'])
def get_queue():
    """
    API endpoint to get all recent processed texts with metadata.
    Useful for batch processing in your pipeline.
    """
    global processing_queue
    
    return jsonify({
        'success': True,
        'count': len(processing_queue),
        'items': processing_queue
    })

@app.route('/api/clear_queue', methods=['POST'])
def clear_queue():
    """
    API endpoint to clear the processing queue.
    Your pipeline can call this after consuming the data.
    """
    clear_processing_queue()
    return jsonify({
        'success': True,
        'message': 'Processing queue cleared'
    })

@app.route('/stats')
def performance_stats():
    """
    Show performance statistics about the application.
    
    Like a dashboard showing how well the system is working.
    """
    try:
        # Calculate average processing time
        avg_processing_time = (
            request_stats['total_processing_time'] / request_stats['total_requests']
            if request_stats['total_requests'] > 0 else 0
        )
        
        # Get processor-specific stats if available
        processor_stats = {}
        if PROCESSOR_AVAILABLE:
            processor = get_processor()
            processor_stats = processor.get_performance_stats()
        
        # Return all statistics as JSON
        return jsonify({
            'application_stats': {
                'total_requests': request_stats['total_requests'],
                'average_processing_time': f"{avg_processing_time:.4f}s",
                'average_text_length': f"{request_stats['average_text_length']:.0f} chars",
                'max_text_length': f"{request_stats['max_text_length']:,} chars"
            },
            'processor_stats': processor_stats,
            'processor_available': PROCESSOR_AVAILABLE,
            'latest_risk_analysis': latest_risk_analysis
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.errorhandler(413)
def too_large(e):
    """Handle when someone tries to submit text that's too big."""
    flash('Text input is too large. Maximum size is 1MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """Handle when someone visits a page that doesn't exist."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle internal server errors gracefully."""
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    try:
        print("=" * 60)
        print("Email Processor Web Application with Risk Analysis")
        print("=" * 60)
        print(f"Processor available: {'✓ Yes' if PROCESSOR_AVAILABLE else '✗ No'}")
        print("Web Interface: http://localhost:5000")
        print("Performance Stats: http://localhost:5000/stats")
        print()
        print("API Endpoints:")
        print("   • POST /api/process          - Returns plain text")
        print("   • POST /api/process_detailed - Returns JSON with metadata")
        print("   • POST /api/update_results   - Receive risk analysis from Main.py")
        print()
        print("Pipeline Integration Endpoints:")
        print("   • GET  /api/get_latest       - Get latest processed text")
        print("   • GET  /api/get_latest_with_risk - Get text with risk analysis")
        print("   • GET  /api/get_queue        - Get all recent processed texts")
        print("   • POST /api/clear_queue      - Clear the processing queue")
        print()
        print("Your pipeline can now:")
        print("   ✓ Get cleaned text automatically after processing")
        print("   ✓ Send risk analysis results back to web interface")
        print("   ✓ Access recent processing history")
        print("   ✓ Send text directly for processing via API")
        print("=" * 60)
        
        # Start the web server
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Failed to start Flask application: {e}")
        print("Make sure no other application is using port 5000")
    finally:
        print("Application stopped.")