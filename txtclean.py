from datacleaning import datacleaning


clean = datacleaning()
#Must be in /Phishing_filter directory when executing
clean.cleanfile("testingdata.txt")

cleaned_text, emails, domains, urls, ips = clean.cleantext("fake.invalidtld")
print(cleaned_text, emails, domains, urls, ips)
