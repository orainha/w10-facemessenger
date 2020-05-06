import os
import sys
import shutil
import csv
import json
import sqlite3
import argparse
import webbrowser
from pathlib import Path
from headers import fill_header
from bs4 import BeautifulSoup


CONVERSATIONS_TEMPLATE_FILENAME = r'templates\template_conversations.html'
MESSAGES_TEMPLATE_FILENAME = r'templates\template_messages.html'
# NEW_FILE_PATH = os.path.expandvars(r'%TEMP%\\')
# PATH = os.path.expandvars(r'%LOCALAPPDATA%\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\')
# DB_PATH = PATH + db_file_name
# MESSAGES_PATH = NEW_FILE_PATH + "msgs\\"
NEW_FILE_PATH = ''
MESSAGES_PATH = ''
PATH = ''
DB_PATH = ''
auth_id = 0
CONVERSATIONS_QUERRY = """
    SELECT
        c.profile_picture_url,
        c.name,
        c.profile_picture_large_url, 
        p.thread_key,
        p.contact_id,
        p.nickname
    FROM participants as p 
    JOIN contacts as c ON c.id = p.contact_id
"""
MESSAGES_PER_CONVERSATION_QUERRY = """
    SELECT
        m.thread_key,
        datetime((m.timestamp_ms)/1000,'unixepoch'), 
        u.contact_id,
        m.sender_id,
        u.name,
        m.text, 
        a.preview_url,
        a.playable_url,
        a.title_text,
        a.subtitle_text,
        a.default_cta_type,
        a.playable_url_mime_type,
        a.filename,
        r.reaction,
        (SELECT name FROM contacts WHERE id = r.actor_id),
        a.playable_duration_ms/1000
    FROM messages as m 
    LEFT JOIN attachments AS a ON m.message_id = a.message_id
    JOIN user_contact_info as u ON m.sender_id = u.contact_id
    LEFT JOIN reactions AS r ON m.message_id = r.message_id
    ORDER BY m.timestamp_ms
"""
THREADS_QUERY = """
    SELECT DISTINCT thread_key
    FROM threads
"""


class MessagesCollector():

    def __init__(self):
        pass


def create_js_files():
    # XXX (ricardoapl) Duplicate from contacts.py
    try:
        if not os.path.exists(NEW_FILE_PATH + "\js"):
            os.makedirs(NEW_FILE_PATH + "\js")
        js_files = os.listdir('templates\js\\')
        for filename in js_files:
            shutil.copy2('templates\js\\' + filename, NEW_FILE_PATH + "\js")
    except OSError as error:
        print(error)


