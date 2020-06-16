import os
import sys
import threading
import shutil
import csv
import sqlite3
import copy
from pathlib import Path

from bs4 import BeautifulSoup

import utils.files as utils


# XXX (ricardoapl) Fix this non-pythonic mess!
CONVERSATIONS_TEMPLATE_FILENAME = os.path.join(os.path.dirname(__file__), r'..\templates\template_conversations.html')
MESSAGES_TEMPLATE_FILENAME = os.path.join(os.path.dirname(__file__), r'..\templates\template_messages.html')
NEW_FILE_PATH = ''
MESSAGES_PATH = ''
PATH = ''
MSG_FILES_FOLDER_NAME = ''
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
        a.playable_duration_ms/1000,
        m.message_id
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


def report_html(depth):
    report_html_conversations(CONVERSATIONS_TEMPLATE_FILENAME, depth)
    report_html_messages(MESSAGES_TEMPLATE_FILENAME, depth)


def header(html, thread_key, depth):

    one_participant_querry = """
        SELECT
            c.profile_picture_url,
            c.name,
            c.profile_picture_large_url, 
            p.thread_key,
            p.contact_id,
            p.nickname
        FROM participants as p 
        JOIN contacts as c ON c.id = p.contact_id
        WHERE p.thread_key = """ + str(thread_key)

    # Connect to database
    db_path = utils.get_db_path(PATH)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(one_participant_querry)

    victim_photo = html.header.find(
    "div", attrs={"id": "victimPhoto"})
    victim_name = html.header.find(
    "div", attrs={"id": "victimName"})

    div_row_photo = html.new_tag('div')
    div_row_photo["class"] = "row"
    
    div_row_name = html.new_tag('div')
    div_row_name["class"] = "row"

    suspect_id = utils.get_suspect_id(PATH)

    for row in c:
        pic_url = str(row[0])
        name = str(row[1])
        large_pic_url = str(row[2])
        contact_id = str (row[4])

        if contact_id != suspect_id:
            filetype = utils.get_filetype(pic_url)
            div_col_photo = html.new_tag('div')
            div_col_photo["class"] = "col"
            if (depth == "fast"):
                button_tag = html.new_tag('button')
                button_tag['id'] = str(contact_id) + filetype
                button_tag['class'] = 'btn_download_conversation_contact_image btn btn-outline-dark my-2 my-sm-0 mt-2'
                button_tag['value'] = large_pic_url
                button_tag.append('Download Image')
                div_col_photo.append(button_tag)
            elif (depth == "complete"):
                href_tag = html.new_tag('a')
                href_tag['href'] = f'..\conversations\images\large\{contact_id}' + filetype
                img_tag = html.new_tag('img')
                img_tag['src'] = f'..\conversations\images\small\{contact_id}' + filetype
                img_tag['id'] = 'imgContact'
                href_tag.append(img_tag)
                div_col_photo.append(href_tag)
        
            div_row_photo.append(div_col_photo)
            
            # Fill name
            p_tag = html.new_tag('p')
            p_tag["class"] = "col"
            p_tag.append(name)
            
            div_row_name.append(p_tag)            

    victim_photo.append(div_row_photo)
    victim_name.append(div_row_name)

    return html


def create_message_download_button(html_doc_new_file, button_id, button_class, button_value, button_text):
    button_tag = html_doc_new_file.new_tag('button')
    button_tag['id'] = button_id
    button_tag['class'] = "btn btn-outline-light my-2 my-sm-0 fast-button " + button_class
    button_tag['value'] = button_value
    button_tag.append(button_text)
    return button_tag


