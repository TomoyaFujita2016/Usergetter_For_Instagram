import requests
import os
from tqdm import tqdm

# const
BASE_URL = "https://www.instagram.com/"
USER_FILE = "users"
DICT_FILE = "eng_dict"
SAVE_SPAN = 5

# val
words = []
users = []
userNum = 0

def readDict():
    with open(DICT_FILE, "r") as f:
        for row in f:
            words.append(row.replace("\n", ""))
    print("Reading the dict file was Successfully!")

def readUsers():
    global userNum
    if not os.path.exists(USER_FILE):
        print("NOTFOUND the users file ! (This is the first execution ...?)")
        return
    with open(USER_FILE, "r") as f:
        for row in f:
            users.append(row.replace("\n", ""))
    userNum = len(users)
    print("Reading the users file was Successfully!")

def generateUrl(word):
    return BASE_URL + word + "/"

def checkUserExistence():
    global saveThreshold
    pbar = tqdm(words, ncols=80)
    for word in pbar:
        result = requests.get(generateUrl(word))
        if result.status_code == requests.codes.ok:
            if not word in users:
                users.append(word)
        else:
            if word in users:
                users.remove(word)

        # When a certain number of users are saved, save them in a file.
        if (len(users) - userNum) % SAVE_SPAN == 0 and not (len(users) - userNum) == 0:
            saveUsers()
            pbar.set_description("Saved!")
        pbar.set_description("Result: %18s %4d" % (word, result.status_code ))

def saveUsers():
    with open(USER_FILE, "w") as f: 
        for user in users:
            f.write(user + "\n")

if __name__=="__main__":
    try:
        readDict()
        readUsers()
        checkUserExistence()
        saveUsers()
    except KeyboardInterrupt:
        print("\n")
        pass
    print("%d users are added to the list!" % (len(users) - userNum))
