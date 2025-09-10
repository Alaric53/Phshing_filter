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


def datacleaningg(file):
    rows = []
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

    stemmer = PorterStemmer()
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

                #Extracting and storing email, domain and url data
                emails = re.findall(email_pattern, body)
                emails = list(set([email.removesuffix('.') for email in emails]))
                urls = re.findall(url_pattern,body)
                urls = list(set([url.removesuffix('.') for url in urls]))

                domains = "\n".join([email.split('@')[-1] for email in emails])
                emails = "\n".join(emails)
                urls = "\n".join(urls)

                # Remove emails and urls from data
                cleaned_text = body
                cleaned_text = re.sub(email_pattern, '', body)
                cleaned_text = re.sub(url_pattern, '', body)

                #removed punctuations
                cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text) 

                #remove stop words
                words = cleaned_text.split()
                words = [w for w in words if w not in stop_words]
                cleaned_text = " ".join(words)

                rows.append({"label": label, "body": cleaned_text, "emails": emails, "domains": domains, "urls": urls})

                #stemming words into base words,
                
                words = [stemmer.stem(w) for w in words]
                ml_text = " ".join(words)
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

    
    
    
datacleaningg("testingdata.txt")



#data = "Dear friend, friend  RE save our soul kabila72b@37.com I am Mrs. Deborah Kabila, one of the wives of Late  President Laurent D. Kabila of Democratic Republic of  Congo (DRC).  Consequent upon the assassination of my husband, I am  in possession of USD 58,000,000 (Fifty Eight Million  US Dollars Only) being funds earlier earmarked for  special projects.  This fund has since been deposited  in a security company in West African Country of Togo  where I am residing now with my children. It is now my intention to move the said fund out of  this place (Togo) to a safer place for the benefit of  my children and I, for immediate investment.  Based on  this that I solicited for your assistance to enable me  take this money out of Togo.  However, note that my children and I have agreed to give you 20% of the total fund if you can accept the  offer of assisting us.  Also it will be your  responsibility in directing us on a viable business.  It is also my intention to relocate and probably take  a temporarily resident in your country pending when  all the troubles in my country will be resolved. We  advised that you look for a house we will buy as soon  as we arrived.  To conclude this transaction, you will be required to  come to Togo to open an account in any bank here in  Togo where the security company will deposit the total  sum in your favor. From this bank the money will be  remitted into your original bank in your country.  Immediately this done, all of us will depart Togo to  your country, where my children and I are expected to  take a temporary resident.  Please note that I can not open any Bank account with  my name because, My late husband's first  son-JOSEPH-who took over power in our country, don't  want to see me and my children, He claimed that when  our husband was alive, that I was very close to him  than any other of his wives including his (Joseph)  mother. He also claimed that because of my closeness  to him that I was able to get things from him more  than others. As a result he has been monitoring me.  Infact this one of the main reasons I want to take my children out of our country and any nearby country.  Thanking you in advance. Yours faithfully,  Deborah Kabila (Mrs.)  N/B: Kindly give me your direct telephone,fax and your mobile telephone numbers for  more explanations. ------------------------------------------------------------ http://Game.37.com/  <--- Free Games http://newJoke.com/   <---  J O K E S  ! ! ! --------------------------------------------------------------------- Express yourself with a super cool email address from BigMailBox.com. Hundreds of choices. It's free! http://www.bigmailbox.com ---------------------------------------------------------------------"


def datacleaning(data):
    #Extracting and storing email, domain and url data
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'

    emails = re.findall(email_pattern, data)
    domains = [email.split('@')[-1] for email in emails]
    urls = re.findall(url_pattern,data)

    # Remove emails and urls from data
    cleaned_text = data
    cleaned_text = re.sub(email_pattern, '', data)
    cleaned_text = re.sub(url_pattern, '', cleaned_text)

    

    #removed punctuations
    cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text) 

    #remove stop words
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    words = cleaned_text.split()
    words = [w for w in words if w not in stop_words]
    cleaned_text = [" ".join(words)]

    #stemming words into base words,
    stemmer = PorterStemmer()
    words = [stemmer.stem(w) for w in words]
    ml_text = [" ".join(words)]


    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(ml_text)

    # Convert to DataFrame
    idf = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())

    #CLEANED TEXT IS FOR RULE BASED
    # idf is for ML
    print(cleaned_text)
    print(idf)
    print(emails,domains,urls)

#datacleaning(data)

