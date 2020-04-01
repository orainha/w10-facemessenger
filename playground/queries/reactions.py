import sys
import sqlite3
import json
from pathlib import Path

REACTIONS_PATH = "C:\\Users\\IEUser\\Desktop\\python\\reactions.json"
DB_PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\msys_100047488492327.db"
QUERRY = "SELECT DISTINCT r.reaction \
         FROM reactions as r "
STDOUT_ALL_OK = "Reactions successfully created!"

def printReaction(messengerDB):
    # connect to database
    conn = sqlite3.connect(messengerDB)
    c = conn.cursor()
    c.execute(QUERRY)
    # variable initialization
    reaction_counter = 1
    file_write = ""
    for row in c:
        # querry fields
        reaction = str(row[0])
        if reaction_counter == 1:
            try:
                file_write = open(REACTIONS_PATH, 'w+',
                                  errors='ignore', encoding="utf16")
                json.dump(reaction, file_write)
                reaction_counter = reaction_counter + 1
            except IOError as error:
                print(error)
                break
        else:
            try:
                file_write = open(REACTIONS_PATH, 'a',
                                  errors='ignore', encoding="utf16")
                json.dump(reaction, file_write)
            except IOError as error:
                print(error)
                break
        file_write.close()

try:
    counter = printReaction(DB_PATH)
    print(STDOUT_ALL_OK)
except IOError as error:
    print(error)
