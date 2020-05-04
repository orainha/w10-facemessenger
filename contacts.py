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
from downloads import download_contact_images

#NEW_FILE_PATH = os.path.expandvars(r'%TEMP%\\')
#PATH = os.path.expandvars(r'%LOCALAPPDATA%\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\')
CONTACTS_TEMPLATE_FILE_PATH = r'templates\template_contacts.html'
NEW_FILE_PATH = ''
PATH = ''
DB_PATH = ''

CONTACTS_QUERRY = """
    SELECT id, profile_picture_url, name, phone_number, email_address, profile_picture_large_url
    FROM contacts
    ORDER BY name
    """

def create_miscellaneous_files():
    try:
        if not os.path.exists(NEW_FILE_PATH + "\misc"):
             os.makedirs(NEW_FILE_PATH + "\misc")
        js_files = os.listdir('templates\misc\\')
        for filename in js_files:
            shutil.copy2('templates\misc\\' + filename, NEW_FILE_PATH + "\misc")
    except OSError as error:
        print(error)

def create_js_files():
    # XXX Duplicate from messages.py
    try:
        if not os.path.exists(NEW_FILE_PATH + "\js"):
             os.makedirs(NEW_FILE_PATH + "\js")
        js_files = os.listdir('templates\js\\')
        for filename in js_files:
            shutil.copy2('templates\js\\' + filename, NEW_FILE_PATH + "\js")
    except OSError as error:
        print(error)

def function_html_contacts_file(database_path, template_path):
    global NEW_FILE_PATH
    # connect to database
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute(CONTACTS_QUERRY)

    #get template and create new file
    template_file = open(template_path, 'r', encoding='utf-8')
    html_doc_new_file = BeautifulSoup(template_file, features='html.parser')
    new_file = open(NEW_FILE_PATH + "contacts.html", 'w', encoding='utf-8')
    template_file.close()
    
    for row in c:
        # querry fields
        contact_id = str(row[0])
        contact_pic = str(row[1])
        contact_name = str(row[2])
        contact_phone = str(row[3])
        contact_email = str(row[4])
        contact_large_pic = str(row[5])
        # set default values to 'None'
        if contact_phone == 'None':
            contact_phone = "No Phone"
        if contact_email == 'None':
            contact_email = "No Email"
        try:
            tr_tag = html_doc_new_file.new_tag('tr')
            td_id = html_doc_new_file.new_tag('td')
            td_id.append(contact_id)
            td_photo = html_doc_new_file.new_tag('td')
            href_tag = html_doc_new_file.new_tag('a')
            href_tag['href'] = str(contact_large_pic)
            #1) start html with links (download all images)
            # p_img_tag = html_doc_new_file.new_tag('p')
            # p_img_tag['class'] = 'img_url'
            # p_img_tag.append(str(contact_pic))
            # href_tag.append(p_img_tag)
            #end 1)
            #2) start html with images (download image one by one)
            img_tag = html_doc_new_file.new_tag('img')
            img_tag['src'] = str(contact_pic)
            href_tag.append(img_tag)
            #end 2)
            td_photo.append(href_tag)
            td_name = html_doc_new_file.new_tag('td')
            td_name.append(str(contact_name))
            td_email = html_doc_new_file.new_tag('td')
            td_email.append(str(contact_email))
            td_phone = html_doc_new_file.new_tag('td')
            td_phone.append(str(contact_phone))
            #2) start html with images (download images one by one)
            td_btn = html_doc_new_file.new_tag('td')
            button_tag = html_doc_new_file.new_tag('button')
            button_tag['id'] = contact_id
            button_tag['class'] = 'download_image'
            button_tag['value'] = str(contact_large_pic)
            button_tag.append('Download Image')
            td_btn.append(button_tag)
            #end 2)
            tr_tag.append(td_id)
            tr_tag.append(td_photo)
            tr_tag.append(td_name)
            tr_tag.append(td_email)
            tr_tag.append(td_phone)
            #2) start html with images (download images one by one)
            tr_tag.append(td_btn)
            #end 2)
            html_doc_new_file.table.append(tr_tag)
        except IOError as error:
            print(error)
            break
    new_file.seek(0)
    new_file.write(html_doc_new_file.prettify())
    new_file.truncate()
    new_file.close()   

