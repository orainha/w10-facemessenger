import sys
import sqlite3
import json

# CONSTANTS
CONTACT_PATH = "C:\\Users\\user\\Documents\\python\\querrys\\contactos\\contacts.txt"
DB_PATH = "C:\\Users\\user\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\msys_709212107.db"
QUERRY = "SELECT * FROM user_contact_info"
STDOUT_ALL_OK = "Contact file successfuly created"

# FUNCTIONS
def printContacts(messengerDB):

   #connect to database
   conn = sqlite3.connect(messengerDB)
   c = conn.cursor()
   c.execute(QUERRY)

   #variable initialization
   thread_key = 0
   new_thread_key = 1
   file_write = ""
   contact_counter = 1

   for row in c:
      #querry fields
      contact_id = str(row[0]) 
      contact_name = str(row[1])
      contact_phone = str(row[2])
      contact_email = str(row[3])

      new_file = CONTACT_PATH
      if contact_counter == 1:
         try:
            file_write = open(new_file, 'w+', errors='ignore', encoding="utf8")
            #file_write.write("Number: " + str(contact_counter) + "\r\nName: " + str(contact_name) + "\r\nPhone : "+ str(contact_phone) +"\r\nEmail: "+ str(contact_email) + "\r\n\n")
            file_write.write(json.dumps({'Number': str(contact_counter), 'Name': str(contact_name), 'Phone':  str(contact_phone), 'Email': str(contact_email) }, sort_keys=True, indent=4) + "\n")
            contact_counter = contact_counter + 1
         except IOError as error:
            print (error)
            break
      else:
         try:
            file_write = open(new_file, 'a', errors='ignore', encoding="utf8")
            #file_write.write("Number: " + str(contact_counter) + "\r\nName: " + str(contact_name) + "\r\nPhone : "+ str(contact_phone) +"\r\nEmail: "+ str(contact_email) + "\r\n\n")
            file_write.write(json.dumps({'Number': str(contact_counter), 'Name': str(contact_name), 'Phone':  str(contact_phone), 'Email': str(contact_email) }, sort_keys=True, indent=4) + "\n")
            contact_counter = contact_counter + 1
         except IOError as error:
            print (error)
            break

# MAIN
try:
   counter = printContacts(DB_PATH)
except IOError as error:
    print (error)
finally:
   print (STDOUT_ALL_OK)