import os 
import requests
import shutil

def check_internet_connection(host='http://google.com'):
    try:
        req = requests.get(host)  # Python 3.x
        return True
    except:
        return False


def replace_by_default(output_path, file_path, filename):
    # URL not found, get default image to replace
    not_found_image_filename = output_path + f'images\\notfound.jpg'
    try:
        #create /images if not exists
        if not os.path.exists(output_path + "\images"):
            os.makedirs(output_path + "\images")

            images_dir = os.path.join(os.path.dirname(__file__), r'..\templates\images\\')
            images = os.listdir(images_dir)
            for image in images:
                shutil.copy2(images_dir + image,
                            output_path + "\images")

        # Copy default "not found" image and name it with contact id as file name
        shutil.copy2(not_found_image_filename, file_path +
                        '\\' + filename + '.jpg')
    except IOError as error:
        print(error)

def extract(output_path, file_path, url, filename, filetype):
    if (not check_internet_connection()):
        print("Warning: Internet connection is required for images display")
        exit()
    try:
        # Create diretory if not exists
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        # Make request
        req = requests.get(url)

        if req.status_code == requests.codes.ok:
            
            # Create image file with contact id as file name
            filename = file_path + "\\" + filename + filetype

            try:
                f = open(filename, 'wb+')
                f.write(req.content)
                f.close()
            except IOError as error:
                print(error)
        else:
            replace_by_default(output_path, file_path, filename)
    except IOError as error:
        print(error)

def get_filetype(file_url):
    strSplit = file_url.split('?')
    strLen = len(strSplit[0])
    periodIndex = strLen - 1
    while (strSplit[0][periodIndex].find('.') == -1):
        periodIndex = periodIndex -1
        if (periodIndex < 0):
            break
    filetype = strSplit[0][periodIndex:strLen]
    return filetype


def get_filename_from_url(url):
    strSplit = url.split('/')
    splitCount = len(strSplit)
    strFilename = strSplit[splitCount-1]
    strLen = len(strFilename)
    periodIndex = 0
    while (strFilename[periodIndex].find('.') == -1):
        periodIndex = periodIndex + 1
        if (strFilename[periodIndex].find('?') != -1 or periodIndex == strLen-1):
            break
    filename = strFilename[0:periodIndex-1]
    return filename