def create_modern_message_style(html_doc_new_file, fields, div_container_fluid):

    suspect_contact_id = fields[0]
    thread_key = fields[1]
    datetime = fields[2]
    sender_id = fields[3]
    sender_name = fields[4]
    td_message = fields[5]
    reaction = fields[6]
    reaction_sender = fields[7]
    message_id = fields[8]
    last_message_id = fields[9]
    last_sender = fields[10]
    filename = fields[11]
    last_filename = fields[12]

    # suspect align-right    
    suspect_element_style = "col text-right w-75"
    suspect_element_style_color = "col text-right bg-dark text-white"

    # victim align-left
    victim_element_style = "col text-left w-75"
    victim_element_style_color = "col text-left bg-secondary text-white"

    # Sender
    div_row_sender = html_doc_new_file.new_tag('div')
    div_row_sender["class"] = "row"
    small_sender = html_doc_new_file.new_tag('small')
    if(suspect_contact_id == sender_id):
        small_sender["class"] = suspect_element_style
    else:
        small_sender["class"] = victim_element_style
    small_sender.append(sender_name)
    div_empty = html_doc_new_file.new_tag('div')
    div_empty["class"] = "col"
    if(suspect_contact_id == sender_id):
        div_row_sender.append(div_empty)
        div_row_sender.append(small_sender)
    else:
        div_row_sender.append(small_sender)
        div_row_sender.append(div_empty)

    # Message
    div_row_message = html_doc_new_file.new_tag('div')
    div_row_message["class"] = "row"
    div_message = html_doc_new_file.new_tag('div')
    div_message["id"] = "divMessage"
    div_message["class"] = "div-message"
    div_message_content = html_doc_new_file.new_tag('div')
    message = html_doc_new_file.new_tag('td')
    # Must copy td_message to can use on both div and table
    message = copy.copy(td_message)
    if (suspect_contact_id == sender_id):
        div_message_content["id"] = "divMessageContentSuspect"
        div_message_content["class"] = suspect_element_style_color
    else:
        div_message_content["id"] = "divMessageContentVictim"
        div_message_content["class"] = victim_element_style_color
    div_message_content.append(message)
    div_message.append(div_message_content)
    div_empty = html_doc_new_file.new_tag('div')
    div_empty["class"] = "col"
    if (suspect_contact_id == sender_id):
        div_row_message.append(div_empty)
        div_row_message.append(div_message)
    else:
        div_row_message.append(div_message)
        div_row_message.append(div_empty)

    # Datetime
    div_row_datetime = html_doc_new_file.new_tag('div')
    div_row_datetime["class"] = "row"
    div_datetime = html_doc_new_file.new_tag('div')
    if (suspect_contact_id == sender_id):
        div_datetime["class"] = suspect_element_style
    else:
        div_datetime["class"] = victim_element_style
    small_datetime = html_doc_new_file.new_tag('small')
    cite_datetime = html_doc_new_file.new_tag('cite')
    cite_datetime.append(datetime)
    small_datetime.append(cite_datetime)
    div_datetime.append(small_datetime)
    div_empty = html_doc_new_file.new_tag('div')
    div_empty["class"] = "col"
    if (suspect_contact_id == sender_id):
        div_row_datetime.append(div_empty)
        div_row_datetime.append(div_datetime)
    else:
        div_row_datetime.append(div_datetime)
        div_row_datetime.append(div_empty)

    # Reaction
    div_row_reaction = html_doc_new_file.new_tag('div')
    div_row_reaction["class"] = "row"
    div_reaction = html_doc_new_file.new_tag('div')
    if(suspect_contact_id == sender_id):
        div_reaction["class"] = suspect_element_style
    else:
        div_reaction["class"] = victim_element_style
    cite_reaction_sender = html_doc_new_file.new_tag('cite')
    cite_reaction_sender.append(reaction_sender)
    div_reaction.append(reaction + " ")
    div_reaction.append(cite_reaction_sender)
    div_empty = html_doc_new_file.new_tag('div')
    div_empty["class"] = "col"
    if(suspect_contact_id == sender_id):
        div_row_reaction.append(div_empty)
        div_row_reaction.append(div_reaction)
    else:
        div_row_reaction.append(div_reaction)
        div_row_reaction.append(div_empty)
    div_container_fluid_row = html_doc_new_file.new_tag('div')
    div_container_fluid_row["class"] = "row"
    div_row_w100_suspect = html_doc_new_file.new_tag('div')
    div_row_w100_suspect["class"] = "row w-100"
    div_suspect = html_doc_new_file.new_tag('div')
    div_suspect["id"] = "divSuspect"
    div_suspect["class"] = "col mt-3"
    div_row_w100_victim = html_doc_new_file.new_tag('div')
    div_row_w100_victim["class"] = "row w-100"
    div_victim = html_doc_new_file.new_tag('div')
    div_victim["id"] = "divVictim"
    div_victim["class"] = "col mt-3"

    if (suspect_contact_id == sender_id):
        # Avoid all message content repeat just because multiple reactions
        if last_message_id != message_id:
            # Avoid sender name repeat
            if last_sender != sender_id:
                div_suspect.append(div_row_sender)
            div_suspect.append(div_row_message)
            div_suspect.append(div_row_datetime)
            if reaction != 'None':
                div_suspect.append(div_row_reaction)
        else:
            if filename != 'None' and last_filename != filename:
                div_suspect.append(div_row_message)
                div_suspect.append(div_row_datetime)
            if reaction != 'None':
                div_suspect.append(div_row_reaction)
        div_row_w100_suspect.append(div_suspect)
        div_container_fluid_row.append(div_row_w100_suspect)
    else:
        # Avoid all message content repeat just because multiple reactions
        if last_message_id != message_id:
            # Avoid sender name repeat
            if last_sender != sender_id:
                div_victim.append(div_row_sender)
            div_victim.append(div_row_message)
            div_victim.append(div_row_datetime)
            if reaction != 'None':
                div_victim.append(div_row_reaction)
        else:
            if filename != 'None' and last_filename != filename:
                div_victim.append(div_row_message)
                div_victim.append(div_row_datetime)
            if reaction != 'None':
                div_victim.append(div_row_reaction)
        div_row_w100_victim.append(div_victim)
        div_container_fluid_row.append(div_row_w100_victim)

    div_container_fluid.append(div_container_fluid_row)
    return div_container_fluid


