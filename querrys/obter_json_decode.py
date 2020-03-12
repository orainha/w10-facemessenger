import sys
import json

ficheiro_db = "C:\\Users\\user\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\msys_709212107.db"
ficheiro = "C:\\Users\\user\\Documents\\python\\querrys\\contactos\\contacts.txt"

try:
   # open file stream
   #file = open("c:\\users\\user\\test.txt", 'r') 
   in_file = open(ficheiro, 'r', errors='ignore')
   data = json.load(in_file)
   for line in in_file:
      print(line)
   in_file.close()

except IOError as error:
   print (error)
   #sys.exit()


    
