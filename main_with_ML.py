from datacleaning import datacleaning
import requests
import subprocess
import ruleset
import NLP_ML
print(NLP_ML.__file__)

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
            cleaned_text, emails, domains, urls, ips = clean.cleantext(cleaned_data)
            print(cleaned_text, emails, domains, urls, ips)
            #ML analysis        
            probability = NLP_ML.analyse(cleaned_text, emails, domains, urls, ips)
            #ruleset score
            ruleset_score, keyword_count = ruleset.process_email_and_score(cleaned_text, emails, domains, urls, ips)
            risk_score, risk_level = combined_score(ruleset_score, probability)

            # Prepare response data
            response_data = {
                'risk_score': risk_score,
                'risk_level':risk_level,
                'sus_keywords':keyword_count,
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
                
            return response_data, risk_score, risk_level, keyword_count

#put the probability variable into the combined score
def combined_score(ruleset_score, probability):
    # call ml function here to give variable a score for now is 0
    ml_score = probability * 100
    print("ruleset_score:", ruleset_score, "ml_score:", ml_score)
    # combine with 50/50 weightage
    risk_score = round((ruleset_score * 0.5) + (ml_score * 0.5))    
    print(f"risk score: {risk_score}")
    # Decide danger level
    if risk_score == 0:
        risk_level ="SAFE"
    elif risk_score <= 33:
        risk_level = "Low danger"
    elif risk_score <= 66:
        risk_level = "Medium danger"
    else:
        risk_level = "High danger"
    
    return risk_score, risk_level


if __name__ == "__main__":
    main()
