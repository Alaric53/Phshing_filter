import re

SAFE_DOMAINS = [
    # Government
    "gov.sg", "moh.gov.sg", "cpf.gov.sg", "singpass.gov.sg",
    # Banks
    "dbs.com.sg", "ocbc.com", "uobgroup.com", "hsbc.com.sg", "standardchartered.com.sg",
    # Universities
    "sit.edu.sg", "ntu.edu.sg", "nus.edu.sg", "smu.edu.sg", "suss.edu.sg",
    # Healthcare
    "singhealth.com.sg", "kkh.com.sg", "nhg.com.sg", "ttsh.com.sg", "nuhs.edu.sg", "nccs.com.sg", "sgmc.com.sg",
    "changi.sghealth.org", "cgh.com.sg", "sgh.com.sg", 
    # Major online shopping sites
    "amazon.com", "amazon.sg", "shopee.sg", "lazada.sg", "qoo10.sg",
    "aliexpress.com", "ebay.com", "taobao.com",
    # International brands
    "microsoft.com", "google.com",  "apple.com", "paypal.com"
]

SUSPICIOUS_KEYWORDS = [
    "urgent", "immediately","important", "verify", "account", "password", "login", "sign in", "credential",
    "security alert", "unusual activity", "suspended", "locked", "payment", "transaction", "banking", "refund",
    "credit card", "debit", "prize", "lottery", "winner", "reset", "free", "offer", "limited time", "attention"
]   # probably have many more

def safe_domain_check(provided_email):
    domain = provided_email.split("@")[-1].lower()
    if domain in SAFE_DOMAINS:                     # return a score of either 0 or 2, with 0 being safe
        return 0    
    else: 
        return 2                                   # not sure if 2 is a good number

def suspicious_keyword_check(subject,body):       # check the subject and body of email for flagged keywords
    content = subject.lower() + "" + body.lower()
    count = 0                                     # count for flagged keywords
    for word in SUSPICIOUS_KEYWORDS:
        if word in content:
            count += 1
    return count

def keyword_position_scoring(subject,body):
    score = 0
    body_content = body.lower().spilt()           # dont need to spilt subject of email because usually it is short
    for word in SUSPICIOUS_KEYWORDS:
        if  word in body_content:
            score += 1            
        elif word in subject.lower():
            score += 2                            # flagged keywords in subject more serious
    return score 

def distance_check():

