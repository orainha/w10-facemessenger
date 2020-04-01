import sys
from pathlib import Path
import webbrowser
import sqlite3
import os
import json
import shutil

PARTICIPANTS_TEMPLATE_FILE_PATH = "html_participants_template.html"
MESSAGES_TEMPLATE_FILE_PATH = "html_messages_template.html"
NEW_FILE_PATH = str(Path.home()) + "\\AppData\\Local\\Temp\\"
PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\"

# get id present in db file name
auth_id = 0
try:
    f_data = open(PATH + 'data', 'r')
    data = json.load(f_data)
    for item in data:
        txt = item.split(":")
        auth_id = txt[1]
        break
    db_file_name = "msys_" + auth_id + ".db"
except IOError as error:
    print(error)

DB_PATH = PATH + db_file_name
MESSAGES_PATH = NEW_FILE_PATH + "msgs\\"
PARTICIPANTS_QUERRY = """
                        SELECT c.profile_picture_url, c.name, c.profile_picture_large_url, 
                                p.thread_key, p.contact_id, p.nickname
                        FROM participants as p 
                            JOIN contacts as c on c.id = p.contact_id
                    """
MESSAGES_PER_PARTICIPANT_QUERRY = """
                        SELECT m.thread_key, datetime((m.timestamp_ms)/1000,'unixepoch'), 
                                u.contact_id, m.sender_id, u.name, m.text, 
                                a.preview_url, a.playable_url, a.title_text,
                                a.subtitle_text, a.default_cta_type, a.playable_url_mime_type
                        FROM messages as m 
                            LEFT JOIN attachments AS a ON m.message_id = a.message_id
                            JOIN user_contact_info as u ON m.sender_id = u.contact_id
                        ORDER BY m.timestamp_ms
                    """

def function_html_messages_file(template_path):
    # a ideia é a função function_write_messages_to_html criar os seus próprios ficheiros html de mensagens
    # devem receber um template e criam cada ficheiro baseado nesse template
    function_write_messages_to_html(DB_PATH, template_path)

def function_write_messages_to_html(database_path, template_path):
    # connect to database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(MESSAGES_PER_PARTICIPANT_QUERRY)
    # variable initialization
    thread_key = 0
    new_thread_key = 1
    file_write = ""
    counter = 1
    # delete msgs file path if exists
    if os.path.exists(MESSAGES_PATH):
        shutil.rmtree(MESSAGES_PATH)
    for row in cursor:
        # querry fields
        new_thread_key = row[0]
        datetime = str(row[1])
        sender_name = str(row[4])
        message = str(row[5])
        cta_preview_url = str(row[6])
        cta_title = str(row[8])
        cta_subtitle = str(row[9])
        cta_type = str(row[10])
        cta_url_mimetype = str(row[11])
        # if is the first conversation file...
        if thread_key == 0:
            thread_key = new_thread_key
            try:
                if not os.path.exists(MESSAGES_PATH):
                    os.makedirs(MESSAGES_PATH)
                new_file_path = MESSAGES_PATH + str(thread_key)+".html"
                # get template
                template_file = open(template_path, 'r')
                new_file = open(new_file_path, 'w', encoding='utf-8')
                # get the right place to write
                for line in template_file:
                    start_line_index = line.find("</ul>")
                    # if find the string..
                    if start_line_index > 0:
                        new_file.write(
                            "<li>[" + datetime + "] " + sender_name + " : " + message + "</li>")
                    # write file till the end..
                    new_file.write(line)
                # close files / good practice
                template_file.close()
                new_file.close()
            except IOError as error:
                print(error)
        # if is the same conversation as previous..
        elif thread_key == new_thread_key:
            try:
                previous_file_path = MESSAGES_PATH + str(thread_key) + ".html"
                previous_file = open(new_file_path, 'a', encoding='utf-8')
                # write all participants on the right spot
                # TODO: Verificar se message = null;
                # Se for um attachment poderá ser:
                #  - um video: (preview_url + url video + title_text + subtitle_text)
                #  - um attachment: (preview_url + title_text + subtitle_text + default_cta_title )
                #  - uma imagem (preview_url + title_text + subtitle_text + )
                #  - uma chamada perdida (title_text + subtitle_text)
                if not message or message == 'None':
                    if "xma_rtc" in cta_type:
                        previous_file.write(
                            "<li>[" + datetime + "]" + sender_name + " : " + cta_title + " - " + cta_subtitle + "</li>")
                    # se não tiver "xma_rtc" há de ser outra coisa, e sempre assim
                    elif "image" in cta_url_mimetype:
                        previous_file.write(
                            "<li>[" + datetime + "]" + sender_name + " : ""<img src="+cta_preview_url+"></img></li>")
                    # TODO: continuar esta parte, verificar também nos outros casos de threadkey
                    elif "audio" in cta_url_mimetype:
                        previous_file.write(
                            "<li>[" + datetime + "]" + sender_name + " : Audio - " + cta_title + " - " + cta_subtitle + "</li>")
                    elif "video" in cta_url_mimetype:
                        previous_file.write(
                            "<li>[" + datetime + "]" + sender_name + " : Video - " + cta_title + " - " + cta_subtitle + "</li>")
                else:
                    previous_file.write(
                        "<li>[" + datetime + "]" + sender_name + " : " + message + "</li>")
                previous_file.close()
            except IOError as error:
                print(error)
        # if is a new conversation..
        elif thread_key != new_thread_key:
            thread_key = new_thread_key
            counter = counter + 1
            new_file_path = MESSAGES_PATH + str(thread_key)+".html"
            # avoid file overwrite, check if file exists
            if Path(MESSAGES_PATH + str(new_thread_key)+".html").is_file():
                try:
                    new_file = open(new_file_path, 'a', encoding='utf-8')
                except IOError as error:
                    print(error)
            else:
                try:
                    new_file = open(new_file_path, 'w+', encoding='utf-8')
                except IOError as error:
                    print(error)
            try:
                new_file.write("<li>[" + datetime + "]" +
                               sender_name + " : " + message + "</li>")
                new_file.close()
            except IOError as error:
                print(error)

