import webbrowser
from pathlib import Path

NEW_FILE = DB_PATH = str(Path.home()) + "\\AppData\\Local\\Temp\\"

f = open(DB_PATH + 'helloworld.html','w+')

string = "Hello Worldji"

message = """<html>
<head></head>
<body><p>""" + string +"""</p></body>
</html>"""

f.write(message)
f.close()


webbrowser.open_new_tab(DB_PATH + 'helloworld.html')