def export_csv(delim):
    # XXX (ricardoapl) Remove reference to DB_PATH?
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(CONTACTS_QUERRY)
        rows = cursor.fetchall()
        cursor.close()
    # XXX (ricardoapl) Careful! Columns is highly dependant on the query,
    #     if we change query we also have to change columns.
    columns = [
        'id',
        'profile_picture_url',
        'name',
        'phone_number',
        'email_address',
        'profile_picture_large_url'
    ]
    # XXX (ricardoapl) Remove reference to NEW_FILE_PATH?
    filename = NEW_FILE_PATH + 'contacts.csv'
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=delim, quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow(columns)
        writer.writerows(rows)

def input_file_path(path):
    #TODO: procurar por utilizadores dando apenas o drive?
    global DB_PATH
    #get full path
    PATH = path + f'\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\'
    # XXX (ricardoapl) Get id present in db file name
    # TODO (ricardoapl) Extract into common method
    try:
        if os.path.exists(PATH):
            auth_id = 0
            f_data = open(PATH + 'data', 'r')
            data = json.load(f_data)
            for item in data:
                txt = item.split(":")
                auth_id = txt[1]
                break
            db_file_name = "msys_" + auth_id + ".db"
            DB_PATH = PATH + db_file_name
        else:
            raise IOError("Error: File not found on given path")
    except IOError as error:
        print(error)
        exit()

def output_file_path(path):
    global NEW_FILE_PATH 
    path = os.path.expandvars(path)
    NEW_FILE_PATH = path + "\\report\\"
    try:
        if not os.path.exists(path):
            raise IOError ("Error: Given destination output path not found")
        if not os.path.exists(NEW_FILE_PATH):
            os.makedirs(NEW_FILE_PATH)
    except IOError as error:
        print(error)
        exit()

def load_command_line_arguments():
    # TODO (ricardoapl) This method should only be responsible for parsing, not execution!
    parser = argparse.ArgumentParser()
    group1 = parser.add_argument_group('mandatory arguments')
    group1.add_argument('-i','--input', help=r'Windows user path. Usage: %(prog)s -i C:\Users\User', required=True)
    parser.add_argument('-o','--output', default=r'%USERPROFILE%\Desktop', help='Output destination path')
    parser.add_argument('-e','--export', choices=['csv'], help='Export to %(choices)s')
    parser.add_argument('-d','--delimiter', choices=[',','»','«'], help='Delimiter to csv')
    #parser.add_argument('-src','--source', help='Windows user path. Usage %(prog)s -src C:\Users\User', required=True)
    #parser.add_argument('-dst','--destination', default=r'%USERPROFILE%\Desktop', help='Save report path')

    args = parser.parse_args()
    
    export_options = {"csv" : export_csv}
    file_options = {"input" : input_file_path, "output" : output_file_path}

    # XXX (ricardoapl) Careful! The way this is, execution is dependant on parsing order!
    for arg, value in vars(args).items():
        if value is not None and arg=='export':
            delimiter = args.delimiter if args.delimiter is not None else ','
            export_options[value](delimiter)
        elif value is not None and arg!='delimiter':
            file_options[arg](value)

def main():
    # TODO (ricardoapl) HTML report is only created if the user requests it (see cmdline args)
    load_command_line_arguments()
    create_js_files()
    create_miscellaneous_files()
    function_html_contacts_file(DB_PATH, CONTACTS_TEMPLATE_FILE_PATH)
    #1) start html with links (download all images)
    #download_contact_images(NEW_FILE_PATH)
    #end 1)
    fill_header(DB_PATH, NEW_FILE_PATH + 'contacts.html')
    webbrowser.open_new_tab(NEW_FILE_PATH + 'contacts.html')

if __name__ == '__main__':
    main()