def create_message_table_row(html, fields):            
    tr_tag = html.new_tag('tr')
    for field in fields: 
        td_field = html.new_tag('td')
        if str(field).find("<td>") != -1:
            td_field.append(field.text)
        else:
            td_field.append(str(field))
        tr_tag.append(td_field)

    return tr_tag


def handle_empty_messages(html_doc_new_file, fields, td_message):

    thread_key = fields[0]
    attachment_type = fields[1]
    attachment_preview_url = fields[2]
    attachment_playable_url = fields[3]
    attachment_title = fields[4]
    attachment_subtitle = fields[5]
    attachment_url_mimetype = fields[6]
    attachment_filename = fields[7]
    attachment_duration = fields[8]
    depth = fields[9]
    output_path = fields[10]
    MSG_FILES_FOLDER_NAME = fields[11]
    
    # An attachment can be:
    #  - video: (preview_url + url video + title_text + subtitle_text)
    #  - attachment: (preview_url + title_text + subtitle_text + default_attachment_title)
    #  - image (preview_url + title_text + subtitle_text)
    #  - missed call (title_text + subtitle_text)

    # XXX (orainha) O que é xma_rtc?
    if attachment_type == "xma_rtc_ended_video":
        td_message.append("Ended " + attachment_title + " - " + attachment_subtitle)
    elif attachment_type == "xma_rtc_missed_video":
        td_message.append(attachment_title + " at " + attachment_subtitle)
    elif "xma_rtc" in attachment_type:
        td_message.append(attachment_title + " - " + attachment_subtitle)
    # If it hasn't "xma_rtc", it would be something else
    if (depth == "fast"):
        if "image" in attachment_url_mimetype:
            # Get file type
            filetype = utils.get_filetype(attachment_playable_url)
            button_id = attachment_filename + filetype
            button = create_message_download_button(html_doc_new_file, button_id, 
                'btn_download_message_image', attachment_playable_url, "Download Image")
            td_message.append(button)
        elif "audio" in attachment_url_mimetype:
            # Audio filename already has filetype
            filetype = ''
            button = create_message_download_button(html_doc_new_file, attachment_filename, 
                'btn_download_message_file', attachment_playable_url, "Download Audio")
            td_message.append(button)
        elif "video" in attachment_url_mimetype:
            button = create_message_download_button(html_doc_new_file, attachment_filename, 
                'btn_download_message_file', attachment_playable_url, "Download Video")
            td_message.append(button)
        else:
            # Can be gifs, files
            filetype = ''
            if (attachment_filename.find('.') > 0):
                filetype = ''
            else:
                filetype = utils.get_filetype(attachment_playable_url)
                filetype = '.' + filetype
            button_id = attachment_filename + filetype
            button_value = ''
            if (attachment_preview_url != 'None'):
                button_value = attachment_preview_url
            elif (attachment_playable_url != 'None'):
                button_value = attachment_playable_url
            button = create_message_download_button(html_doc_new_file, button_id, 
                'btn_download_message_file', button_value, "Download File")
            td_message.append(button)
    elif (depth == "complete"):   
        if "image" in attachment_url_mimetype:
            filetype = utils.get_filetype(attachment_playable_url)
            extract_message_file(output_path, attachment_preview_url, attachment_filename, filetype, str(thread_key))
            img_tag = html_doc_new_file.new_tag('img')
            img_tag['src'] = f'..\{MSG_FILES_FOLDER_NAME}\{str(thread_key)}\{attachment_filename}{filetype}'
            td_message.append(img_tag)
        elif "audio" in attachment_url_mimetype:
            # Audio filename already has filetype
            filetype = ''
            extract_message_file(output_path, attachment_playable_url, attachment_filename, filetype, str(thread_key))
            href_tag = html_doc_new_file.new_tag('a')
            href_tag['href'] = f'..\{MSG_FILES_FOLDER_NAME}\{str(thread_key)}\{attachment_filename}'
            href_tag['style'] = "color: white"
            href_tag.append("Audio - " + attachment_title + " - " + attachment_subtitle)
            td_message.append(href_tag)
        elif "video" in attachment_url_mimetype:
            filetype = utils.get_filetype(attachment_preview_url)
            extract_message_file(output_path, attachment_preview_url, attachment_filename, filetype, str(thread_key))
            extract_message_file(output_path, attachment_playable_url, attachment_filename, '', str(thread_key))
            img_tag = html_doc_new_file.new_tag('img')
            # Need to add image filetype on this case, filename ends like '.mp4' (not suitable to show an image)
            img_tag['src'] = f'..\{MSG_FILES_FOLDER_NAME}\{str(thread_key)}\{attachment_filename}{filetype}'
            duration = "["+attachment_duration + \
                "s]" if attachment_duration != "None" else ""
            title = " - " + attachment_title if attachment_title != "None" else ""
            subtitle = " - " + attachment_subtitle if attachment_subtitle != "None" else ""
            img_tag.append("Video " + duration + title + subtitle)
            href_tag = html_doc_new_file.new_tag('a')
            # Video filename already has filetype
            href_tag['href'] = f'..\{MSG_FILES_FOLDER_NAME}\{str(thread_key)}\{attachment_filename}'
            href_tag['style'] = "color: white"
            href_tag.append(img_tag)
            td_message.append(href_tag)
        else:
            filetype = ''
            # if filename has his filetype written...
            if (attachment_filename.find('.') > 0):
                filetype = ''
            else:
                filetype = utils.get_filetype(attachment_playable_url)

            if (attachment_preview_url != 'None'):
                extract_message_file(output_path, attachment_preview_url, attachment_filename, filetype, str(thread_key))
                img_tag = html_doc_new_file.new_tag('img')
                img_tag['src'] = f'..\{MSG_FILES_FOLDER_NAME}\{str(thread_key)}\{attachment_filename}{filetype}'
                td_message.append(img_tag)

            elif (attachment_playable_url != 'None'):
                extract_message_file(output_path, attachment_playable_url, attachment_filename, filetype, str(thread_key))
                p_tag = html_doc_new_file.new_tag('p')
                p_tag.append(attachment_filename)
                href_tag = html_doc_new_file.new_tag('a')
                href_tag['href'] = f'..\{MSG_FILES_FOLDER_NAME}\{str(thread_key)}\{attachment_filename}' + '.' + filetype
                href_tag['style'] = "color: white"
                href_tag.append(p_tag)
                td_message.append(href_tag)
    return td_message


