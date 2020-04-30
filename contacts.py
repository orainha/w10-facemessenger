import sys
import os
import shutil
import json
import sqlite3
import webbrowser
from pathlib import Path
from headers import fill_header
from bs4 import BeautifulSoup
import argparse

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

# XXX Get id present in db file name
# TODO Extract into common method

def create_js_files():
    # XXX Duplicate from messages.py
    try:
        if not os.path.exists(NEW_FILE_PATH + "\js"):
            os.makedirs(NEW_FILE_PATH + "\js")
        shutil.copy2('templates\js\export-to-csv.js', NEW_FILE_PATH + "\js")
    except IOError as error:
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

    # variable initialization
    contact_counter = 1
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
            td_id.append(str(contact_counter))
            td_photo = html_doc_new_file.new_tag('td')
            href_tag = html_doc_new_file.new_tag('a')
            href_tag['href'] = str(contact_large_pic)
            img_tag = html_doc_new_file.new_tag('img')
            img_tag['src'] = str(contact_pic)
            href_tag.append(img_tag)
            td_photo.append(href_tag)
            td_name = html_doc_new_file.new_tag('td')
            td_name.append(str(contact_name))
            td_email = html_doc_new_file.new_tag('td')
            td_email.append(str(contact_email))
            td_phone = html_doc_new_file.new_tag('td')
            td_phone.append(str(contact_phone))
            tr_tag.append(td_id)
            tr_tag.append(td_photo)
            tr_tag.append(td_name)
            tr_tag.append(td_email)
            tr_tag.append(td_phone)
            html_doc_new_file.table.append(tr_tag)
            contact_counter = contact_counter + 1
        except IOError as error:
            print(error)
            break
    new_file.seek(0)
    new_file.write(html_doc_new_file.prettify())
    new_file.truncate()
    new_file.close()   

def export_to_csv(delimiter):   
    print ("Exported to CSV with delimiter: " + delimiter)

def input_file(path):
    #todo: procurar por utilizadores dando apenas o drive?
    global DB_PATH
    #get full path
    PATH = path + f'\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\'
    #get db file name
    try:
        if os.path.exists(PATH):
            auth_id = 0
            #print (PATH+'data')
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

def output_file(path):
    global NEW_FILE_PATH 
    path = os.path.expandvars(path)
    NEW_FILE_PATH = path + "\\report\\"
    try:
        if not os.path.exists(path):
            raise IOError ("Error: Given destination output path not found")
        if not os.path.exists(NEW_FILE_PATH):
            os.makedirs(NEW_FILE_PATH)
        #print (f'Report files saved on: {NEW_FILE_PATH}')
    except IOError as error:
        print(error)
        exit()

def load_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e','--export', choices=['csv'], help='Export to %(choices)s')
    parser.add_argument('-d','--delimiter', choices=[',','»','«'], help='Delimiter to csv')
    #parser.add_argument('-src','--source', help='Windows user path. Usage %(prog)s -src C:\Users\User', required=True)
    #parser.add_argument('-dst','--destination', default=r'%USERPROFILE%\Desktop', help='Save report path')
    parser.add_argument('-i','--input', help=r'Windows user path. Usage %(prog)s -src C:\Users\User', required=True)
    parser.add_argument('-o','--output', default=r'%USERPROFILE%\Desktop', help='Save report path')

    args = parser.parse_args()
    
    export_options = {"csv" : export_to_csv}
    file_options = {"input" : input_file, "output" : output_file}

    for arg, value in vars(args).items():
        if value is not None and arg=='export':
            delimiter = args.delimiter if args.delimiter is not None else ','
            export_options[value](delimiter)
        elif value is not None and arg!='delimiter':
            file_options[arg](value)

def main():
    load_command_line_arguments()
    create_js_files()
    function_html_contacts_file(DB_PATH, CONTACTS_TEMPLATE_FILE_PATH)
    fill_header(DB_PATH, NEW_FILE_PATH + 'contacts.html')
    webbrowser.open_new_tab(NEW_FILE_PATH + 'contacts.html')

if __name__ == '__main__':
    main()