def function_html_messages_file(template_path):
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(MESSAGES_PER_CONVERSATION_QUERRY)
    # Variable initialization
    thread_key = 0
    new_thread_key = 1
    file_write = ""
    counter = 1
    # Delete msgs file path if exists
    if os.path.exists(MESSAGES_PATH):
        shutil.rmtree(MESSAGES_PATH)
    for row in cursor:
        # Query fields
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

        # BeautifulSoup variables
        html_doc_new_file = ""
        td_message = ""

        # If is the first conversation file...
        if thread_key == 0:
            thread_key = new_thread_key
            try:
                if not os.path.exists(MESSAGES_PATH):
                    os.makedirs(MESSAGES_PATH)
                new_file_path = MESSAGES_PATH + str(thread_key)+".html"
                # Get template
                template_file = open(template_path, 'r', encoding='utf-8')
                html_doc_new_file = BeautifulSoup(
                    template_file, features='html.parser')
                new_file = open(new_file_path, 'w', encoding='utf-8')
                # Close file
                template_file.close()
            except IOError as error:
                print(error)
        # If is the same conversation as previous..
        elif thread_key == new_thread_key:
            try:
                previous_file_path = MESSAGES_PATH + str(thread_key) + ".html"
                f = open(previous_file_path, 'r', encoding='utf-8')
                html_doc_new_file = BeautifulSoup(f, features='html.parser')
                new_file = open(previous_file_path, 'w', encoding='utf-8')
                # Close file
                f.close()
            except IOError as error:
                print(error)
        # If is a new conversation..
        elif thread_key != new_thread_key:
            thread_key = new_thread_key
            counter = counter + 1
            new_file_path = MESSAGES_PATH + str(thread_key)+".html"
            # Avoid file overwrite, check if file exists
            if Path(new_file_path).is_file():
                try:
                    f = open(new_file_path, 'r', encoding='utf-8')
                    html_doc_new_file = BeautifulSoup(
                        f, features='html.parser')
                    f.close()
                except IOError as error:
                    print(error)
            else:
                try:
                    # New file, get template_file
                    template_file = open(template_path, 'r', encoding='utf-8')
                    html_doc_new_file = BeautifulSoup(
                        template_file, features='html.parser')
                    template_file.close()
                except IOError as error:
                    print(error)
            # Open according file
            new_file = open(new_file_path, 'w', encoding='utf-8')

        # Add <tr> to new file, according to previous thread_key statements(ifs)
        try:
            # TODO (orainha) Verificar se message = null
            # Se for um attachment poderá ser:
            #  - um video: (preview_url + url video + title_text + subtitle_text)
            #  - um attachment: (preview_url + title_text + subtitle_text + default_attachment_title)
            #  - uma imagem (preview_url + title_text + subtitle_text)
            #  - uma chamada perdida (title_text + subtitle_text)
            if not message or message == "" or message == 'None':
                # XXX (orainha) O que é xma_rtc?
                if attachment_type == "xma_rtc_ended_video":
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(
                        "Ended " + attachment_title + " - " + attachment_subtitle)
                # XXX (orainha) O que é xma_rtc?
                elif attachment_type == "xma_rtc_missed_video":
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(attachment_title +
                                      " at " + attachment_subtitle)
                elif "xma_rtc" in attachment_type:
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(attachment_title +
                                      " - " + attachment_subtitle)
                elif "application" in attachment_url_mimetype:
                    filetype = attachment_url_mimetype.split('/')[1]
                    href_tag = html_doc_new_file.new_tag('a')
                    href_tag['href'] = attachment_playable_url
                    href_tag.append("["+filetype+"] " + attachment_filename)
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(href_tag)
                # Se não tiver "xma_rtc" há de ser outra coisa, e sempre assim
                elif "image" in attachment_url_mimetype:
                    img_tag = html_doc_new_file.new_tag('img')
                    img_tag['src'] = attachment_preview_url
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(img_tag)
                # TODO (orainha) Continuar esta parte, verificar também nos outros casos de threadkey
                elif "audio" in attachment_url_mimetype:
                    href_tag = html_doc_new_file.new_tag('a')
                    href_tag['href'] = attachment_playable_url
                    href_tag.append(
                        "Audio - " + attachment_title + " - " + attachment_subtitle)
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(href_tag)
                elif "video" in attachment_url_mimetype:
                    img_tag = html_doc_new_file.new_tag('img')
                    img_tag['src'] = attachment_preview_url
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(img_tag)
                    duration = "["+attachment_duration + \
                        "s]" if attachment_duration != "None" else ""
                    title = " - " + attachment_title if attachment_title != "None" else ""
                    subtitle = " - " + attachment_subtitle if attachment_subtitle != "None" else ""
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
                td_message.append(
                    message + " - " + attachment_title + " - " + attachment_subtitle)
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

            has_header = html_doc_new_file.find_all(
                "p", attrs={"id": "filename"})
            if (not has_header):
                fill_header(DB_PATH, new_file_path)

            # Close file
            new_file.close()
        except IOError as error:
            print(error)


