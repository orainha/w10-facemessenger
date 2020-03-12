import sys
import os
import optparse
from winreg import *

def sid2user (sid):
    try:
        key = OpenKey(HKEY_LOCAL_MACHINE, 
        "SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList"  
        + '\\' + sid)

        (value, type) = QueryValueEx(key, 'ProfileImagePath')  
        user = value.split('\\')[-1]  
        return user
    except:
        return sid

def returnDir(): 
    dirs=['C:\\Recycler\\','C:\\Recycled\\','C:\\$Recycle.Bin\\'] 
    for recycleDir in dirs:  
        if os.path.isdir(recycleDir):   
            return recycleDir 
    return None

#for file in os.listdir(returnDir()):
    #print (file)

def findRecycled(recycleDir): 
    dirList = os.listdir(recycleDir) 
    for sid in dirList:
         files = os.listdir(recycleDir + sid)  
         user = sid2user(sid)  
         print ('\n[*] Listing Files For User: ' + str(user))  
         for file in files:   
             print ('[+] Found File: ' + str(file))

try:
    recycledDir = returnDir() 
    findRecycled(recycledDir)
except IOError as error:
    print (error)
#def main():
#    recycledDir = returnDir() 
#    findRecycled(recycledDir)
#
#if __name__ == "__main__":
#    main() 


