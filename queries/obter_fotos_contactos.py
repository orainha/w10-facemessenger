import sys
import sqlite3
import requests

# CONSTANTS
IMG_PATH = "C:\\Users\\user\\Documents\\python\\querrys\\fotos\\"
DB_PATH = "C:\\Users\\user\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\msys_709212107.db"
QUERRY = "SELECT c.id, c.name, c.profile_picture_large_url, u.phone_number, u.email_address \
          FROM contacts as c \
               JOIN user_contact_info as u ON c.id = u.contact_id \
          ORDER BY c.name"
QUERRY_COUNT = "SELECT COUNT (c.id) \
               FROM contacts as c \
                     JOIN user_contact_info as u ON c.id = u.contact_id \
               ORDER BY c.name"
STDOUT_PLEASE_WAIT = "[+]Getting all contact photos and information.\n[+]This might take a while..."
STDOUT_ALL_OK = "All files successfuly created"

# FUNCTIONS
def printContactInfo(messengerDB):

   # connect to database
   conn = sqlite3.connect(messengerDB)
   c = conn.cursor()
   last_row = c.execute(QUERRY_COUNT).fetchone()[0]
   c.execute(QUERRY)

   print (STDOUT_PLEASE_WAIT)

   # variable initialization
   output_stream = sys.stdout
   row_counter = 1

   for row in c:
      print("Taking care of "+ str(row_counter) +"/"+ str(last_row) + "\r", flush=True)

      # querry fields
      contact_name = str(row[1]) 
      contact_pic = str(row[2])
      contact_phone = str(row[3])
      contact_email = str(row[4])

      # if exists contact_pic_url
      if contact_pic != 'None':
         req = requests.get(contact_pic)
         if req.status_code == requests.codes.ok:
            try:
               # get the picture extension
               ext = ''
               if contact_pic.find (".jpg") > 0:
                  ext = ".jpg"
               if contact_pic.find (".gif") > 0:
                  ext = ".gif"
               if contact_pic.find (".png") > 0:
                  ext = ".png"

               # check if contact has phone and email
               if contact_phone == 'None':
                  contact_phone = 'no-phone'
               if contact_email == 'None':
                  contact_email = 'no-email'

               # create image file
               img_file = IMG_PATH + str(contact_name) + "_" + str(contact_phone) + "_" + str(contact_email) + "_" + ext
               file_write = open(img_file, 'wb+')
               file_write.write(req.content)

               # update display counter
               row_counter = row_counter + 1

            except IOError as error:
               print (error)

# MAIN
try:
   printContactInfo(DB_PATH)
except IOError as error:
    print (error)
finally:
   print (STDOUT_ALL_OK)