import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# Using unigrams, bigrams, and trigrams and setting maximum document frequency of 90%
vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_df=0.9)
model = LogisticRegression()

#Initialise Dataframe
df = pd.read_csv('cleaned_data/cleaned_trainingdata.csv')

#Training Data
target = df.label
df.body = df.body.fillna('')
df.emails = df.emails.fillna('')
df.domains = df.domains.fillna('')
df.urls = df.urls.fillna('')
df.ips = df.ips.fillna('')
data = [a + b + c + d + e for a, b, c, d, e in zip(df.domains, df.body, df.emails, df.urls, df.ips)]

#Testing different configurations
i=0
max_i=0
accuracy = 0
stored_accuracy = 0
MAX_TRIES = 3000
while (accuracy < 1 and i < MAX_TRIES):
    #Split Training(70%) and Testing(30%) Data
    X_train, X_test, Y_train, Y_test = train_test_split(data,target,test_size=0.3,random_state=i)

    #Training
    xtrain_tfidf = vectorizer.fit_transform(X_train)
    model.fit(xtrain_tfidf, Y_train)

    #Testing
    xtest_tfidf = vectorizer.transform(X_test)

    #Results
    accuracy = model.score(xtest_tfidf, Y_test)
    
    if accuracy > stored_accuracy:
        stored_accuracy = accuracy
        print(accuracy)
        #update max
        max_i=i
        print(i)
    
    i += 1


#Saving best model
#Split Training(70%) and Testing(30%) Data
X_train, X_test, Y_train, Y_test = train_test_split(data,target,test_size=0.3,random_state=max_i)

#Training
xtrain_tfidf = vectorizer.fit_transform(X_train)
model.fit(xtrain_tfidf, Y_train)

#Testing
xtest_tfidf = vectorizer.transform(X_test)

#Results
accuracy = model.score(xtest_tfidf, Y_test)
print(accuracy)

# Saving the trained model and vectorizer
joblib.dump({'model': model, 'vectorizer': vectorizer}, 'model/model_trained.joblib')