def report_html_messages(template_path, depth):

    # Connect to database
    db_path = utils.get_db_path(PATH)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(MESSAGES_PER_CONVERSATION_QUERRY)
    # Variable initialization
    thread_key = 0
    new_thread_key = 1
    last_sender = 0
    last_message_id = 0
    last_attachment_filename = ""
    web_img_url_counter = 0
    button_style_class = "btn btn-outline-light my-2 my-sm-0 fast-button"
    output_path = NEW_FILE_PATH
    for row in cursor:
        # Query fields
        new_thread_key = row[0]
        datetime = str(row[1])
        sender_id = str(row[2])
        sender_name = str(row[3])
        message = str(row[4])
        attachment_preview_url = str(row[5])
        attachment_playable_url = str(row[6])
        attachment_title = str(row[7])
        attachment_subtitle = str(row[8])
        attachment_type = str(row[9])
        attachment_url_mimetype = str(row[10])
        attachment_filename = str(row[11])
        reaction = str(row[12])
        reaction_sender = str(row[13])
        attachment_duration = str(row[14])
        message_id = str(row[15])

        # BeautifulSoup variables
        html_doc_new_file = ""

        has_header = []

        # If is the same conversation as previous..
        if thread_key == new_thread_key:
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
                    # build header
                    if thread_key not in has_header:
                        html_doc_new_file = header(html_doc_new_file,thread_key,depth)
                        has_header.append(thread_key)
                except IOError as error:
                    print(error)
            # Open according file
            new_file = open(new_file_path, 'w', encoding='utf-8')
        try:
            if not message or message == "" or message == 'None':
                fields = [
                    thread_key,
                    attachment_type,
                    attachment_preview_url,
                    attachment_playable_url,
                    attachment_title,
                    attachment_subtitle,
                    attachment_url_mimetype,
                    attachment_filename,
                    attachment_duration,
                    depth,
                    output_path,
                    MSG_FILES_FOLDER_NAME
                    ]
                td_message = html_doc_new_file.new_tag('td')
                td_message = handle_empty_messages(html_doc_new_file, fields, td_message)   
            elif "xma_web_url" in attachment_type:
                filetype = ''
                if (attachment_filename == "None"):
                    attachment_filename = attachment_filename + "(" + str(web_img_url_counter) + ")" + ".jpg"
                    web_img_url_counter = web_img_url_counter + 1
                elif (attachment_filename.find('.') > 0):
                    filetype = ''
                else:
                    filetype = utils.get_filetype(attachment_preview_url)
                a_href_tag = html_doc_new_file.new_tag('a')
                a_href_tag["href"] = attachment_playable_url
                a_href_tag["target"] = "_new"
                a_href_tag["class"] = button_style_class
                a_href_tag["style"] = "color: white"
                a_href_tag.append("Play")
                if (depth == "fast"):
                    a_tag = html_doc_new_file.new_tag('a')
                    a_tag['class'] = button_style_class
                    a_tag['href'] = attachment_preview_url
                    a_tag['target'] = "_new"
                    a_tag.append("View Image")
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(a_tag)
                    if attachment_playable_url != "None":
                        td_message.append(a_href_tag)
                    td_message.append(message + " - " + attachment_title + " - " + attachment_subtitle)
                elif (depth == "complete"):
                    extract_message_file(output_path, attachment_preview_url, attachment_filename, filetype, str(thread_key))
                    img_tag = html_doc_new_file.new_tag('img')
                    img_tag['src'] = f'..\{MSG_FILES_FOLDER_NAME}\{str(thread_key)}\{attachment_filename}{filetype}'
                    td_message = html_doc_new_file.new_tag('td')
                    td_message.append(img_tag)
                    if attachment_playable_url != "None":
                        td_message.append(a_href_tag)
                    td_message.append(message + " - " + attachment_title + " - " + attachment_subtitle)
            else:
                td_message = html_doc_new_file.new_tag('td')
                td_message.append(message)

            # New style

            suspect_contact_id = utils.get_suspect_id(PATH)

            div_container_fluid = html_doc_new_file.new_tag('div')
            if (suspect_contact_id == sender_id):
                div_container_fluid["class"] = "container-fluid w-80 mr-5"
            else:
                div_container_fluid["class"] = "container-fluid w-80 ml-5"

            fields = [
                suspect_contact_id,
                thread_key,
                datetime,
                sender_id,
                sender_name,
                td_message,
                reaction,
                reaction_sender,
                message_id,
                last_message_id, 
                last_sender,
                attachment_filename,
                last_attachment_filename
            ]
            div_container_fluid = create_modern_message_style(html_doc_new_file, fields, div_container_fluid)

            last_sender = sender_id
            last_message_id = message_id
            if (attachment_filename != 'None'):
                last_filename = attachment_filename
            
            html_doc_new_file.table.insert_before(div_container_fluid)

            # Old Style                

            tr_tag = html_doc_new_file.new_tag('tr')

            # Atention to field order. It must match the template_messages table headers
            fields = [
                thread_key,
                datetime,
                sender_id,
                sender_name,
                td_message,
                attachment_filename,
                attachment_playable_url,
                attachment_url_mimetype,
                attachment_type,
                reaction,
                reaction_sender,
                message_id
            ]
            tr_tag = create_message_table_row(html_doc_new_file, fields)

            html_doc_new_file.table.tbody.append(tr_tag)

            new_file.seek(0)
            new_file.write(html_doc_new_file.prettify())
            new_file.truncate()

            # Close file
            new_file.close()
        except IOError as error:
            print(error)


