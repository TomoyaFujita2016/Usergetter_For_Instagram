import requests
import os
from datetime import datetime
import time
import re
import functools
import json
from bs4 import BeautifulSoup
import threading
from logging import (getLogger, StreamHandler, INFO, Formatter)

# log config
handler = StreamHandler()
handler.setLevel(INFO)
handler.setFormatter(Formatter("[%(asctime)s] [%(threadName)s] %(message)s"))
logger = getLogger()
logger.addHandler(handler)
logger.setLevel(INFO)

# const
THREAD_COUNT = 15 
SAVE_FREQ = 10
SLEEP_SEC = 100
USER_FILE = "users"
SUM_FILE = "sumFF"
USERDATA_FILE = "./data/"
INSTA_URL = "https://www.instagram.com/"
JSON_STRING = 'window\._sharedData = '
JSON_END = "};"
TAG_FOLLOW = "edge_follow"
TAG_FOLLOWER = "edge_followed_by"
TAG_TIMELINE = "edge_owner_to_timeline_media"
TAG_COUNT = "count"
TAGS_PARENT = ["graphql", "user"]
NUM_ACTIVE = 0

# values
users = []
users_d = []
threads = []
user_data = {}

def getUserIds():
    global users
    with open(USER_FILE, "r") as f:
        for row in f:
            users.append(row.replace("\n", ""))
    print("Reading the user file was Successfully!")

def getHTML(url):
    FLAG_GO = False
    while not FLAG_GO:
        try:
            result = requests.get(url)
            # TODO Also support other status codes
            if result.status_code == 429:
                logger.info("sleep for 429")
                time.sleep(SLEEP_SEC)
            else:
                FLAG_GO = True
        except:
            logger.info("\033[31mAn Error occured!\033[0m"+ generateUrl(word))
            return ""
    return result.text

def divideUsers():
    global users_d
    q = len(users) // THREAD_COUNT
    m = len(users) % THREAD_COUNT

    users_d = functools.reduce(
        lambda acc, i:
            (lambda fr = sum([ len(x) for x in acc ]):
                acc + [ users[fr:(fr + q + (1 if i < m else 0))] ]
            )()
        ,
        range(THREAD_COUNT),
        []
    )


def filteringFF(text):
    data = re.search(JSON_STRING, text)
    jsonData = json.loads(text[data.span()[1]:text.find(JSON_END)+1])
    try:
        user = jsonData["entry_data"]["ProfilePage"][0][TAGS_PARENT[0]][TAGS_PARENT[1]]
    except:
        logger.info(jsonData["entry_data"])
        return {TAG_TIMELINE: -1, TAG_FOLLOW: -1, TAG_FOLLOWER: -1}
    return {TAG_TIMELINE: int(user[TAG_TIMELINE][TAG_COUNT]), TAG_FOLLOW: int(user[TAG_FOLLOW][TAG_COUNT]), TAG_FOLLOWER: int(user[TAG_FOLLOWER][TAG_COUNT])}

def saveHandler(userDict, num):
    global NUM_ACTIVE
    global user_data
    while not NUM_ACTIVE == num:
        pass
    user_data.update(userDict)
    NUM_ACTIVE += 1
    if NUM_ACTIVE == THREAD_COUNT:
        saveUserData()
        logger.info("SAVED!")
        NUM_ACTIVE = 0
    

def work(users_dt, thread_num):
    userData = {}
    for i, user in enumerate(users_dt):
        userData[user] = filteringFF(getHTML(INSTA_URL + user + "/"))
        
        # log
        # This if is for avoiding to divide by zero
        if len(users_dt) < 100:
            logger.info(str(100*i/len(users_dt)) + "% " + str(user) + " post:" + str(userData[user][TAG_TIMELINE]) + " follow:" + str(userData[user][TAG_FOLLOW]) + " follower:" + str(userData[user][TAG_FOLLOWER]))
            pass
        else:
            if i % (len(users_dt)//100) == 0:
                logger.info(str(100*i/len(users_dt)) + "% " + str(user) + " post:" + str(userData[user][TAG_TIMELINE]) + " follow:" + str(userData[user][TAG_FOLLOW]) + " follower:" + str(userData[user][TAG_FOLLOWER]))

        if i != 0 and i % SAVE_FREQ == 0:
            saveHandler(userData, thread_num)
            # initialize to append new dict
            userData = {}

    saveHandler(userData, thread_num)
    logger.info("SAVED!")

def generateWorkers():
    for i in range(THREAD_COUNT):
        t = threading.Thread(target=work, args=(users_d[i], i))
        threads.append(t)
        t.start()

def saveUserData():
    with open(USERDATA_FILE, "w") as f:
        for username in user_data.keys():
            f.write(username  + "," + str(user_data[username][TAG_TIMELINE]) + "," + str(user_data[username][TAG_FOLLOW]) + "," + str(user_data[username][TAG_FOLLOWER]) + "\n")

def setupDir():
    global USERDATA_FILE
    USERDATA_FILE += "{0:%Y%m%d_%H%M.csv}".format(datetime.now())
    filePath = os.path.dirname(USERDATA_FILE)
    if not os.path.exists(filePath):
        os.makedirs(filePath)

if __name__=="__main__":
    #filteringFF(getHTML("https://www.instagram.com/errfd/"))     
    setupDir()
    getUserIds()
    divideUsers()
    generateWorkers()
