import os
import sys
import shutil
import csv
import json
import sqlite3
from pathlib import Path
# TODO: (orainha) Remove import requests
import requests

from bs4 import BeautifulSoup

from core.headers import fill_header

import utils.files as utils


# XXX (ricardoapl) Fix this non-pythonic mess!
CONVERSATIONS_TEMPLATE_FILENAME = os.path.join(os.path.dirname(__file__), r'..\templates\template_conversations.html')
MESSAGES_TEMPLATE_FILENAME = os.path.join(os.path.dirname(__file__), r'..\templates\template_messages.html')
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


# XXX (ricardoapl) Move method to other module (utils?)
# XXX (ricardoapl) Maybe create a single method for all assets (js, css, images)
# XXX (ricardoapl) Fix this non-pythonic mess!
def create_js_files():
    try:
        if not os.path.exists(NEW_FILE_PATH + "\js"):
            os.makedirs(NEW_FILE_PATH + "\js")
        js_path = os.path.join(os.path.dirname(__file__), r'..\templates\js\\')
        js_files = os.listdir(js_path)
        for filename in js_files:
            shutil.copy2(os.path.join(js_path, filename), NEW_FILE_PATH + "\js")
    except OSError as error:
        print(error)


def report_html_messages(template_path, depth):
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
    # XXX (ricardoapl) This method is not responsible for deleting old files
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
                # # Se não tiver "xma_rtc" há de ser outra coisa, e sempre assim
                elif "image" in attachment_url_mimetype:
                    # Get file type
                    filetype = utils.get_filetype(attachment_playable_url)
                    if (depth == "fast"):
                        button_tag = html_doc_new_file.new_tag('button')
                        button_tag['id'] = attachment_filename + filetype
                        button_tag['class'] = 'btn_download_message_image'
                        button_tag['value'] = attachment_playable_url
                        button_tag.append('Download Image')
                        td_message = html_doc_new_file.new_tag('td')
                        td_message.append(button_tag)
                    elif (depth == "complete"):
                        extract_message_file(MESSAGES_PATH, attachment_preview_url, attachment_filename, filetype, str(thread_key))
                        img_tag = html_doc_new_file.new_tag('img')
                        img_tag['src'] = f'files\{str(thread_key)}\{attachment_filename}{filetype}'
                        td_message = html_doc_new_file.new_tag('td')
                        td_message.append(img_tag)
                # TODO (orainha) Continuar esta parte, verificar também nos outros casos de threadkey
                elif "audio" in attachment_url_mimetype:
                    # Audio filename already has filetype
                    filetype = ''
                    if (depth == "fast"):
                        button_tag = html_doc_new_file.new_tag('button')
                        button_tag['id'] = attachment_filename
                        button_tag['class'] = 'btn_download_message_file'
                        button_tag['value'] = attachment_playable_url
                        button_tag.append('Download Audio')
                        td_message = html_doc_new_file.new_tag('td')
                        td_message.append(button_tag)
                    elif (depth == "complete"):
                        extract_message_file(MESSAGES_PATH, attachment_playable_url, attachment_filename, filetype, str(thread_key))
                        href_tag = html_doc_new_file.new_tag('a')
                        href_tag['href'] = f'files\{str(thread_key)}\{attachment_filename}'
                        href_tag.append(
                            "Audio - " + attachment_title + " - " + attachment_subtitle)
                        td_message = html_doc_new_file.new_tag('td')
                        td_message.append(href_tag)
                elif "video" in attachment_url_mimetype:
                    if (depth == "fast"):
                        button_tag = html_doc_new_file.new_tag('button')
                        button_tag['id'] = attachment_filename
                        button_tag['class'] = 'btn_download_message_file'
                        button_tag['value'] = attachment_playable_url
                        button_tag.append('Download Video')
                        td_message = html_doc_new_file.new_tag('td')
                        td_message.append(button_tag)
                    elif (depth == "complete"):
                        filetype = utils.get_filetype(attachment_preview_url)
                        extract_message_file(MESSAGES_PATH, attachment_preview_url, attachment_filename, filetype, str(thread_key))
                        extract_message_file(MESSAGES_PATH, attachment_playable_url, attachment_filename, '', str(thread_key))
                        img_tag = html_doc_new_file.new_tag('img')
                        # Need to add image filetype on this case, filename ends like '.mp4' (not suitable to show an image)
                        img_tag['src'] = f'files\{str(thread_key)}\{attachment_filename}{filetype}'
                        duration = "["+attachment_duration + \
                            "s]" if attachment_duration != "None" else ""
                        title = " - " + attachment_title if attachment_title != "None" else ""
                        subtitle = " - " + attachment_subtitle if attachment_subtitle != "None" else ""
                        img_tag.append("Video " + duration + title + subtitle)
                        href_tag = html_doc_new_file.new_tag('a')
                        # Video filename already has filetype
                        href_tag['href'] = f'files\{str(thread_key)}\{attachment_filename}'
                        href_tag.append(img_tag)
                        td_message = html_doc_new_file.new_tag('td')
                        td_message.append(href_tag)
                else:
                    # Can be gifs, files
                    if (depth == "fast"):
                        filetype = ''
                        if (attachment_filename.find('.') > 0):
                            filetype = ''
                        else:
                            filetype = utils.get_filetype(attachment_playable_url)
                            filetype = '.' + filetype
                        button_tag = html_doc_new_file.new_tag('button')
                        button_tag['id'] = attachment_filename + filetype
                        button_tag['class'] = 'btn_download_message_file'
                        if (attachment_preview_url != 'None'):
                            button_tag['value'] = attachment_preview_url
                        elif (attachment_playable_url != 'None'):
                            button_tag['value'] = attachment_playable_url
                        button_tag.append('Download File')
                        td_message = html_doc_new_file.new_tag('td')
                        td_message.append(button_tag)
                    elif (depth == "complete"):
                        filetype = ''
                        # if filename has his filetype written...
                        if (attachment_filename.find('.') > 0):
                            filetype = ''
                        else:
                            filetype = utils.get_filetype(attachment_playable_url)

                        if (attachment_preview_url != 'None'):
                            extract_message_file(MESSAGES_PATH, attachment_preview_url, attachment_filename, filetype, str(thread_key))
                            img_tag = html_doc_new_file.new_tag('img')
                            img_tag['src'] = f'files\{str(thread_key)}\{attachment_filename}{filetype}'
                            td_message = html_doc_new_file.new_tag('td')
                            td_message.append(img_tag)

                        elif (attachment_playable_url != 'None'):
                            extract_message_file(MESSAGES_PATH, attachment_playable_url, attachment_filename, filetype, str(thread_key))
                            p_tag = html_doc_new_file.new_tag('p')
                            p_tag.append(attachment_filename)
                            href_tag = html_doc_new_file.new_tag('a')
                            href_tag['href'] = f'files\{str(thread_key)}\{attachment_filename}' + '.' + filetype
                            href_tag.append(p_tag)
                            td_message = html_doc_new_file.new_tag('td')
                            td_message.append(href_tag)

            elif "xma_web_url" in attachment_type:
                if (depth == "fast"):
                    filetype = ''
                    # if filename has his filetype written...
                    if (attachment_filename.find('.') > 0):
                        filetype = ''
                    else:
                        filetype = utils.get_filetype(attachment_playable_url)
                    button_tag = html_doc_new_file.new_tag('button')
                    button_tag['id'] = attachment_filename + filetype
                    button_tag['class'] = 'btn_download_message_file'
                    button_tag['value'] = attachment_preview_url
                    button_tag.append('Download Image')
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(button_tag)
                    td_message.append(message + " - " + attachment_title + " - " + attachment_subtitle)
                elif (depth == "complete"):
                    filetype = utils.get_filetype(attachment_playable_url)
                    extract_message_file(MESSAGES_PATH, attachment_preview_url, attachment_filename, filetype, str(thread_key))
                    img_tag = html_doc_new_file.new_tag('img')
                    img_tag['src'] = f'files\{str(thread_key)}\{attachment_filename}{filetype}'
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(img_tag)
                    td_message.append(message + " - " + attachment_title + " - " + attachment_subtitle)
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