def build_conversations_div_row(html, div_conversation_group, thread_key):
    p_tag = html.new_tag('p')
    p_tag["class"] = "mt-4 ml-2"
    strong_tag = html.new_tag('strong')
    strong_tag.append(f"Conversation {str(thread_key)}")
    p_tag.append(strong_tag)
    div_conversation = html.new_tag('div')
    div_conversation["class"] = "row"
    conversation = p_tag
    div_conversation.append(conversation)
    div_conversation_group["id"] = str(thread_key)
    div_conversation_group.append(div_conversation)


def build_conversations_profile_pic(html, participant_pic, participant_contact_id, participant_large_pic, div_col_left, depth, td_photo):
    filetype = utils.get_filetype(participant_pic)
    if (depth == "fast"):
        button_tag = html.new_tag('button')
        button_tag['id'] = str(participant_contact_id) + filetype
        button_tag['class'] = 'btn_download_conversation_contact_image btn btn-outline-dark my-2 my-sm-0 fast-button pb-2'
        button_tag['value'] = participant_large_pic
        button_tag.append('Download Image')
        td_photo.append(button_tag)
    elif (depth == "complete"):
        href_tag = html.new_tag('a')
        href_tag['href'] = f'conversations\images\large\{participant_contact_id}' + filetype
        img_tag = html.new_tag('img')
        img_tag['src'] = f'conversations\images\small\{participant_contact_id}' + filetype
        img_tag['id'] = 'imgParticipant'
        href_tag.append(img_tag)
        td_photo.append(href_tag)
    return td_photo


