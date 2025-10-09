from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Using unigrams, bigrams, and trigrams and setting maximum document frequency of 90%
vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_df=0.9)
model = LogisticRegression()

def analyse(loaded_model_data, cleaned_text, emails, domains, urls, ips):
    # Extract model and vectorizer from the loaded data
    model = loaded_model_data['model']
    vectorizer = loaded_model_data['vectorizer']
    
    # Ensure none of the input lists are empty
    cleaned_text = cleaned_text if cleaned_text else [""]
    emails = emails if emails else [""]
    domains = domains if domains else [""]
    urls = urls if urls else [""]
    ips = ips if ips else [""]
    new_input = [ct + em + dom + url + ip for ct, em, dom, url, ip in zip(cleaned_text, emails, domains, urls, ips)]
    
    # Vectorize the new input
    new_input_tfidf = vectorizer.transform(new_input)
    
    # Make predictions
    prediction = model.predict(new_input_tfidf)
    probability = model.predict_proba(new_input_tfidf)
    
    '''
    # Display predictions and their probabilities
    for text, label, prob in zip(new_input_tfidf, prediction, probability):
        print(f"Text: {text}\nPredicted Label: {label}, Probabilities: {prob}\n")
    '''
    
    #Return probability(Positive%)
    return probability[0][1]