def report_html_conversations(template_path, depth):
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
            # XXX (ricardoapl) Use thread_key instead of counter (that's how we identify the HTML file later on)
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
        # td 1
        td_empty2 = html_doc_new_file.new_tag('td')
        # td 2
        # Get file type
        filetype = utils.get_filetype(participant_pic)
        td_photo = html_doc_new_file.new_tag('td')
        if (depth == "fast"):
            button_tag = html_doc_new_file.new_tag('button')
            button_tag['id'] = str(participant_contact_id) + filetype
            button_tag['class'] = 'btn_download_conversation_contact_image'
            button_tag['value'] = participant_large_pic
            button_tag.append('Download Image')
            td_photo.append(button_tag)
        elif (depth == "complete"):
            extract_images(NEW_FILE_PATH, participant_pic, participant_large_pic, filetype, str(participant_contact_id))
            href_tag = html_doc_new_file.new_tag('a')
            href_tag['href'] = f'conversations\images\large\{participant_contact_id}' + filetype
            img_tag = html_doc_new_file.new_tag('img')
            img_tag['src'] = f'conversations\images\small\{participant_contact_id}' + filetype
            href_tag.append(img_tag)
            td_photo.append(href_tag)
        # td 3
        td_msgs = html_doc_new_file.new_tag('td')
        href_msgs_tag = html_doc_new_file.new_tag('a')
        href_msgs_tag["href"] = f'messages\{str(thread_key)}.html'
        href_msgs_tag["target"] = 'targetframemessages'
        href_msgs_tag.append(str(participant_name))
        td_msgs.append(href_msgs_tag)
        tr_tag_data.append(td_empty2)
        tr_tag_data.append(td_photo)
        tr_tag_data.append(td_msgs)
        html_doc_new_file.table.append(tr_tag_data)
    new_file.seek(0)
    new_file.write(html_doc_new_file.prettify())
    new_file.truncate()


