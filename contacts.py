import sys
import os
import shutil
import json
import sqlite3
import webbrowser
from pathlib import Path
from headers import fill_header

CONTACTS_TEMPLATE_FILE_PATH = r'templates\template_contacts.html'
NEW_FILE_PATH = os.path.expandvars(r'%TEMP%\\')
PATH = os.path.expandvars(r'%LOCALAPPDATA%\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\')
CONTACTS_QUERRY = "SELECT c.id, c.profile_picture_url, c.name, u.phone_number, u.email_address, c.profile_picture_large_url \
    FROM contacts as c JOIN user_contact_info as u ON c.id = u.contact_id \
    ORDER BY c.name"

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

def create_js_files():
    # XXX Duplicate from messages.py
    try:
        if not os.path.exists(NEW_FILE_PATH + "\js"):
            os.makedirs(NEW_FILE_PATH + "\js")
        shutil.copy2('templates\js\export-to-csv.js', NEW_FILE_PATH + "\js")
    except IOError as error:
        print(error)

def function_html_contacts_file(template_path, new_file_path):
    try:
        # get template
        template_file = open(template_path, 'r')
        new_file = open(new_file_path + "contacts.html", 'w')
        # get the right place to write
        for line in template_file:
            start_line_index = line.find("</table>")
            # if find the string...
            if start_line_index > 0:
                # write all contacts on the right spot
                function_write_contacts_to_html(DB_PATH, new_file)
            # write file till the end...
            new_file.write(line)
        template_file.close()
        new_file.close()
    except IOError as error:
        print(error)

def function_write_contacts_to_html(database_path, obj_file):
    # connect to database
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute(CONTACTS_QUERRY)
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
            obj_file.write("""
                <tr>
                    <td>""" + str(contact_counter) + """</td>
                    <td><a href=\'""" + str(contact_large_pic) + """\'><img src=\'""" + str(contact_pic) + """\'></img></a></td>
                    <!--<td>""" + str(contact_name) + """ </br>""" + str(contact_email) + """</br>""" + str(contact_phone) + """</td>-->
                    <td>""" + str(contact_name) + """</td>
                    <td>""" + str(contact_email) + """</td>
                    <td>""" + str(contact_phone) + """</td>
                </tr>
            """)
            contact_counter = contact_counter + 1
        except IOError as error:
            print(error)
            break

def main():
    create_js_files()
    function_html_contacts_file(CONTACTS_TEMPLATE_FILE_PATH, NEW_FILE_PATH)
    fill_header(DB_PATH, NEW_FILE_PATH + 'contacts.html')
    webbrowser.open_new_tab(NEW_FILE_PATH + 'contacts.html')

if __name__ == '__main__':
    main()