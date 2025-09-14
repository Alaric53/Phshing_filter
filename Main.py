from datacleaning import datacleaning
import requests
import subprocess

def main():
    subprocess.Popen(['python', 'app.py'])#run app.py in background
    process_user_input()

    return

def get_data_from_flask():
    try:
        response = requests.get('http://localhost:5000/api/get_latest')
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                return result['text']
        return ""
    except:
        return ""
    
def process_user_input():
    while True:
        cleaned_data = get_data_from_flask()
        if cleaned_data:
            # Process the input
            clean = datacleaning()
            cleaned_text, emails, domains, urls, ml_text = clean.cleantext(cleaned_data)
            print(cleaned_text, emails, domains, urls, ml_text)
            # Temporary risk score (replace with actual ML model and kessler's output via functions)
            risk_score = 0.75  # example score
            
            # Prepare response data
            response_data = {
                'risk_score': risk_score,
                'cleaned_text': cleaned_text,
                'emails': emails,
                'domains': domains,
                'urls': urls
            }
            
            # Send results back to Flask
            try:
                requests.post('http://localhost:5000/api/update_results', 
                            json=response_data)
            except Exception as e:
                print(f"Error sending results: {e}")
                
            return response_data

if __name__ == "__main__":
    main()