def report_csv_conversations(delim):
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


def report_csv_messages(delim):
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


def report_csv(delim):
    report_csv_conversations(delim)
    report_csv_messages(delim)


def input_file_path(user_path):
    # XXX (orainha) Procurar por utilizadores dando apenas o drive?
    global DB_PATH
    PATH = utils.get_input_file_path(user_path)
    DB_PATH = utils.get_db_path(PATH)

def output_file_path(destination_path):
    global NEW_FILE_PATH
    global MESSAGES_PATH
    NEW_FILE_PATH = utils.get_output_file_path(destination_path)
    MESSAGES_PATH = NEW_FILE_PATH + "messages\\"
    try:
        if not os.path.exists(MESSAGES_PATH):
            os.makedirs(MESSAGES_PATH)
    except IOError as error:
        print(error)
        exit()


def extract_message_file(path, url, filename, filetype, msg_thread_key):
    PATH = os.path.expandvars(path)
    IMAGES_PATH = PATH + f'\\files\{msg_thread_key}'
    utils.extract(path, IMAGES_PATH, url, filename, filetype)


def extract_images(output_path, small_pic_url, large_pic_url, filetype, filename):
    global PATH
    FILENAME = 'conversations.html'
    PATH = os.path.expandvars(output_path)
    SMALL_IMAGES_PATH = PATH + f'\conversations\images\small'
    LARGE_IMAGES_PATH = PATH + f'\conversations\images\large'
    FILENAME = PATH + f'\\{FILENAME}'

    utils.extract(output_path, SMALL_IMAGES_PATH, small_pic_url, filename, filetype)
    utils.extract(output_path, LARGE_IMAGES_PATH, large_pic_url, filename, filetype)
