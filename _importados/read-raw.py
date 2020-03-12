import sys
import os


try:
    #r"\\.\PhysicalDrive1"
    #disk = open(r"C:\Users\user\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState",'rb')
    disk = os.chdir(r"C:\Users\user\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState")
    #disk.seek(14000*sector_size)
    print (os.getcwd())
    file = os.open (r"C:\Users\user\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState", os.O_BINARY);
    print (file)
    
except IOError as error:
    print (error)
    pass

