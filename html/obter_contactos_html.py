import webbrowser
from pathlib import Path
import sqlite3

# CONSTANTS

NEW_FILE = str(Path.home()) + "\\AppData\\Local\\Temp\\"
DB_PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\msys_709212107.db"
#DB_PATH = "C:\\Users\\user\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\msys_709212107.db"
#DB_PATH = "C:\\Users\\user\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\msys_709212107.db"
#QUERRY = "SELECT * FROM user_contact_info"
QUERRY = "SELECT c.id, c.profile_picture_url, c.name, u.phone_number, u.email_address, c.profile_picture_large_url \
          FROM contacts as c \
               JOIN user_contact_info as u ON c.id = u.contact_id \
          ORDER BY c.name"
STDOUT_ALL_OK = "Contact file successfuly created"

# FUNCTIONS
def printContacts(messengerDB):

    #connect to database
    conn = sqlite3.connect(messengerDB)
    c = conn.cursor()
    c.execute(QUERRY)

    #variable initialization
    contact_counter = 1
    html_header = """
    <!DOCTYPE html>
    <html>
    <head>
    </head>
    <body>
        <table>    
            <th>Id</th>
            <th>Photo</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>"""
    html_footer ="""</table></body></html>"""


    f = open(NEW_FILE + 'contacts.html','w+')
    f.write(html_header)

    for row in c:
        #querry fields
        contact_id = str(row[0])
        contact_pic = str(row[1])
        contact_name = str(row[2])
        contact_phone = str(row[3])
        contact_email = str(row[4])
        contact_large_pic = str(row[5])

        if contact_phone == 'None':
            contact_phone = "No Phone"
        if contact_email == 'None':
            contact_email = "No Email"

        try:

            f.write("""
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
    f.write(html_footer)
    f.close()


# MAIN

try:
   printContacts(DB_PATH)
   webbrowser.open_new_tab(NEW_FILE + 'contacts.html')
except IOError as error:
    print (error)
finally:
   print (STDOUT_ALL_OK)

