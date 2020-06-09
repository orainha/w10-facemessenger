import os
import sys
import shutil
import csv
import json
import sqlite3
# TODO (orainha) Fix requests import!
import requests
import threading 
# XXX (orainha) How to use the word "threading" importing this way?
from threading import * 

from bs4 import BeautifulSoup

from core.headers import fill_header

import utils.files as utils



# XXX (ricardoapl) Fix this non-pythonic mess!
CONTACTS_TEMPLATE_FILE_PATH = os.path.join(os.path.dirname(__file__), r'..\templates\template_contacts.html')
NEW_FILE_PATH = ''
PATH = ''
DB_PATH = ''
CONTACTS_QUERRY = """
    SELECT
        id,
        profile_picture_url,
        name,
        phone_number,
        email_address,
        profile_picture_large_url
    FROM contacts
    ORDER BY name
"""


class ContactsCollector(Thread):
    def __init__(self):
        pass


def report_html(depth):
    global NEW_FILE_PATH
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(CONTACTS_QUERRY)

    # Get template and create new file
    template_file = open(CONTACTS_TEMPLATE_FILE_PATH, 'r', encoding='utf-8')
    html_doc_new_file = BeautifulSoup(template_file, features='html.parser')
    new_file = open(NEW_FILE_PATH + "contacts.html", 'w', encoding='utf-8')
    template_file.close()
    extract_contact_list = list()
    for row in c:
        # Query fields
        contact_id = str(row[0])
        contact_pic = str(row[1])
        contact_name = str(row[2])
        contact_phone = str(row[3])
        contact_email = str(row[4])
        contact_large_pic = str(row[5])
        # Set default values to 'None'
        if contact_phone == 'None':
            contact_phone = "No Phone"
        if contact_email == 'None':
            contact_email = "No Email"
        threads = list()
        try:
            tr_tag = html_doc_new_file.new_tag('tr')
            # td 1
            td_id = html_doc_new_file.new_tag('td')
            td_id.append(contact_id)
            # td 2
            filetype = utils.get_filetype(contact_large_pic)
            if (depth == 'fast'):
                td_download_photo = html_doc_new_file.new_tag('td')
                button_tag = html_doc_new_file.new_tag('button')
                button_tag['id'] = str(contact_id) + filetype
                button_tag['class'] = 'btn_download_contact_image btn btn-outline-dark my-2 my-sm-0'
                button_tag['value'] = contact_large_pic
                button_tag.append('Download Image')
                td_download_photo.append(button_tag)
            elif (depth == 'complete'):
                # Download images later
                contact = [NEW_FILE_PATH, contact_pic, contact_large_pic, contact_id, filetype]
                extract_contact_list.append(contact)
                td_photo = html_doc_new_file.new_tag('td')
                href_tag = html_doc_new_file.new_tag('a')
                href_tag['href'] = f'contacts\images\large\{contact_id}{filetype}'
                img_tag = html_doc_new_file.new_tag('img')
                img_tag['src'] = f'contacts\images\small\{contact_id}{filetype}'
                img_tag['id'] = 'imgContact'
                href_tag.append(img_tag)
                td_photo.append(href_tag)
            # td 3
            td_name = html_doc_new_file.new_tag('td')
            td_name.append(str(contact_name))
            # td 4
            td_email = html_doc_new_file.new_tag('td')
            td_email.append(str(contact_email))
            # td 5
            td_phone = html_doc_new_file.new_tag('td')
            td_phone.append(str(contact_phone))
            
            # tr append
            tr_tag.append(td_id)

            if (depth == 'fast'):
                tr_tag.append(td_download_photo)
            elif (depth == 'complete'):
                tr_tag.append(td_photo)

            tr_tag.append(td_name)
            tr_tag.append(td_email)
            tr_tag.append(td_phone)
            html_doc_new_file.table.tbody.append(tr_tag)
        except IOError as error:
            print(error)
            break
    new_file.seek(0)
    new_file.write(html_doc_new_file.prettify())
    new_file.truncate()
    new_file.close()
    if (depth == 'complete'):
        extract_images(extract_contact_list)


def report_csv(delim):
    # XXX (ricardoapl) Remove reference to DB_PATH?
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(CONTACTS_QUERRY)
        rows = cursor.fetchall()
        cursor.close()
    # XXX (ricardoapl) Careful! Columns is highly dependant on the query,
    #     if we change query we also have to change columns.
    columns = [
        'Id',
        'Small Profile Picture',
        'Name',
        'Phone',
        'Email',
        'Large Profile Picture'
    ]
    # XXX (ricardoapl) Remove reference to NEW_FILE_PATH?
    filename = NEW_FILE_PATH + 'contacts.csv'
    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=delim, quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow(columns)
        writer.writerows(rows)

def paths(args):
    input_file_path(args.input)
    output_file_path(args.output)

def input_file_path(user_path):
    # XXX (orainha) Procurar por utilizadores dando apenas o drive?
    global PATH
    global DB_PATH
    PATH = utils.get_input_file_path(user_path)
    DB_PATH = utils.get_db_path(PATH)


def output_file_path(destination_path):
    global NEW_FILE_PATH
    NEW_FILE_PATH = utils.get_output_file_path(destination_path)

def extract_images(extract_contacts_list):
    small_images_path = NEW_FILE_PATH + f'contacts\images\small'
    large_images_path = NEW_FILE_PATH + f'contacts\images\large'
    if not os.path.exists(small_images_path):
        os.makedirs(small_images_path)
    if not os.path.exists(large_images_path):
        os.makedirs(large_images_path)
    threads = list()
    for contact in extract_contacts_list:
        new_file_path = contact[0]
        small_pic = contact[1]
        large_pic = contact[2]
        id = contact[3]
        filetype = contact[4]
        x = threading.Thread(target=utils.extract, args=(new_file_path, small_images_path, small_pic, id, filetype,))
        x1 = threading.Thread(target=utils.extract, args=(new_file_path, large_images_path, large_pic, id, filetype,))
        threads.append(x)
        threads.append(x1)
        x.start()
        x1.start()
    for thread in threads:
        thread.join()
