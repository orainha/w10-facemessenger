import sys
from pathlib import Path
import webbrowser
import sqlite3
import os

# CONSTANTS

PARTICIPANTS_TEMPLATE_FILE_PATH = "html_participants_template.html"
MESSAGES_TEMPLATE_FILE_PATH = "html_messages_template.html"

NEW_FILE_PATH = str(Path.home()) + "\\AppData\\Local\\Temp\\"
DB_PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\msys_709212107.db"
MESSAGES_PATH = NEW_FILE_PATH + "msgs\\"


PARTICIPANTS_QUERRY = "SELECT c.profile_picture_url, c.name, c.profile_picture_large_url, p.thread_key, p.nickname \
     FROM participants as p \
         JOIN contacts as c on c.id = p.contact_id"

MESSAGES_PER_PARTICIPANT_QUERRY = "SELECT m.thread_key, datetime((m.timestamp_ms)/1000,'unixepoch'), \
    u.contact_id, m.sender_id, u.name, m.text  \
    FROM messages as m JOIN user_contact_info as u ON m.sender_id = u.contact_id \
    ORDER BY m.timestamp_ms"



# FUNCTIONS


def function_html_messages_file(template_path):

    # a ideia é a função function_write_messages_to_html criar os seus próprios ficheiros html de mensagens
    # devem receber um template e criam cada ficheiro baseado nesse template
    function_write_messages_to_html(DB_PATH, template_path)


def function_write_messages_to_html(database_path, template_path):
    #connect to database
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute(MESSAGES_PER_PARTICIPANT_QUERRY)

    #variable initialization
    thread_key = 0
    new_thread_key = 1
    file_write = ""
    counter = 1

    for row in c:
        #querry fields
        datetime = str(row[1]) 
        sender_name = str(row[4])
        message = str(row[5])
        new_thread_key = row[0]

        #if is the first conversation file...
        if thread_key == 0:
            thread_key = new_thread_key
            try:
                if not os.path.exists(MESSAGES_PATH):
                    os.makedirs(MESSAGES_PATH)
                new_file_path = MESSAGES_PATH + str(thread_key)+".html"
                #get template
                template_file = open(template_path, 'r')
                new_file = open(new_file_path, 'w', encoding='utf-8')

                #get the right place to write
                for line in template_file:
                    start_line_index = line.find("</ul>")
                    #if find the string..
                    if start_line_index > 0:
                        #write all participants on the right spot
                        new_file.write("<li>["+ datetime +"]"+ sender_name +" : "+ message +"</li>")
                    
                    #write file till the end..
                    new_file.write(line)
                #close files / good practice
                template_file.close()
                new_file.close()
            except IOError as error:
                print (error)

        #if is the same conversation as previous..
        elif thread_key == new_thread_key:
            try:
                new_file = open(new_file_path, 'a', encoding='utf-8')
                new_file.write("<li>["+ datetime +"]"+ sender_name +" : "+ message +"</li>")
                new_file.close()
            except IOError as error:
                print (error)

        #if is a new conversation..
        elif thread_key != new_thread_key:
            thread_key = new_thread_key
            counter = counter + 1
            new_file_path = MESSAGES_PATH + str(thread_key)+".html"
            try:
                new_file = open(new_file_path, 'w+', encoding='utf-8')
                new_file.write("<li>["+ datetime +"]"+ sender_name +" : "+ message +"</li>")
                new_file.close()
            except IOError as error:
                print (error)

    return counter



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
    counter = 1
    thread_key = 0
    new_thread_key = 1

    for row in c:
        #querry fields
        participant_pic = str(row[0])
        participant_name = str(row[1])
        participant_large_pic = str(row[2])
        new_thread_key = row[3]
        #if is the first conversation file...
        if thread_key == 0:
            thread_key = new_thread_key

            try:
                obj_file.write("""
                    <tr><td></td><td>Conversation: """+ str(counter) +"""</td><td></td></tr>
                    <tr>
                        <td></td>
                        <td><a href=\'"""+ str(participant_large_pic) +"""\'><img src=\'""" + str(participant_pic) + """\'></img></a></td>
                        <td><a href=\'msgs\\"""+ str(thread_key) +""".html\'>""" + str(participant_name) + """</a></td>
                    </tr>
                """)
            except IOError as error:
                print (error)
                break
            

        #if is the same conversation as previous..
        elif thread_key == new_thread_key:
            try:
                obj_file.write("""
                    <tr>
                        <td></td>
                        <td><a href=\'"""+ str(participant_large_pic) +"""\'><img src=\'""" + str(participant_pic) + """\'></img></a></td>
                        <td><a href=\'msgs\\"""+ str(thread_key) +""".html\'>""" + str(participant_name) + """</a></td>
                    </tr>
                """)
            except IOError as error:
                print (error)
                break


        #if is a new conversation..
        elif thread_key != new_thread_key:
            thread_key = new_thread_key
            counter = counter + 1
            try:
                obj_file.write("""
                    <tr><td></td><td>Conversation: """+ str(counter) +"""</td><td></td></tr>
                    <tr>
                        <td></td>
                        <td><a href=\'"""+ str(participant_large_pic) +"""\'><img src=\'""" + str(participant_pic) + """\'></img></a></td>
                        <td><a href=\'msgs\\"""+ str(thread_key) +""".html\'>""" + str(participant_name) + """</a></td>
                    </tr>
                """)
            except IOError as error:
                print (error)
                break


# MAIN

try:
    function_html_participants_file(PARTICIPANTS_TEMPLATE_FILE_PATH, NEW_FILE_PATH)
    function_html_messages_file(MESSAGES_TEMPLATE_FILE_PATH)
    webbrowser.open_new_tab(NEW_FILE_PATH + 'participants.html')
except IOError as error:
    print (error)
