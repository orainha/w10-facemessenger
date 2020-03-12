from django.http import HttpResponse
from django.shortcuts import render

from .models import Contact

import sqlite3

DB_PATH = "C:\\Users\\user\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\msys_709212107.db"
QUERRY = "SELECT * FROM user_contact_info"

# Create your views here.
def contact_view(request):
    #return HttpResponse("<h1>Hello W</h1>")
    #connect to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(QUERRY)

    #variable initialization
    thread_key = 0
    new_thread_key = 1
    file_write = ""
    contact_counter = 1
    context = []

    for row in c:
        #querry fields
        contact_id = str(row[0]) 
        contact_name = str(row[1])
        contact_phone = str(row[2])
        contact_email = str(row[3])
      

        #new_file = CONTACT_PATH
        #contacts[contact_counter] = contact
        
        #context[str(contact_counter)] = contact
        #context.update({'Number': str(contact_counter), 'Name': str(contact_name), 'Phone':  str(contact_phone), 'Email': str(contact_email)})
        context.append({'Number': str(contact_counter), 'Name': str(contact_name), 'Phone':  str(contact_phone), 'Email': str(contact_email)})
    
        contact_counter = contact_counter + 1 


    return render(request , "contact/contacts.html", {'data': context})
