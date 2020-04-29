import sys
import os
import shutil
import json
import sqlite3
import webbrowser
from headers import fill_header
from bs4 import BeautifulSoup
from pathlib import Path

PARTICIPANTS_TEMPLATE_FILENAME = r'templates\template_participants.html'
MESSAGES_TEMPLATE_FILENAME = r'templates\template_messages.html'
NEW_FILE_PATH = os.path.expandvars(r'%TEMP%\\')
PATH = os.path.expandvars(r'%LOCALAPPDATA%\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\')

# XXX Get id present in db file name
# TODO Extract into common method
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
                                a.subtitle_text, a.default_cta_type, a.playable_url_mime_type,
                                a.filename, r.reaction, (SELECT name FROM contacts WHERE id = r.actor_id),
                                a.playable_duration_ms/1000
                        FROM messages as m 
                            LEFT JOIN attachments AS a ON m.message_id = a.message_id
                            JOIN user_contact_info as u ON m.sender_id = u.contact_id
                            LEFT JOIN reactions AS r ON m.message_id = r.message_id
                        ORDER BY m.timestamp_ms
                    """
def create_js_files():
    # XXX Duplicate from contacts.py
    try:
        if not os.path.exists(NEW_FILE_PATH + "\js"):
            os.makedirs(NEW_FILE_PATH + "\js")
        shutil.copy2('templates\js\export-to-csv.js', NEW_FILE_PATH + "\js")
    except IOError as error:
        print(error)

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
        attachment_preview_url = str(row[6])
        attachment_playable_url = str(row[7])
        attachment_title = str(row[8])
        attachment_subtitle = str(row[9])
        attachment_type = str(row[10])
        attachment_url_mimetype = str(row[11])
        attachment_filename = str(row[12])
        reaction = str(row[13])
        reaction_sender = str(row[14])
        attachment_duration = str(row[15]) 

        #beautiful soup variables
        html_doc_new_file = ""
        td_message = ""
       
        # if is the first conversation file...
        if thread_key == 0:
            thread_key = new_thread_key
            try:
                if not os.path.exists(MESSAGES_PATH):
                    os.makedirs(MESSAGES_PATH)
                new_file_path = MESSAGES_PATH + str(thread_key)+".html"
                # get template
                template_file = open(template_path, 'r', encoding='utf-8')
                html_doc_new_file = BeautifulSoup(template_file, features='html.parser')
                new_file = open(new_file_path, 'w', encoding='utf-8')
                # close files / good practice
                template_file.close()
            except IOError as error:
                print(error)
        # if is the same conversation as previous..
        elif thread_key == new_thread_key:
            try:
                previous_file_path = MESSAGES_PATH + str(thread_key) + ".html"
                f = open(previous_file_path, 'r', encoding='utf-8')
                html_doc_new_file = BeautifulSoup(f, features='html.parser')
                new_file = open(previous_file_path, 'w', encoding='utf-8')
                # close files / good practice
                f.close()
            except IOError as error:
                print(error)
        # if is a new conversation..
        elif thread_key != new_thread_key:
            thread_key = new_thread_key
            counter = counter + 1
            new_file_path = MESSAGES_PATH + str(thread_key)+".html"
            # avoid file overwrite, check if file exists
            if Path(new_file_path).is_file():
                try:
                    f = open(new_file_path, 'r', encoding='utf-8')
                    html_doc_new_file = BeautifulSoup(f, features='html.parser')
                    f.close()
                except IOError as error:
                    print(error)
            else:
                try:
                    # new file, get template_file
                    template_file = open(template_path, 'r', encoding='utf-8')
                    html_doc_new_file = BeautifulSoup(template_file, features='html.parser')
                    template_file.close()
                except IOError as error:
                    print(error)
            #open according file
            new_file =  open(new_file_path, 'w', encoding='utf-8')
        
        #add <tr> to new file, according to previous thread_key statements(ifs)
        try:
            # TODO: Verificar se message = null;
            # Se for um attachment poderá ser:
            #  - um video: (preview_url + url video + title_text + subtitle_text)
            #  - um attachment: (preview_url + title_text + subtitle_text + default_attachment_title )
            #  - uma imagem (preview_url + title_text + subtitle_text + )
            #  - uma chamada perdida (title_text + subtitle_text)
            if not message or message=="" or message=='None':
                if attachment_type=="xma_rtc_ended_video": #o que é xma_rtc?
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append("Ended "+attachment_title + " - "+ attachment_subtitle)
                elif attachment_type=="xma_rtc_missed_video": #o que é xma_rtc?
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(attachment_title + " at "+ attachment_subtitle)
                elif "xma_rtc" in attachment_type:
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(attachment_title + " - "+ attachment_subtitle)
                elif "application" in attachment_url_mimetype:
                    filetype = attachment_url_mimetype.split('/')[1]
                    href_tag = html_doc_new_file.new_tag('a')
                    href_tag['href']=attachment_playable_url
                    href_tag.append("["+filetype+"] " + attachment_filename)
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(href_tag)
                # se não tiver "xma_rtc" há de ser outra coisa, e sempre assim
                elif "image" in attachment_url_mimetype:
                    img_tag = html_doc_new_file.new_tag('img')
                    img_tag['src'] = attachment_preview_url
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(img_tag)
                # TODO: continuar esta parte, verificar também nos outros casos de threadkey
                elif "audio" in attachment_url_mimetype:
                    href_tag = html_doc_new_file.new_tag('a')
                    href_tag['href'] = attachment_playable_url
                    href_tag.append("Audio - "+ attachment_title + " - "+ attachment_subtitle)
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(href_tag)
                elif "video" in attachment_url_mimetype:
                    img_tag = html_doc_new_file.new_tag('img')
                    img_tag['src'] = attachment_preview_url
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(img_tag)
                    duration = "["+attachment_duration+"s]" if attachment_duration!="None" else ""
                    title = " - " + attachment_title if attachment_title!="None" else ""
                    subtitle = " - " + attachment_subtitle if attachment_subtitle!="None" else ""
                    td_message.append("Video " + duration + title + subtitle)
                else:
                    img_tag = html_doc_new_file.new_tag('img')
                    img_tag['src'] = attachment_preview_url
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(img_tag)
            elif "xma_web_url" in attachment_type:
                href_tag = html_doc_new_file.new_tag('a')
                href_tag['href'] = message
                img_tag = html_doc_new_file.new_tag('img')
                img_tag['src'] = attachment_preview_url
                href_tag.append(img_tag)
                td_message = html_doc_new_file.new_tag('td')
                td_message.append(href_tag)
                td_message.append(message + " - " + attachment_title + " - "+ attachment_subtitle)
            else:
                td_message = html_doc_new_file.new_tag('td')
                td_message.append(message)
            
            tr_tag = html_doc_new_file.new_tag('tr')
            td_datetime = html_doc_new_file.new_tag('td')
            td_datetime.append(datetime)
            td_sender = html_doc_new_file.new_tag('td')
            td_sender.append(sender_name)
            td_reaction = html_doc_new_file.new_tag('td')
            td_reaction.append(reaction)
            td_reaction_sender = html_doc_new_file.new_tag('td')
            td_reaction_sender.append(reaction_sender)
            tr_tag.append(td_datetime)
            tr_tag.append(td_sender)
            tr_tag.append(td_message)
            tr_tag.append(td_reaction)
            tr_tag.append(td_reaction_sender)
            html_doc_new_file.table.append(tr_tag)
            new_file.seek(0)
            new_file.write(html_doc_new_file.prettify())
            new_file.truncate()

            has_header = html_doc_new_file.find_all("p", attrs={"id": "filename"})
            if (not has_header):
                fill_header(database_path, new_file_path)

            # close files / good practice
            new_file.close()
        except IOError as error:
            print(error)

def function_html_participants_file(template_path, new_file_path):
    try:
        # get template
        template_file = open(template_path, 'r', encoding='utf-8')
        new_file_path = new_file_path + "participants.html"
        new_file = open(new_file_path, 'w', encoding='utf-8')
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

def main():
    create_js_files()
    function_html_participants_file(PARTICIPANTS_TEMPLATE_FILENAME, NEW_FILE_PATH)
    function_html_messages_file(MESSAGES_TEMPLATE_FILENAME)
    fill_header(DB_PATH, NEW_FILE_PATH + 'participants.html')
    webbrowser.open_new_tab(NEW_FILE_PATH + 'participants.html')

if __name__ == '__main__':
    main()