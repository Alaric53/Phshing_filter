import re #regular expressions
import nltk #pip install nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

import csv
import os

nltk.download('stopwords', quiet=True)
stemmer = PorterStemmer()
from urllib.parse import urlparse



class datacleaning:
    #matches standard email addres
    email_pattern = r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}'

    # Matches http and https URLs, www URLs, and plain domains with valid TLDs
    url_pattern = re.compile(
    r'(?:^|(?<=[^\w@]))'    # Start anchor: Match start of string OR a non-word/non-@ character (prevents email conflict).
    r'(?:'  # Start main non-capturing group for the three URL formats (Protocol, www., plain domains).
    r'https?://(?:'     # 1. Match full protocol (http:// or https://)
    r'(?:[a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}'    # Match standard domain (subdomains + root domain + TLD >= 2 chars)
    r'|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))' # OR match an IPv4 address (four dot-separated octets 0-255)
    r'|www\.(?:[a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}'  # OR 2. Match domain starting with www.
    r'|(?:[a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(?:com|org|net|edu|gov|io|co|uk|de|fr|jp|au|ca|in|ru|br|mx|nl|se|ch|es|it|kr|cn|us|info|biz|tv|cc|ws)\b'    # OR 3. Match a naked domain ending in one of the specific common TLDs
    r')'
    r'(?::\d{1,5})?'    # OPTIONAL: Match a port number (e.g., :8080), 1 to 5 digits.
    r'(?:/[^\s<>"{}|\\^`\[\]]*)?',  # OPTIONAL: Match the rest of the URL (path, query, fragment), excluding common invalid characters.
    re.MULTILINE)


    ip_pattern = re.compile(
    r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'    # Matches first 3 octets, 0 to 255
    r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'             # Matches last octet 0 to 255
    r'(?::\d{1,5})?'       # optional port number
    r'(?!\d)'              # don’t allow trailing digit
    )

    #install stopwords
    stop_words = set(stopwords.words('english'))
    def __init__(self):
        # Initialize resources once when the class is created
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))

    def clean_trailing_punctuation(self, text):
        return re.sub(r'[.,;:!?)]+$', '', text)

    def cleantext(self,body):
        #Extracting and storing email, domain and url data

        body=body.lower()   #change text to lowercase
        emails = re.findall(self.email_pattern, body)   #extracts emails

        #set make sure that my list values are deduplicated
        #remove suffix and trailing punctuation helps remove the punctuations captured after the extraction
        emails = list(set([email.removesuffix('.') for email in emails]))
        urls = re.findall(self.url_pattern,body)
        urls = list(set([self.clean_trailing_punctuation(url) for url in urls]))
        ips = re.findall(self.ip_pattern, body)
        ips = list(set(ips))
        domains = list(set([email.split('@')[-1] for email in emails]))

        for i in urls:
            if not i.startswith(('http://', 'https://')):   #parse only works when http or https is infront
                i = 'https://' + i                          #urls without http would have trouble getting extracted
            parsed = urlparse(i)
            web = parsed.netloc.removeprefix('www.')        #retrieves web domain only
            domains.append(web)     
                

        # Remove emails and urls from data
        cleaned_text = body
        cleaned_text = re.sub(self.email_pattern, '', cleaned_text)
        cleaned_text = re.sub(self.url_pattern, '', cleaned_text)
        cleaned_text = re.sub(self.ip_pattern, '', cleaned_text)
        #removed punctuations
        cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text) 

        #remove stop words
        words = cleaned_text.split()
        words = [w for w in words if w not in self.stop_words]
        

        #stemming words into base words,
        words = [stemmer.stem(w) for w in words]
        cleaned_text = " ".join(words)
        return cleaned_text, emails, domains, urls, ips


    def cleanfile(self,file):
        rows = []

        file_name = file.replace(".txt", "")
        output_dir = "cleaned_data"
        try:
            with open("testdata/"+file, "r", encoding="utf-8") as f:
                
                for line in f:
                    line = line.strip()
                    #if line is empty, skip line
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
                            #if label is not "yes" or "no" skips line
                            continue
                        
                        #saves the lists as text with new line inbetween each item
                        cleaned_text, emails, domains, urls, ips = self.cleantext(body)
                        emails = "\n".join(emails)
                        domains = "\n".join(domains)
                        urls = "\n".join(urls)
                        ips = "\n".join(ips)

                        rows.append({"label": label, "body": cleaned_text, "emails": emails, "domains": domains, "urls": urls, "ips": ips})

        except:
            #prints error when file to clean cannot be found
            output = "File does not exist"
            print(output)
            return output
                    

        # Save as CSV with labels
        output_path = output_dir + "/cleaned_" + file_name + ".csv"
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["label", "body","emails","domains","urls","ips"])
            writer.writeheader()
            writer.writerows(rows)

        
        output = f"Saved {len(rows)} rows to cleaned_{file_name}.csv"
        print(output)
        return output
        

        
        
        