def function_html_participants_file(template_path, new_file_path):
    try:
        # get template
        template_file = open(template_path, 'r')
        new_file_path = new_file_path + "participants.html"
        new_file = open(new_file_path, 'w')
        # get the right place to write
        for line in template_file:
            start_line_index = line.find("</table>")
            # if find the string...
            if start_line_index > 0:
                # write all participants on the right spot
                function_write_participants_to_html(DB_PATH, new_file)
            # write file till the end...
            new_file.write(line)
        template_file.close()
        new_file.close()
    except IOError as error:
        print(error)

def function_write_participants_to_html(database_path, obj_file):
    # connect to database
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute(PARTICIPANTS_QUERRY)
    # variable initialization
    counter = 1
    thread_key = 0
    new_thread_key = 1
    for row in c:
        # querry fields
        participant_pic = str(row[0])
        participant_name = str(row[1])
        participant_large_pic = str(row[2])
        new_thread_key = row[3]
        participant_contact_id = row[4]
        # if is the first conversation file...
        if thread_key == 0:
            thread_key = new_thread_key
            try:
                obj_file.write("""
                    <tr><td></td><td>Conversation: """ + str(counter) + """</td><td></td></tr>
                    <tr>
                        <td></td>
                        <td><a href=\'""" + str(participant_large_pic) + """\'><img src=\'""" + str(participant_pic) + """\'></img></a></td>
                        <td><a href=\'msgs\\""" + str(thread_key) + """.html\'>""" + str(participant_name) + """</a></td>
                    </tr>
                """)
            except IOError as error:
                print(error)
                break
        # if is the same conversation as previous..
        elif thread_key == new_thread_key:
            suspect_contact_id = auth_id
            if (str(participant_contact_id) != str(suspect_contact_id)):
                try:
                    obj_file.write("""
                        <tr>
                            <td></td>
                            <td><a href=\'""" + str(participant_large_pic) + """\'><img src=\'""" + str(participant_pic) + """\'></img></a></td>
                            <td><a href=\'msgs\\""" + str(thread_key) + """.html\'>""" + str(participant_name) + """</a></td>
                        </tr>
                    """)
                except IOError as error:
                    print(error)
                    break
        # if is a new conversation..
        elif thread_key != new_thread_key:
            suspect_contact_id = auth_id
            if (str(participant_contact_id) != str(suspect_contact_id)):
                thread_key = new_thread_key
                counter = counter + 1
                try:
                    obj_file.write("""
                        <tr><td></td><td>Conversation: """ + str(counter) + """</td><td></td></tr>
                        <tr>
                            <td></td>
                            <td><a href=\'""" + str(participant_large_pic) + """\'><img src=\'""" + str(participant_pic) + """\'></img></a></td>
                            <td><a href=\'msgs\\""" + str(thread_key) + """.html\'>""" + str(participant_name) + """</a></td>
                        </tr>
                    """)
                except IOError as error:
                    print(error)
                    break

try:
    function_html_participants_file(
        PARTICIPANTS_TEMPLATE_FILE_PATH, NEW_FILE_PATH)
    function_html_messages_file(MESSAGES_TEMPLATE_FILE_PATH)
    webbrowser.open_new_tab(NEW_FILE_PATH + 'participants.html')
except IOError as error:
    print(error)
