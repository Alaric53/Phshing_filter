from ruleset import (
    safe_domain_check,
    suspicious_keyword_check,
    keyword_position_scoring,
    levenshtein_distance,
    lookalike_domain_check,
    suspicious_url_detection
)

# --- Demo data ---
email = "user@g0v.sg"  # typo lookalike domain
subject = "Urgent account verification"
body = "Please verify your password immediately at http://192.168.0.1"
domain = "g0v.sg"

# --- Run individual functions ---
safe_result = safe_domain_check(email)
keyword_hits = suspicious_keyword_check(subject, body)
keyword_pos_score = keyword_position_scoring(subject, body)
lev_dist = levenshtein_distance("paypal", "paypa1")
lookalike_score = lookalike_domain_check(domain)
url_score, suspicious_urls = suspicious_url_detection(body)

# --- Display results ---
print("=== RULESET FUNCTION DEMONSTRATION ===")
print(f"Safe domain check (0=safe,2=unsafe): {safe_result}")
print(f"Suspicious keywords detected: {keyword_hits}")
print(f"Keyword position score: {keyword_pos_score}")
print(f"Levenshtein distance (paypal vs paypa1): {lev_dist}")
print(f"Lookalike domain score: {lookalike_score}")
print(f"Suspicious URL score: {url_score}")
print(f"Detected URLs: {suspicious_urls}")
print("=======================================")
