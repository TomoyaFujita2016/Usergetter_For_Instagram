import requests
import os
from tqdm import tqdm
import threading
import functools
from logging import (getLogger, StreamHandler, INFO, Formatter)

# log config
handler = StreamHandler()
handler.setLevel(INFO)
handler.setFormatter(Formatter("[%(asctime)s] [%(threadName)s] %(message)s"))
logger = getLogger()
logger.addHandler(handler)
logger.setLevel(INFO)

# const
BASE_URL = "https://www.instagram.com/"
USER_FILE = "users"
DICT_FILE = "eng_dict"
THREAD_NUM = 15

# val
words = []
users = []
threads = []
words_d = []
userNum = 0
tager = 0


def readDict():
    with open(DICT_FILE, "r") as f:
        for row in f:
            words.append(row.replace("\n", ""))
    print("Reading the dict file was Successfully!")

def generateUrl(word):
    return BASE_URL + word + "/"

def checkUserExistence(threadNum, divWords):
    miniUsers = []
    
    for i, word in enumerate(divWords):
        try:
            result = requests.get(generateUrl(word))
        except:
            logger.info("\033[31mAn Error occured!\033[0m"+ generateUrl(word))
        
        if result.status_code == requests.codes.ok:
            miniUsers.append(word)
        
        # conversion of 100%
        if i % (len(divWords)//100) == 0:
            logger.info(str(100*i/len(divWords)) + "% " + str(word))
            if i != 0:
                orderedSaver(threadNum, miniUsers)
            
    orderedSaver(threadNum, miniUsers)

def divideWords(n):
    global words_d
    q = len(words) // n
    m = len(words) % n

    words_d = functools.reduce(
        lambda acc, i:
            (lambda fr = sum([ len(x) for x in acc ]):
                acc + [ words[fr:(fr + q + (1 if i < m else 0))] ]
            )()
        ,
        range(n),
        []
    )

def orderedSaver(threadNum, miniUsers):
    global tager
    global users
    global userNum

    while tager != threadNum:
        pass
    users.extend(miniUsers)
    if tager == (THREAD_NUM - 1):
        saveUsers()
        logger.info("%d users are added to the list!" % (len(users) - userNum))
        userNum = len(users)
        users = []
        tager = 0
    else:
        tager += 1


def saveUsers():
    with open(USER_FILE, "w") as f: 
        for user in users:
            f.write(user + "\n")

def generateWorkers():
    for i in range(THREAD_NUM):
        t = threading.Thread(target=checkUserExistence, args=(i, words_d[i]))
        threads.append(t)
        t.start()

if __name__=="__main__":
    readDict()
    divideWords(THREAD_NUM)
    generateWorkers()
    
