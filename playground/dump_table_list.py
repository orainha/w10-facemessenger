import sys
from pathlib import Path

DB_PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\msys_100047488492327.db"
TABLES_FILE = "C:\\Users\\IEUser\\Desktop\\python\\tabelas.txt"

try:
    file = open(DB_PATH, 'r', errors='ignore')
except IOError:
    print("There was an error reading from ", file)

try:
    file_write = open(TABLES_FILE, 'w')
except IOError:
    print("There was an error writing to ", file_write)

for line in file:
    start_index = line.find("CREATE TABLE")
    end_index = line.find("(")
    if start_index > 0:
        file_write.write(line[start_index+12:end_index] + "\n")

file.close()
file_write.close()
