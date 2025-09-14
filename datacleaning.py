import re #regular expressions
import nltk #pip install nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

import csv
import os


stemmer = PorterStemmer()


class datacleaning:
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    url_pattern = r'(https?://[^\s?]+|www\.[^\s?]+)'
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
        

        #stemming words into base words,
        words = [stemmer.stem(w) for w in words]
        cleaned_text = " ".join(words)

        return cleaned_text, emails, domains, urls


    def cleanfile(self,file):
        rows = []

        # Lists to store cleaned text and labels for vectorization

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
                    if label == "No":
                        label = 1
                    elif label == "Yes":
                        label = 0
                    else:
                         continue
                    


                    cleaned_text, emails, domains, urls = self.cleantext(body)
                    

                    rows.append({"label": label, "body": cleaned_text, "emails": emails, "domains": domains, "urls": urls})

                    
                    


        # Save as CSV
        output_path = output_dir + "/cleaned_" + file_name + ".csv"
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["label", "body","emails","domains","urls"])
            writer.writeheader()
            writer.writerows(rows)

        print("Saved", len(rows), "rows to " + file_name + ".csv")
        
        

        
        
        


