import sys
import sqlite3

# CONSTANTS
MSG_PATH = "C:\\Users\\user\\Documents\\python\\querrys\\mensagens\\"
DB_PATH = "C:\\Users\\user\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\msys_709212107.db"
QUERRY = "SELECT m.thread_key, datetime((m.timestamp_ms)/1000,'unixepoch'), u.contact_id, m.sender_id, u.name, m.text \
          FROM messages as m \
                  JOIN user_contact_info as u ON m.sender_id = u.contact_id \
          ORDER BY m.timestamp_ms DESC"
STDOUT_ALL_OK = " files successfuly created"

# FUNCTIONS
def printMsgs(messengerDB):

   #connect to database
   conn = sqlite3.connect(messengerDB)
   c = conn.cursor()
   c.execute(QUERRY)

   #variable initialization
   thread_key = 0
   new_thread_key = 1
   file_write = ""
   file_counter = 1

   for row in c:
      #querry fields
      datetime = str(row[1]) 
      sender_name = str(row[4])
      message = str(row[5])
      new_thread_key = row[0]

      #if is the first conversation file...
      if thread_key == 0:
         thread_key = new_thread_key
         new_file = MSG_PATH + str(file_counter)+".txt"
         try:
            file_write = open(new_file, 'w+', errors='ignore')
            file_write.write("["+ datetime +"]"+ sender_name +" : "+ message +"\r\n")
         except IOError as error:
            print (error)
            break

      #if is the same conversation as previous..
      elif thread_key == new_thread_key:
         try:
            file_write = open(new_file, 'a', errors='ignore')
            file_write.write("["+ datetime +"]"+ sender_name +" : "+ message +"\r\n")
         except IOError as error:
            print (error)
            break

      #if is a new conversation..
      elif thread_key != new_thread_key:
         thread_key = new_thread_key

         file_counter = file_counter + 1
         new_file = MSG_PATH + str(file_counter)+".txt"
         try:
            file_write = open(new_file, 'w+', errors='ignore')
            file_write.write("["+ datetime +"]"+ sender_name +" : "+ message +"\r\n")
         except IOError as error:
            print (error)
            break
   return file_counter

# MAIN
counter = 0
try:
   counter = printMsgs(DB_PATH)
except IOError as error:
    print (error)
finally:
   print (str(counter) + STDOUT_ALL_OK)