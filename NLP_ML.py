import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
model = MultinomialNB()

#Initialise Dataframe
df = pd.read_csv('Phishing Filters\cleaned_testingdata.csv')

target = df.label
df.domains = df.domains.fillna('')
inputs = df.domains + df.body

#Split Training(70%) and Testing(30%) Data
X_train, X_test, Y_train, Y_test = train_test_split(inputs,target,test_size=0.3,random_state=1122)

#Training
xtrain_tfidf = vectorizer.fit_transform(X_train)
model.fit(xtrain_tfidf, Y_train)

#Testing
xtest_tfidf = vectorizer.transform(X_test)

#Results
accuracy = model.score(xtest_tfidf, Y_test)
print(accuracy)



"""
# Use case
new_input = []

# Vectorize the new input
new_input_tfidf = vectorizer.transform(new_input)

# Make predictions
prediction = model.predict(new_input_tfidf)
probability = model.predict_proba(new_input_tfidf)

# Display predictions and their probabilities
for text, label, prob in zip(new_input_tfidf, prediction, probability):
    print(f"Text: {text}\nPredicted Label: {label}, Probabilities: {prob}\n")
"""