def build_conversations_name(html_doc_new_file, thread_key, participant_name, div_col_right, depth, td_name):
    href_msgs_tag = html_doc_new_file.new_tag('a')
    href_msgs_tag["href"] = f'messages\{str(thread_key)}.html'
    href_msgs_tag["target"] = "targetframemessages"
    href_msgs_tag.append(str(participant_name))
    td_name.append(href_msgs_tag)
    return td_name


def report_html_conversations(template_path, depth):
    # Connect to database
    db_path = utils.get_db_path(PATH)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(CONVERSATIONS_QUERRY)
    results = c.fetchall()
    results_lenght = len(results)

    # Get template
    template_file = open(template_path, 'r', encoding='utf-8')
    html_doc_new_file = BeautifulSoup(template_file, features='html.parser')
    new_file = open(NEW_FILE_PATH + "conversations.html",
                    'w', encoding='utf-8')

    # Variable initialization
    thread_key = 0
    suspect_contact_id = utils.get_suspect_id(PATH)

    div_container_fluid = html_doc_new_file.new_tag('div')
    div_container_fluid["id"] = "divConversations"
    div_container_fluid["class"] = "container-fluid"

    extract_conversation_list = list()
    for i, row in enumerate(results):
        # Query fields
        participant_pic = str(row[0])
        participant_name = str(row[1])
        participant_large_pic = str(row[2])
        new_thread_key = row[3]
        participant_contact_id = row[4]
        participant_nickname = str(row[5])

        # # If is a new conversation..
        if thread_key != new_thread_key:
            div_conversation_group = html_doc_new_file.new_tag('div')
            div_conversation_group["class"] = "container-fluid conversation-group"
            thread_key = new_thread_key
            build_conversations_div_row(html_doc_new_file, div_conversation_group, thread_key)
        
        # Div skeleton
        div_row_col = html_doc_new_file.new_tag('div')
        div_row_col["class"] = "row mt-2"
        div_col_left = html_doc_new_file.new_tag('div')
        div_col_left["class"] = "col text-right"
        div_col_right = html_doc_new_file.new_tag('div')
        div_col_right["class"] = "col text-left mt-3"

        # Table will not be visible, but its needed for csv export
        # td 1 - Profile Pic
        if (depth == "complete"):
            filetype = utils.get_filetype(participant_pic)
            conversation = [NEW_FILE_PATH, participant_pic, participant_large_pic, filetype, str(participant_contact_id)]
            extract_conversation_list.append(conversation)
        td_photo = html_doc_new_file.new_tag('td')
        td_photo["class"] = "col-md-2 text-right pr-1"
        td_photo = build_conversations_profile_pic(html_doc_new_file, participant_pic, 
                            participant_contact_id, participant_large_pic, 
                            div_col_left, depth, td_photo)
        photo = copy.copy(td_photo)

        # td 2 - Name
        td_name = html_doc_new_file.new_tag('td')
        td_name = build_conversations_name(html_doc_new_file, thread_key, participant_name, div_col_right, depth, td_name)
        name = copy.copy(td_name)
        
        # td 3 - Thread Key
        td_thread_key = html_doc_new_file.new_tag('td')
        td_thread_key.append(str(new_thread_key))

        # td 4 - Contact Id
        td_contact_id = html_doc_new_file.new_tag('td')
        td_contact_id.append(str(participant_contact_id))

        # td 5 - Nickname
        td_nickname = html_doc_new_file.new_tag('td')
        td_nickname.append(str(participant_nickname))

        tr_tag_data = html_doc_new_file.new_tag('tr')
        tr_tag_data.append(td_photo)
        tr_tag_data.append(td_name)
        tr_tag_data.append(td_thread_key)
        tr_tag_data.append(td_contact_id)
        tr_tag_data.append(td_nickname)

        html_doc_new_file.table.tbody.append(tr_tag_data)
        
        # This is what will be visible
        if (str(participant_contact_id) != str(suspect_contact_id)):
            div_col_left.append(photo)
            div_col_right.append(name)
            div_row_col.append(div_col_left)
            div_row_col.append(div_col_right)
            div_empty_1 = html_doc_new_file.new_tag('div')
            div_empty_1["class"] = "col"
            div_empty_2 = html_doc_new_file.new_tag('div')
            div_empty_2["class"] = "col"
            div_row_col.append(div_empty_1)
            div_row_col.append(div_empty_2)

            div_conversation_group.append(div_row_col)

            # Check if isnt the last row
            if (i < results_lenght-2):
                next_thread_key = results[i + 2][3]
                if next_thread_key != thread_key:
                    div_container_fluid.append(div_conversation_group)
            if (results_lenght == i + 2):
                div_container_fluid.append(div_conversation_group)

    html_doc_new_file.table.insert_before(div_container_fluid)
    
    new_file.seek(0)
    new_file.write(html_doc_new_file.prettify())
    new_file.truncate()
    if (depth == "complete"):
        extract_images(extract_conversation_list)


