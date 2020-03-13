import sys
from pathlib import Path
import webbrowser
import sqlite3

# CONSTANTS

PARTICIPANTS_TEMPLATE_FILE_PATH = "html_participants_template.html"

NEW_FILE_PATH = str(Path.home()) + "\\AppData\\Local\\Temp\\"
DB_PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\msys_709212107.db"

PARTICIPANTS_QUERRY = "SELECT c.profile_picture_url, c.name, c.profile_picture_large_url, p.read_watermark_timestamp_ms, \
     p.delivered_watermark_timestamp_ms, p.nickname \
     FROM participants as p \
         JOIN contacts as c on c.id = p.contact_id"



# FUNCTIONS

def function_html_participants_file(template_path, new_file_path):

    try:
        #get template
        template_file = open(template_path, 'r')
        new_file = open(new_file_path + "participants.html", 'w')

        #get the right place to write
        for line in template_file:
            start_line_index = line.find("</table>")

            #if find the string..
            if start_line_index > 0:
                #write all participants on the right spot
                function_write_participants_to_html(DB_PATH, new_file)
            
            #write file till the end..
            new_file.write(line)
        
        #close files / good practice
        template_file.close()
        new_file.close()

    except IOError as error:
        print (error)


def function_write_participants_to_html(database_path, obj_file):

    #connect to database
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute(PARTICIPANTS_QUERRY)

    #variable initialization
    participant_counter = 1

    for row in c:
        #querry fields
        participant_pic = str(row[0])
        participant_name = str(row[1])
        participant_large_pic = str(row[2])
        participant_thread_key = str(row[3])

        try:
            obj_file.write("""
                <tr>
                    <td>"""  +str(participant_counter) + """</td>
                    <td><a href=\'"""+ str(participant_large_pic) +"""\'><img src=\'""" + str(participant_pic) + """\'></img></a></td>
                    <td>""" + str(participant_name) + """</td>
                </tr>
            """)
            contact_counter = contact_counter + 1
        except IOError as error:
            print (error)
            break



# MAIN

try:
    function_html_participants_file(PARTICIPANTS_TEMPLATE_FILE_PATH, NEW_FILE_PATH)
    webbrowser.open_new_tab(NEW_FILE_PATH + 'participants.html')
except IOError as error:
    print (error)
