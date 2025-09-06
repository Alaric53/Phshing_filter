from flask import Flask, render_template_string, request
import csv

app = Flask(__name__)

def evaluate_email(email_content):              #Function to evaluate email danger level
    suspicious_keywords = [
    "urgent", "immediately","important", "verify", "account", "password", "login", "sign in", "credential",
    "security alert", "unusual activity", "suspended", "locked", "payment", "transaction", "banking", "refund",
    "credit card", "debit", "prize", "lottery", "winner", "reset", "free", "offer", "limited time", "attention"
    ] 
    #Total scoring for suspicious keywords TBI with whitelist postion scoring distance check URL detection
    score = sum(keyword in email_content.lower() for keyword in suspicious_keywords)
    if score >= 3:
        danger_level = "High Danger"
    elif score == 2:
        danger_level = "Medium Danger"
    else:
        danger_level = "Low Danger"
    return score, danger_level

# Extract email content from html/csv file
def extract_content(file):
    filename = file.filename.lower()
    content = ''
    if filename.endswith('.csv'):
        # Read CSV and link all fields
        stream = file.stream.read().decode('utf-8')
        reader = csv.reader(stream.splitlines())
        for row in reader:
            content += ' '.join(row) + ' '
    elif filename.endswith('.html') or filename.endswith('.htm'):
        content = file.read().decode('utf-8')
    else:
        content = ''
    return content

@app.route('/', methods=['GET', 'POST'])
def report():
    danger_level = None
    email_content = ''
    score = None
    if request.method == 'POST':
        email_content = request.form.get('email', '')
        uploaded_file = request.files.get('file')
        if uploaded_file and uploaded_file.filename != '':
            email_content = extract_content(uploaded_file)
        score, danger_level = evaluate_email(email_content)

#HTML Page, bare bones needs some work done
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Danger Report</title>
            <script>
                function openPopup(email, score, danger) {
                    window.open("/report?email=" + encodeURIComponent(email) + "&score=" + score + "&danger=" + encodeURIComponent(danger), "Report", "width=400,height=200");
                }
            </script>
        </head>
        <body>
            <h2>Enter Email Content or Upload a File</h2>
            <form method="post" enctype="multipart/form-data">
                <label for="email">Email Text:</label><br>
                <textarea name="email" rows="10" cols="50">{{ email_content }}</textarea><br><br>
                <label for="file">Upload CSV or HTML File:</label>
                <input type="file" name="file" accept=".csv, .html, .htm"><br><br>
                <button type="submit">Evaluate</button>
            </form>
            {% if danger_level is not none %}
                <script>
                    window.onload = function() {
                        openPopup(`{{ email_content|replace('\\n', '\\\\n') }}`, {{ score }}, `{{ danger_level }}`);
                    }
                </script>
            {% endif %}
        </body>
        </html>
    ''', email_content=email_content, danger_level=danger_level, score=score)
#Popup for returning report to tell danger level
@app.route('/report')
def report_popup():
    email_content = request.args.get('email', '')
    score = int(request.args.get('score', 0))
    danger_level = request.args.get('danger', 'Low Danger')
    return render_template_string('''
        <html>
        <head><title>Danger Level Report</title></head>
        <body>
            <h3>Danger Level: {{ danger_level }}</h3>
            <p>Suspicious Keywords Score: {{ score }}</p>
        </body>
        </html>
    ''', danger_level=danger_level, score=score)

if __name__ == '__main__':
    app.run(debug=True)
