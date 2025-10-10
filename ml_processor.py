from sklearn.linear_model import LogisticRegression

# Using unigrams, bigrams, and trigrams and setting maximum document frequency of 90%
model = LogisticRegression()

def analyse(loaded_model_data, cleaned_text="", emails="", domains="", urls="", ips=""):
    # Extract model and vectorizer from the loaded data
    model = loaded_model_data['model']
    vectorizer = loaded_model_data['vectorizer']
    
    # Ensure none of the input lists are empty
    cleaned_text_str = " ".join(cleaned_text) if isinstance(cleaned_text, list) and cleaned_text else cleaned_text
    emails_str = " ".join(emails) if isinstance(emails, list) and emails else email
    domains_str = " ".join(domains) if isinstance(domains, list) and domains else domains
    urls_str = " ".join(urls) if isinstance(urls, list) and urls else str(urls) else urls
    ips_str = " ".join(ips) if isinstance(ips, list) and ips else str(ips) else ips
    
    # Combine all text features into a single string
    combined_text = " ".join([cleaned_text_str, emails_str, domains_str, urls_str, ips_str])
    
    # Vectorize the combined input (pass as a list with single element)
    new_input_tfidf = vectorizer.transform([combined_text])
    
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


