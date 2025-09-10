import re #regular expressions
import nltk #pip install nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

import pandas as pd #pip install pandas
from sklearn.feature_extraction.text import TfidfVectorizer #pip install sklearn

import csv
import joblib
from scipy.sparse import save_npz
from scipy.sparse import load_npz

import os


stemmer = PorterStemmer()


class datacleaning:
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    def __init__(self):
        # Initialize resources once when the class is created
        self.stemmer = PorterStemmer()
    def cleantext(self,body):
        #Extracting and storing email, domain and url data
        emails = re.findall(self.email_pattern, body)
        emails = list(set([email.removesuffix('.') for email in emails]))
        urls = re.findall(self.url_pattern,body)
        urls = list(set([url.removesuffix('.') for url in urls]))

        domains = "\n".join([email.split('@')[-1] for email in emails])
        emails = "\n".join(emails)
        urls = "\n".join(urls)

        # Remove emails and urls from data
        cleaned_text = body
        cleaned_text = re.sub(self.email_pattern, '', body)
        cleaned_text = re.sub(self.url_pattern, '', body)

        #removed punctuations
        cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text) 

        #remove stop words
        words = cleaned_text.split()
        words = [w for w in words if w not in self.stop_words]
        cleaned_text = " ".join(words)

        #stemming words into base words,
        words = [stemmer.stem(w) for w in words]
        ml_text = " ".join(words)

        return cleaned_text, emails, domains, urls, ml_text


    def cleanfile(self,file):
        rows = []

        # Lists to store cleaned text and labels for vectorization
        ml_text_list = []
        labels_list = []

        file_name = file.replace(".txt", "")
        output_dir = "cleaned_data"
        with open("test data/"+file, "r", encoding="utf-8") as f:
            
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # split only at the first tab (or whitespace if that's the case)
                parts = line.split("\t", 1)  
                if len(parts) == 2:
                    label, body = parts


                    cleaned_text, emails, domains, urls, ml_text = self.cleantext(body)
                    

                    rows.append({"label": label, "body": cleaned_text, "emails": emails, "domains": domains, "urls": urls})

                    
                    ml_text_list.append(ml_text)
                    labels_list.append(label)


        # Save as CSV
        output_path = output_dir + "/cleaned_" + file_name + ".csv"
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["label", "body","emails","domains","urls"])
            writer.writeheader()
            writer.writerows(rows)

        print("Saved", len(rows), "rows to emails.csv")
        
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(ml_text_list)
        print("Starting TF-IDF vectorization...")
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(ml_text_list)
        print("Vectorization complete.")

        # Save the vectorizer object in the output directory
        joblib.dump(vectorizer, os.path.join(output_dir, 'tfidf_vectorizer_' + file_name + '.joblib'))

        # Save the sparse matrix in the output directory
        save_npz(os.path.join(output_dir, 'tfidf_vectors_' + file_name + '.npz'), X)

        # Save the labels list in the output directory
        joblib.dump(labels_list, os.path.join(output_dir, 'labels_' + file_name +'.joblib'))

        
        
        



