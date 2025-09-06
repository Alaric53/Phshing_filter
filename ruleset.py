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
    "microsoft.com", "google.com",  "apple.com", "paypal.com",
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
        return 2                                   

def suspicious_keyword_check(subject,body):        # check the subject and body of email for flagged keywords
    content = subject.lower() + " " + body.lower() # separate subject and body with a 'space'   
    count = 0                                      # count for flagged keywords
    for word in SUSPICIOUS_KEYWORDS:
        if word in content:
            count += 1

    return count

def keyword_position_scoring(subject,body):
    score = 0
    body_content = body.lower().split()           # dont need to spilt subject of email because usually it is short
    for word in SUSPICIOUS_KEYWORDS:
        if  word in body_content[:15]:            # only flag if keywords appear in the first 15 words of body
            score += 1            
        elif word in subject.lower():
            score += 2                            # flagged keywords in subject are more serious
    return score 

def levenshtein_distance(a,b):                    # genuinely just copy pasted this
    dp = [[0] * (len(b)+1) for _ in range(len(a)+1)]
    for i in range(len(a)+1):
        for j in range(len(b)+1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    return dp[len(a)][len(b)]


def lookalike_domain_check(domain):             # checker using levenshtein alg
    for safe in SAFE_DOMAINS:
        distance = levenshtein_distance(domain, safe)
        if distance <= 2:   # small difference means it is suspicious
            return 3        
    return 0


def suspicious_url_detection(body):     
    ips = re.findall(r"http[s]?://\d+\.\d+\.\d+\.\d+", body)       # find ip urls
    urls = re.findall(r"http[s]?://[^\s]+", body)                  # find all urls
    suspicious_urls = ips + urls
    score = len(suspicious_urls) * 2             # 2 points per flagged instance
    
    return score, suspicious_urls

def ruleset(email):     #TBD if we using dict
    score = 0
    sender_domain = email["from"].split("@")[-1]

    score += safe_domain_check(email["from"])
    score += suspicious_keyword_check(email["subject"], email["body"])
    score += keyword_position_scoring(email["subject"], email["body"])
    score += lookalike_domain_check(sender_domain)

    url_score, suspicious_urls = suspicious_url_detection(email["body"])
    score += url_score

    return score, suspicious_urls








