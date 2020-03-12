import sys
from pathlib import Path

DB_PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\msys_709212107.db"
ficheiro_tabelas = "C:\\Users\\user\\Desktop\\python\\tabelas.txt"

try:
   # open file stream
    #file = open("c:\\users\\user\\test.txt", 'r') 
    file = open(DB_PATH, 'r', errors='ignore')
except IOError:
   print ("There was an error reading from", file)
   #sys.exit()

try:
   # open file stream
    file_write = open(ficheiro_tabelas, 'w')
except IOError:
   print ("There was an error writing to"), file_write
   #sys.exit()


for line in file:
   start_index = line.find("CREATE TABLE")
   end_index = line.find("(") 
   if start_index > 0:
      #escreve apenas o nome da tabela
      #exemplo: CREATE TABLE table (
      #  escreve no ficheiro_tabelas, apenas "table"
      file_write.write(line[start_index+12:end_index]+"\n")
    
file.close()
file_write.close()