import sys
import sqlite3
import json
from pathlib import Path


# CONSTANTS

REACTIONS_PATH = "C:\\Users\\user\\Documents\\python\\querrys\\contactos\\reactions.json"
DB_PATH2 = "C:\\Users\\user\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\msys_709212107.db"
DB_PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\msys_709212107.db"

QUERRY = "SELECT DISTINCT r.reaction \
         FROM reactions as r "


STDOUT_ALL_OK = "Reactions successfuly created"


# FUNCTIONS

def printReaction(messengerDB):
   #connect to database
   conn = sqlite3.connect(messengerDB)
   c = conn.cursor()
   c.execute(QUERRY)

   #variable initialization
   reaction_counter = 1

   file_write = ""
   for row in c:
      #querry fields
      reaction = str(row[0]) 
      if reaction_counter == 1:
         try:
            file_write = open(REACTIONS_PATH, 'w+', errors='ignore', encoding="utf16")
            #file_write.write(reaction)python
            json.dump(reaction, file_write)
            reaction_counter = reaction_counter + 1
            #print(reaction)
         except IOError as error:
            print (error)
            break
      else: 
         try:
            file_write = open(REACTIONS_PATH, 'a', errors='ignore', encoding="utf16")
            #file_write.write(reaction)
            json.dump(reaction, file_write)
            #print(reaction)
         except IOError as error:
            print (error)
            break

   file_write.close()
# MAIN

try:
   counter = printReaction(DB_PATH)
except IOError as error:
    print (error)
finally:
   print (STDOUT_ALL_OK)

 
 