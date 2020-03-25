import csv

try:

    csvfile =  open('image.csv', 'w', newline='')
    fieldnames = ['img']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    line_to_handle = """ <a href='https://scontent.flis7-1.fna.fbcdn.net/v/t1.30497-1/c212.0.720.720a/p720x720/84688533_170842440872810_7559275468982059008_n.jpg?_nc_cat=1&_nc_sid=dbb9e7&_nc_ohc=cKV4CcWjkigAX8ARzGU&_nc_ad=z-m&_nc_cid=0&_nc_zor=9&_nc_ht=scontent.flis7-1.fna&oh=3e71fd1b7c020f5c9a582b5fcb48e697&oe=5E91DAF6'><img src='https://scontent.flis7-1.fna.fbcdn.net/v/t1.30497-1/c29.0.100.100a/p100x100/84688533_170842440872810_7559275468982059008_n.jpg?_nc_cat=1&_nc_sid=dbb9e7&_nc_ohc=cKV4CcWjkigAX8ARzGU&_nc_ad=z-m&_nc_cid=0&_nc_zor=9&_nc_ht=scontent.flis7-1.fna&oh=824b2f8a2a7ef9676e4c671be6c8d15f&oe=5E92F7B2'></img></a></td>"""

    start_img_index = line_to_handle.find("<img src=")
    end_img_index = line_to_handle.find("'></img>")

    line_to_print = line_to_handle[start_img_index+10:end_img_index]

    #print (line_to_print)
    
    writer.writerow({'img': line_to_print})

except IOError as error:
    print (error)
