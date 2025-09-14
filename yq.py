from datacleaning import datacleaning

clean = datacleaning()

clean.cleanfile("testingdata.txt")
#cleaned_text, emails, domains, urls, ips = clean.cleantext("input text here 192.168.12.1:8080. hi")
#print(cleaned_text, emails, domains, urls, ips)


