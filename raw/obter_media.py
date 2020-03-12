import sys
import requests
from pathlib import Path
#import httplib
DB_PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\msys_709212107.db"

try:
   # open file stream
    #file = open("c:\\users\\user\\test.txt", 'r') 
    f = open(DB_PATH, 'r', errors='ignore')
    file_write = open("links2.txt", 'w')

except IOError as error:
   print (error)
counter = 0
for line in f:
    locate_str = line.find("image")
    start_index = line.find("https://")
    end_index = line.find("/messaging/") 
    if locate_str > 0:
      img_url = line[start_index:end_index]
      if img_url != '':
         req = requests.get(img_url)
         if req.status_code == requests.codes.ok:
            try:
               ext = ''
               if line.find (".jpg") > 0:
                  ext = ".jpg"
               if line.find (".gif") > 0:
                  ext = ".gif"
               if line.find (".png") > 0:
                  ext = ".png"
               if line.find (".mp4") > 0:
                  ext = ".mp4"
                  
               ficheiro_imagens = "media\\img_"+str(counter)+ext
               file_write = open(ficheiro_imagens, 'wb+')
               file_write.write(req.content)
               counter = counter + 1
            except IOError as error:
               print (error)

print (counter)
#print (len(img_url))
f.close()
file_write.close()