def function_html_participants_file(template_path):
    # global NEW_FILE_PATH

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(CONVERSATIONS_QUERRY)

    # Get template
    template_file = open(template_path, 'r', encoding='utf-8')
    html_doc_new_file = BeautifulSoup(template_file, features='html.parser')
    new_file = open(NEW_FILE_PATH + "conversations.html",
                    'w', encoding='utf-8')

    # Variable initialization
    counter = 1
    thread_key = 0
    new_thread_key = 1
    for row in c:
        # Query fields
        participant_pic = str(row[0])
        participant_name = str(row[1])
        participant_large_pic = str(row[2])
        new_thread_key = row[3]
        participant_contact_id = row[4]
        # If is the first conversation file...
        if thread_key == 0:
            thread_key = new_thread_key

            tr_tag = html_doc_new_file.new_tag('tr')
            td_empty = html_doc_new_file.new_tag('td')
            td_conversation = html_doc_new_file.new_tag('td')
            td_conversation.append(f"Conversation: {str(counter)}")
            tr_tag.append(td_empty)
            tr_tag.append(td_conversation)
            html_doc_new_file.table.append(tr_tag)

        # If is the same conversation as previous..
        elif thread_key == new_thread_key:
            suspect_contact_id = auth_id
            if (str(participant_contact_id) != str(suspect_contact_id)):
                pass
            else:
                continue
        # If is a new conversation..
        elif thread_key != new_thread_key:
            suspect_contact_id = auth_id
            if (str(participant_contact_id) != str(suspect_contact_id)):
                thread_key = new_thread_key
                counter = counter + 1

                tr_tag = html_doc_new_file.new_tag('tr')
                td_empty = html_doc_new_file.new_tag('td')
                td_conversation = html_doc_new_file.new_tag('td')
                td_conversation.append(f"Conversation: {str(counter)}")
                tr_tag.append(td_empty)
                tr_tag.append(td_conversation)
                html_doc_new_file.table.append(tr_tag)
            else:
                continue

        tr_tag_data = html_doc_new_file.new_tag('tr')
        td_empty2 = html_doc_new_file.new_tag('td')
        td_pic = html_doc_new_file.new_tag('td')
        href_pic_tag = html_doc_new_file.new_tag('a')
        href_pic_tag["href"] = str(participant_large_pic)
        img_tag = html_doc_new_file.new_tag('img')
        img_tag["src"] = str(participant_pic)
        href_pic_tag.append(img_tag)
        td_pic.append(href_pic_tag)

        td_msgs = html_doc_new_file.new_tag('td')
        href_msgs_tag = html_doc_new_file.new_tag('a')
        href_msgs_tag["href"] = f'messages\{str(thread_key)}.html'
        href_msgs_tag.append(str(participant_name))
        td_msgs.append(href_msgs_tag)

        tr_tag_data.append(td_empty2)
        tr_tag_data.append(td_pic)
        tr_tag_data.append(td_msgs)

        html_doc_new_file.table.append(tr_tag_data)

    new_file.seek(0)
    new_file.write(html_doc_new_file.prettify())
    new_file.truncate()


def export_csv_conversations(delim):
    # XXX (ricardoapl) Remove reference to DB_PATH?
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(CONVERSATIONS_QUERRY)
        rows = cursor.fetchall()
        cursor.close()
    # XXX (ricardoapl) Columns is highly dependant on the query,
    #     if we change query we also have to change columns.
    columns = [
        'profile_picture_url',
        'name',
        'profile_picture_large_url',
        'thread_key',
        'contact_id',
        'nickname'
    ]
    # XXX (ricardoapl) Remove reference to NEW_FILE_PATH?
    filename = NEW_FILE_PATH + 'conversations.csv'
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=delim, quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow(columns)
        writer.writerows(rows)


def export_csv_messages(delim):
    # XXX (ricardoapl) Remove reference to DB_PATH?
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(THREADS_QUERY)
        thread_rows = cursor.fetchall()
        cursor.execute(MESSAGES_PER_CONVERSATION_QUERRY)
        msg_rows = cursor.fetchall()
        cursor.close()
    # XXX (ricardoapl) Careful! Columns is highly dependant on the query,
    #     if we change query we also have to change columns.
    columns = [
        'thread_key',
        'datetime',
        'contact_id',
        'sender_id',
        'name',
        'text',
        'preview_url',
        'playable_url',
        'title_text',
        'subtitle_text',
        'default_cta_type',
        'playable_url_mime_type',
        'filename',
        'reaction',
        'actor_name',
        'playable_duration_ms'
    ]
    thread_idx = columns.index('thread_key')
    threads = [row[thread_idx] for row in thread_rows]
    for thread in threads:
        thread_messages = filter(lambda row: (
            row[thread_idx] == thread), msg_rows)
        # XXX (ricardoapl) Remove reference to MESSAGES_PATH?
        filename = MESSAGES_PATH + str(thread) + '.csv'
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=delim, quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(columns)
            writer.writerows(thread_messages)


