import os
import sys
import shutil
import requests

from bs4 import BeautifulSoup


# import httplib
PATH = r'%USERPROFILE%\Desktop\\report'


def check_internet_connection(host='http://google.com'):
    try:
        req = requests.get(host)  # Python 3.x
        return True
    except:
        return False


def download_contact_images(path):
    global PATH
    CONTACTS_FILENAME = 'contacts.html'
    PATH = os.path.expandvars(path)
    SMALL_IMAGES_PATH = PATH + f'\contacts\images\small'
    LARGE_IMAGES_PATH = PATH + f'\contacts\images\large'
    CONTACTS_FILENAME = PATH + f'\\' + CONTACTS_FILENAME
    # TODO (orainha) Check network connection?
    if (check_internet_connection()):
        download_small_contact_images(CONTACTS_FILENAME, SMALL_IMAGES_PATH)
        download_large_contact_images(CONTACTS_FILENAME, LARGE_IMAGES_PATH)
    else:
        print("Warning: Internet connection is required for images display")


def download_small_contact_images(contacts_filename, path):
    CONTACTS_FILENAME = contacts_filename
    SMALL_IMAGES_PATH = path

    try:
        # Open file stream
        f = open(CONTACTS_FILENAME, 'r', errors='ignore')
        html_doc_new_file = BeautifulSoup(f, features='html.parser')
        f.close()

        # Create diretory if not exists
        if not os.path.exists(SMALL_IMAGES_PATH):
            os.makedirs(SMALL_IMAGES_PATH)

        # Find small images urls
        html_table = html_doc_new_file.table
        html_table_rows = html_table.find_all('tr')
        small_img_urls = html_table.find_all('p', attrs={"class": "img_url"})

        # print("Please wait. This might take a while...")
        counter = 0
        for url in small_img_urls:
            # Strip url to discart <p> tags and spaces
            url = url.get_text().strip()
            # Make request
            req = requests.get(url)
            # Get first cell bellow table header (id cell)
            cell = html_table_rows[counter+1].find('td')
            if req.status_code == requests.codes.ok:
                # Get file extension
                ext = ''
                if url.find(".jpg") > 0:
                    ext = ".jpg"
                # Create image file with contact id as file name
                image_filename = SMALL_IMAGES_PATH + "\\" + cell.get_text().strip() + ext
                try:
                    f = open(image_filename, 'wb+')
                    f.write(req.content)
                    f.close()
                except IOError as error:
                    print(error)
            else:
                # Url not found, get default image to replace
                not_found_image_filename = PATH + f'images\\notfound.jpg'
                try:
                    # Copy default "not found" image and name it with contact id as file name
                    shutil.copy2(not_found_image_filename, SMALL_IMAGES_PATH +
                                 '\\' + cell.get_text().strip() + '.jpg')
                except IOError as error:
                    print(error)
            counter = counter + 1
    except IOError as error:
        print(error)


def download_large_contact_images(contacts_filename, path):
    CONTACTS_FILENAME = contacts_filename
    LARGE_IMAGES_PATH = path

    try:
        # Open file stream
        f = open(CONTACTS_FILENAME, 'r', errors='ignore')
        html_doc_new_file = BeautifulSoup(f, features='html.parser')
        f.close()

        # Create diretory if not exists
        if not os.path.exists(LARGE_IMAGES_PATH):
            os.makedirs(LARGE_IMAGES_PATH)

        # Find large images urls
        html_table = html_doc_new_file.table
        html_table_rows = html_table.find_all('tr')
        large_img_urls = html_table.find_all('a')

        # print("Please wait. This might take a while...")
        counter = 0
        for url in large_img_urls:
            # Select href class
            url = url['href']
            # Make request
            req = requests.get(url)
            # Get first cell bellow table header (id cell)
            cell = html_table_rows[counter+1].find('td')
            if req.status_code == requests.codes.ok:
                # Get file extension
                ext = ''
                if url.find(".jpg") > 0:
                    ext = ".jpg"
                # Create image file with contact id as file name
                image_filename = LARGE_IMAGES_PATH + "\\" + cell.get_text().strip() + ext
                try:
                    f = open(image_filename, 'wb+')
                    f.write(req.content)
                    f.close()
                except IOError as error:
                    print(error)
            else:
                # URL not found, get default image to replace
                not_found_image_filename = PATH + f'images\\notfound.jpg'
                try:
                    # Copy default "not found" image and name it with contact id as file name
                    shutil.copy2(not_found_image_filename, LARGE_IMAGES_PATH +
                                 '\\' + cell.get_text().strip() + '.jpg')
                except IOError as error:
                    print(error)
            counter = counter + 1
    except IOError as error:
        print(error)


def main():
    download_contact_images(PATH)


if __name__ == '__main__':
    main()
