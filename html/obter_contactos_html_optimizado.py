import sys
from pathlib import Path
import webbrowser
import sqlite3

# CONSTANTS

CONTACTS_TEMPLATE_FILE_PATH = "html_contacts_template.html"

NEW_FILE_PATH = str(Path.home()) + "\\AppData\\Local\\Temp\\"
DB_PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\msys_709212107.db"

CONTACTS_QUERRY = "SELECT c.id, c.profile_picture_url, c.name, u.phone_number, u.email_address, c.profile_picture_large_url \
          FROM contacts as c \
               JOIN user_contact_info as u ON c.id = u.contact_id \
          ORDER BY c.name"



# FUNCTIONS

def function_html_contacts_file(template_path, new_file_path):

    try:
        #get template
        template_file = open(template_path, 'r')
        new_file = open(new_file_path + "contacts.html", 'w')

        #get the right place to write
        for line in template_file:
            start_line_index = line.find("</table>")

            #if find the string..
            if start_line_index > 0:
                #write all contacts on the right spot
                function_write_contacts_to_html(DB_PATH, new_file)
            
            #write file till the end..
            new_file.write(line)
        
        #close files / good practice
        template_file.close()
        new_file.close()

    except IOError as error:
        print (error)


def function_write_contacts_to_html(database_path, obj_file):

    #connect to database
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute(CONTACTS_QUERRY)

    #variable initialization
    contact_counter = 1

    for row in c:
        #querry fields
        contact_id = str(row[0])
        contact_pic = str(row[1])
        contact_name = str(row[2])
        contact_phone = str(row[3])
        contact_email = str(row[4])
        contact_large_pic = str(row[5])

        #set default values to 'None' values
        if contact_phone == 'None':
            contact_phone = "No Phone"
        if contact_email == 'None':
            contact_email = "No Email"

        try:
            obj_file.write("""
                <tr>
                    <td>"""  +str(contact_counter) + """</td>
                    <td><a href=\'"""+ str(contact_large_pic) +"""\'><img src=\'""" + str(contact_pic) + """\'></img></a></td>
                    <!--<td>""" + str(contact_name) + """ </br>""" + str(contact_email) + """</br>""" + str(contact_phone) + """</td>-->
                    <td>""" + str(contact_name) + """</td>
                    <td>""" + str(contact_email) + """</td>
                    <td>""" + str(contact_phone) + """</td>
                </tr>
            """)
            contact_counter = contact_counter + 1
        except IOError as error:
            print (error)
            break



# MAIN

try:
    function_html_contacts_file(CONTACTS_TEMPLATE_FILE_PATH, NEW_FILE_PATH)
    webbrowser.open_new_tab(NEW_FILE_PATH + 'contacts.html')
except IOError as error:
    print (error)
