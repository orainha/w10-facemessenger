import csv
from pathlib import Path
import requests


PATH = str(Path.home()) + "\\AppData\\Local\\Temp\\"


try:

    #create csv
    csvfile =  open('contacts.csv', 'w', newline='')
    fieldnames = ['index', 'photo', 'name', 'email', 'phone']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    # writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
    # writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
    # writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})

    #get html file
    html_file = open(PATH + "contacts.html", 'r')
    
    #variable declare
    found_tr = 0 #flag to seperate multiple <td> by <tr>
    td_counter = 0
    row = {}

    for line in html_file:
        #find table rows
        start_line_index = line.find("<tr>")

        #if find the row..
        if start_line_index > 0:
            found_tr = 1
            #we want the <td>, on the next line
            continue

        elif found_tr > 0:
            #we are on a <td> line now..

            #while not reach </tr>, do:
            if line.find("</tr>") <= 0:
                #get text between <td> and </td>
                start_row = line.find("<td>")               
                if start_row > 0:
                    end_row = line.find("</td>")

                    #<td> on proper fieldname order
                    field = fieldnames[td_counter]
                    
                    #if is "photo" field, needs special treatment
                    if field == "photo":
                        start_img_index = line.find("<img src=")
                        end_img_index = line.find("'></img>")
                        row[field] = line[start_img_index+10:end_img_index]
                    else:
                        #write text between <td> and </td> on object
                        row[field] = line[start_row+4:end_row]
                    
                    td_counter = td_counter + 1
            else:
                #end table row (</tr>), reset flag values
                found_tr=0
                td_counter=0

        #write entire row on csv
        if len(row) == len(fieldnames):
            writer.writerow(row)
            row = {}

            
    #close files / good practice
    html_file.close()
    csvfile.close()

except IOError as error:
    print (error)


