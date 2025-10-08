import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Using unigrams, bigrams, and trigrams and setting maximum document frequency of 90%
vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_df=0.9)
model = LogisticRegression()

#Initialise Dataframe
df = pd.read_csv('cleaned_data/cleaned_testingdata.csv')

#Training Data
target = df.label
df.emails = df.emails.fillna('')
df.domains = df.domains.fillna('')
df.urls = df.urls.fillna('')
df.ips = df.ips.fillna('')
inputs = df.domains + df.body + df.emails + df.urls + df.ips

#Split Training(70%) and Testing(30%) Data
X_train, X_test, Y_train, Y_test = train_test_split(inputs,target,test_size=0.3,random_state=2524)

#Training
xtrain_tfidf = vectorizer.fit_transform(X_train)
model.fit(xtrain_tfidf, Y_train)

# Saving the trained model and vectorizer
joblib.dump({'model': model, 'vectorizer': vectorizer}, 'model/model_trained.joblib')

#Testing
xtest_tfidf = vectorizer.transform(X_test)

#Results
accuracy = model.score(xtest_tfidf, Y_test)
print(accuracy)


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