def export_csv(delim):
    export_csv_conversations(delim)
    export_csv_messages(delim)


def input_file_path(path):
    # XXX (orainha) procurar por utilizadores dando apenas o drive?
    global DB_PATH
    global PATH
    global auth_id
    # Get full path
    PATH = path + f'\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\'
    # TODO (ricardoapl) Extract into common method
    try:
        if os.path.exists(PATH):
            f_data = open(PATH + 'data', 'r')
            data = json.load(f_data)
            for item in data:
                txt = item.split(":")
                auth_id = txt[1]
                break
            db_file_name = "msys_" + auth_id + ".db"
            DB_PATH = PATH + db_file_name
            # print("Application path is " + PATH)
            # print("Database path is " + DB_PATH)
        else:
            raise IOError("Error: File not found on given path")
    except IOError as error:
        print(error)
        exit()


def output_file_path(path):
    global NEW_FILE_PATH
    global MESSAGES_PATH
    path = os.path.expandvars(path)
    NEW_FILE_PATH = path + "\\report\\"
    MESSAGES_PATH = NEW_FILE_PATH + "messages\\"
    try:
        if not os.path.exists(path):
            raise IOError("Error: Given destination output path not found")
        if not os.path.exists(NEW_FILE_PATH):
            os.makedirs(NEW_FILE_PATH)
        if not os.path.exists(MESSAGES_PATH):
            os.makedirs(MESSAGES_PATH)
        # print("Report will be saved on " + NEW_FILE_PATH)
        # print("Messages path is " + MESSAGES_PATH)
    except IOError as error:
        print(error)
        exit()


def load_command_line_arguments():
    # TODO (ricardoapl) This method should only be responsible for parsing, not execution!
    parser = argparse.ArgumentParser()
    group1 = parser.add_argument_group('mandatory arguments')
    group1.add_argument(
        '-i', '--input', help=r'Windows user path. Usage: %(prog)s -i C:\Users\User', required=True)
    parser.add_argument(
        '-o', '--output', default=r'%USERPROFILE%\Desktop', help='Output destination path')
    parser.add_argument(
        '-e', '--export', choices=['csv'], help='Export to %(choices)s')
    parser.add_argument('-d', '--delimiter',
                        choices=[',', '»', '«'], help='Delimiter to csv')
    # parser.add_argument('-src','--source', help='Windows user path. Usage %(prog)s -src C:\Users\User', required=True)
    # parser.add_argument('-dst','--destination', default=r'%USERPROFILE%\Desktop', help='Save report path')

    args = parser.parse_args()

    export_options = {"csv": export_csv}
    file_options = {"input": input_file_path, "output": output_file_path}

    # XXX (ricardoapl) Careful! The way this is, execution is dependant on parsing order!
    # for each argument (key=>value)
    for arg, value in vars(args).items():
        if value is not None and arg == 'export':
            delimiter = args.delimiter if args.delimiter is not None else ','
            export_options[value](delimiter)
        elif value is not None and arg != 'delimiter':
            file_options[arg](value)


def main():
    # TODO (ricardoapl) HTML report is only created if the user requests it (see cmdline args)
    load_command_line_arguments()
    create_js_files()
    function_html_participants_file(CONVERSATIONS_TEMPLATE_FILENAME)
    function_html_messages_file(MESSAGES_TEMPLATE_FILENAME)
    fill_header(DB_PATH, NEW_FILE_PATH + 'conversations.html')
    webbrowser.open_new_tab(NEW_FILE_PATH + 'conversations.html')


if __name__ == '__main__':
    main()
