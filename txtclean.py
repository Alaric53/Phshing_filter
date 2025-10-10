from datacleaning import datacleaning


clean = datacleaning()
#Must be in /Phishing_filter directory when executing
clean.cleanfile("testingdata.txt")
#clean.cleanfile("invalid.txt")
#cleaned_text, emails, domains, urls, ips = clean.cleantext("If you see nothing or a banner below please click here <http://www.bzprod.tv/mail/View.jsp?buzzmailId=186&mailId=an9_28_01> Notice:You are receiving this email because your email address was used to receive an on-line price quote, or because it was provided with a vehicle request." )
#print(cleaned_text)
