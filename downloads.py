import sys
import os
import requests
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
#import httplib
#DB_PATH = str(Path.home()) + "\\AppData\\Local\\Packages\\Facebook.FacebookMessenger_8xx8rvfyw5nnt\\LocalState\\msys_709212107.db"
PATH = r'%USERPROFILE%\Desktop\\report'

def check_internet_connection(host='http://google.com'):
   try:
      req = requests.get(host) #Python 3.x
      return True
   except:
      return False

def download_contact_images(path):
   global PATH
   CONTACTS_FILENAME = 'contacts.html'

   PATH = os.path.expandvars(path)
   SMALL_IMAGES_PATH = PATH + f'\contacts\images\small'
   LARGE_IMAGES_PATH = PATH + f'\contacts\images\large'
   CONTACTS_FILENAME = PATH + f'\\'+ CONTACTS_FILENAME

   #TODO: Check Network connection?
   if (check_internet_connection()):
      download_small_contact_images(CONTACTS_FILENAME, SMALL_IMAGES_PATH)
      download_large_contact_images(CONTACTS_FILENAME, LARGE_IMAGES_PATH)
   else:
      print("Warning: Internet connection is required for images display")

def download_small_contact_images(contacts_filename, path):
   CONTACTS_FILENAME = contacts_filename
   SMALL_IMAGES_PATH = path

   try:
      # open file stream
      f = open(CONTACTS_FILENAME, 'r', errors='ignore')
      html_doc_new_file = BeautifulSoup(f, features='html.parser')
      f.close()

      #create diretory if not exists
      if not os.path.exists(SMALL_IMAGES_PATH):
         os.makedirs(SMALL_IMAGES_PATH)

      #find small images urls
      html_table = html_doc_new_file.table
      html_table_rows = html_table.find_all('tr')
      small_img_urls = html_table.find_all('p', attrs={"class": "img_url"})

      #print("Please wait. This might take a while...")
      counter = 0
      for url in small_img_urls:
         #strip url to discart <p> tags and spaces
         url = url.get_text().strip()
         #make request
         req = requests.get(url)
         #get first cell bellow table header (id cell)
         cell = html_table_rows[counter+1].find('td')
         if req.status_code == requests.codes.ok:
            #get file extension
            ext = ''
            if url.find (".jpg") > 0:
               ext = ".jpg"
            #create image file with contact id as file name
            image_filename = SMALL_IMAGES_PATH + "\\"+ cell.get_text().strip() + ext
            try:
               f = open(image_filename, 'wb+')
               f.write(req.content)
               f.close()
            except IOError as error:
               print (error)
         else:
            #url not found, get default image to replace
            not_found_image_filename = PATH + f'misc\\not_found.jpg'
            try:
               #copy default "not found" image and name it with contact id as file name
               shutil.copy2(not_found_image_filename, SMALL_IMAGES_PATH + '\\' + cell.get_text().strip() + '.jpg')
            except IOError as error:
               print (error)
         counter = counter + 1
   except IOError as error:
      print (error)

def download_large_contact_images(contacts_filename, path):
   CONTACTS_FILENAME = contacts_filename
   LARGE_IMAGES_PATH = path

   try:
      # open file stream
      f = open(CONTACTS_FILENAME, 'r', errors='ignore')
      html_doc_new_file = BeautifulSoup(f, features='html.parser')
      f.close()

      #create diretory if not exists
      if not os.path.exists(LARGE_IMAGES_PATH):
         os.makedirs(LARGE_IMAGES_PATH)

      #find large images urls
      html_table = html_doc_new_file.table
      html_table_rows = html_table.find_all('tr')
      large_img_urls = html_table.find_all('a')

      #print("Please wait. This might take a while...")
      counter = 0
      for url in large_img_urls:
         #select href class
         url = url['href']
         #make request
         req = requests.get(url)
         #get first cell bellow table header (id cell)
         cell = html_table_rows[counter+1].find('td')
         if req.status_code == requests.codes.ok:
            #get file extension
            ext = ''
            if url.find (".jpg") > 0:
               ext = ".jpg"
            #create image file with contact id as file name
            image_filename = LARGE_IMAGES_PATH + "\\"+ cell.get_text().strip() + ext
            try:
               f = open(image_filename, 'wb+')
               f.write(req.content)
               f.close()
            except IOError as error:
               print (error)
         else:
            #url not found, get default image to replace
            not_found_image_filename = PATH + f'misc\\not_found.jpg'
            try:
               #copy default "not found" image and name it with contact id as file name
               shutil.copy2(not_found_image_filename, LARGE_IMAGES_PATH + '\\' + cell.get_text().strip() + '.jpg')
            except IOError as error:
               print (error)
         counter = counter + 1
   except IOError as error:
      print (error)

def main():
   download_contact_images(PATH)

if __name__ == '__main__':
   main()