def report_csv_conversations(delim):
    db_path = utils.get_db_path(PATH)
    with sqlite3.connect(db_path) as connection:
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
    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=delim, quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow(columns)
        writer.writerows(rows)


def report_csv_messages(delim):
    db_path = utils.get_db_path(PATH)
    with sqlite3.connect(db_path) as connection:
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
        thread_messages_list = list()
        thread_messages = filter(lambda row: (
            row[thread_idx] == thread), msg_rows)
        # XXX (ricardoapl) Remove reference to MESSAGES_PATH?
        filename = MESSAGES_PATH + str(thread) + '.csv'
        with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=delim, quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(columns)

            message_index = 4
            title_text_index = 7
            subtitle_text_index = 8
            for row in thread_messages:
                row = replace_enter_by_space(row, message_index, title_text_index, subtitle_text_index)
                thread_messages_list.append(row)
            writer.writerows(thread_messages_list)


def report_csv(delim):
    report_csv_conversations(delim)
    report_csv_messages(delim)


def paths(args):
    input_file_path(args.input)
    output_file_path(args.output)


def input_file_path(user_path):
    # XXX (orainha) Procurar por utilizadores dando apenas o drive?
    global PATH
    PATH = utils.get_input_file_path(user_path)


def output_file_path(destination_path):
    global NEW_FILE_PATH
    global MESSAGES_PATH
    NEW_FILE_PATH = utils.get_output_file_path(destination_path)
    MESSAGES_PATH = NEW_FILE_PATH + "messages\\"
    try:
        if os.path.exists(MESSAGES_PATH):
            shutil.rmtree(MESSAGES_PATH)
        if not os.path.exists(MESSAGES_PATH):
            os.makedirs(MESSAGES_PATH)
    except IOError as error:
        print(error)
        sys.exit()


