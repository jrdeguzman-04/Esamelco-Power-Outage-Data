import os

if os.path.exists(".env"):
    print(".env file exists!")
else:
    print(".env file NOT found!")
