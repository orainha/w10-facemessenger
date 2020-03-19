import json

from pathlib import Path

PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\"

#auth_id = ""
try:
    #get id, present in db file name
    f_data = open (PATH + 'data', 'r')
    data = json.load(f_data)
    for item in data:
        txt = item.split(":")
        auth_id = txt[1]
        break
except IOError as error:
    print (error)

db_file_name = "msys_" + auth_id + ".db"

#DB_PATH = PATH + db_file_name

print (db_file_name)