def extract_message_file(path, url, filename, filetype, msg_thread_key):
    global MSG_FILES_FOLDER_NAME
    MSG_FILES_FOLDER_NAME = 'message-files'
    images_path = path + f'{MSG_FILES_FOLDER_NAME}\{msg_thread_key}'
    utils.extract(path, images_path, url, filename, filetype)


def extract_images(extract_conversation_list):
    small_images_path = NEW_FILE_PATH + f'conversations\images\small'
    large_images_path = NEW_FILE_PATH + f'conversations\images\large'
    if not os.path.exists(small_images_path):
        os.makedirs(small_images_path)
    if not os.path.exists(large_images_path):
        os.makedirs(large_images_path)
    threads = list()
    for conversation in extract_conversation_list:
        new_file_path = conversation[0]
        small_pic = conversation[1]
        large_pic = conversation[2]
        filetype = conversation[3]
        id = conversation[4]
        x = threading.Thread(target=utils.extract, args=(new_file_path, small_images_path, small_pic, id, filetype,))
        x1 = threading.Thread(target=utils.extract, args=(new_file_path, large_images_path, large_pic, id, filetype,))
        threads.append(x)
        threads.append(x1)
        x.start()
        x1.start()
    for thread in threads:
        thread.join()


def replace_enter_by_space(row, *indexes):

    for index in indexes:
        if str(row[index]).find('\n') > 0:
            row_list = list()
            for i, item in enumerate(row):
                if i == index:
                    item = str(row[i]).replace('\n', ' ')
                row_list.append(item)
            row = tuple(row_list)
    return row