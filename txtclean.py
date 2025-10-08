from datacleaning import datacleaning


clean = datacleaning()
#Must be in /Phishing_filter directory when executing
#clean.cleanfile("testingdata.txt")
clean.cleanfile("invalid.txt")
