import os
import sys
import requests
import shutil
import json
import sqlite3
from pathlib import Path
import utils.headers as headers
from bs4 import BeautifulSoup


def replace_by_default(output_path, file_path, filename, filetype):
    # URL not found, get default image to replace
    output_parent_path = os.path.abspath(os.path.join(output_path, os.pardir))
    images_index_path = output_parent_path + "\\images"
    not_found_image_filename = images_index_path + "\\notfound.jpg"

    try:
        #create /images if not exists
        if not os.path.exists(images_index_path):
             raise IOError(images_index_path + " path does not exist")

        # Copy default "not found" image and name it with contact id as file name
        shutil.copy2(not_found_image_filename, file_path +
                        '\\' + filename + filetype)
    except IOError as error:
        print("Error on replace_by_default(): " + str(error))
        sys.exit()


def check_internet_connection(host='http://google.com'):
    try:
        req = requests.get(host)  # Python 3.x
        return True
    except:
        return False


def extract(output_path, file_path, url, filename, filetype):
    if (not check_internet_connection()):
        print("Warning: Internet connection is required for images display")
        sys.exit()
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
            replace_by_default(output_path, file_path, filename, filetype)
    except IOError as error:
        print(error)


def get_filetype(file_url):
    try:
        if file_url.find('.jpg') != -1:
            filetype = '.jpg'
        else:
            strSplit = file_url.split('?')
            strLen = len(strSplit[0])
            periodIndex = strLen - 1
            while (strSplit[0][periodIndex].find('.') == -1):
                periodIndex = periodIndex -1
                if (periodIndex < 0):
                    break
            filetype = strSplit[0][periodIndex:strLen]
        return filetype
    except OSError as error:
        print("Error on get_filetype(): " + str(error))
        sys.exit()


def get_filename_from_url(url):
    try:
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
    except OSError as error:
        print("Error on get_filename_from_url(): " + str(error))
        sys.exit()


def create_report_html(args, suspect_id):
    output_path = get_output_file_path(args.output, suspect_id)
    try:
        template_index_path = os.path.join(os.path.dirname(__file__), r'..\templates\\template_report.html')
        dst_path = output_path + 'report.html'

        template_file = open(template_index_path, 'r', encoding='utf-8')
        html = BeautifulSoup(
            template_file, features='html.parser')
        new_file = open(dst_path, 'w', encoding='utf-8')

        input_path = get_input_file_path(args.input)
        html = headers.fill_report_header(html, input_path, suspect_id, args.depth)

        new_file.seek(0)
        new_file.write(html.prettify())
        new_file.truncate()

        # shutil.copy2(template_index_path, dst_path)
    except OSError as error:
        print("Error on create_report_html(): " + str(error))
        exit()


def create_suspects_html(args, suspect_id):
    output_path = get_index_path(args.output)
    try:
        template_index_path = os.path.join(os.path.dirname(__file__), r'..\templates\\template_suspects.html')
        dst_path = output_path + "suspects.html"
        input_path = get_input_file_path(args.input)
        suspect_profile = get_suspect_profile(input_path, suspect_id)

        if(not os.path.exists(dst_path)):
            template_file = open(template_index_path, 'r', encoding='utf-8')
            html = BeautifulSoup(
                template_file, features='html.parser')
        else:
            f = open(dst_path, 'r', encoding='utf-8')
            html = BeautifulSoup(
                    f, features='html.parser')
        
        new_file = open(dst_path, 'w', encoding='utf-8')

        html = create_suspect_index_row(html, suspect_profile, args.depth)

        new_file.seek(0)
        new_file.write(html.prettify())
        new_file.truncate()

    except OSError as error:
        print("Error on create_suspects_html(): " + str(error))
        sys.exit()


def create_index_html(output_path):
    output_path = get_index_path(output_path)
    try:
        template_index_path = os.path.join(os.path.dirname(__file__), r'..\templates\\template_index.html')
        dst_path = output_path + 'index.html'

        # template_file = open(template_index_path, 'r', encoding='utf-8')
        # html = BeautifulSoup(
        #     template_file, features='html.parser')
        # new_file = open(dst_path, 'w', encoding='utf-8')

        # input_path = get_input_file_path(args.input)
        # html = headers.fill_report_header(html, input_path, suspect_id, args.depth)

        # new_file.seek(0)
        # new_file.write(html.prettify())
        # new_file.truncate()

        shutil.copy2(template_index_path, dst_path)
    except OSError as error:
        print("Error on create_index_html(): " + str(error))
        exit()


def create_js_css(output_path):
    output_path = get_index_path(output_path)
    try:
        if not os.path.exists(output_path + "\js"):
            os.makedirs(output_path + "\js")
        js_path = os.path.join(os.path.dirname(__file__), r'..\templates\js\\')
        js_files = os.listdir(js_path)
        for filename in js_files:
            shutil.copy2(os.path.join(js_path, filename), output_path + "\js")

        if not os.path.exists(output_path + "\css"):
            os.makedirs(output_path + "\css")
        css_path = os.path.join(os.path.dirname(__file__), r'..\templates\css\\')
        css_files = os.listdir(css_path)
        for filename in css_files:
            shutil.copy2(os.path.join(css_path, filename), output_path + "\css")
    except OSError as error:
        print("Error on create_js_css(): " + str(error))


def create_image_files(output_path):
    output_path = get_index_path(output_path)
    try:
        #create /images if not exists
        images_path = output_path + "\images"
        if not os.path.exists(images_path):
            os.makedirs(images_path)
        images_dir = os.path.join(os.path.dirname(__file__), r'..\templates\images\\')
        images = os.listdir(images_dir)
        for image in images:
            shutil.copy2(images_dir + image,
                        images_path)
    except IOError as error:
        print(error)


def create_web_files(output_path):
    create_image_files(output_path)
    create_js_css(output_path)
    create_index_html(output_path)


def get_suspect_ids(input_file_path):
    #auth_id poderá ser um array (se tiver mais elementos, tratá-lo de modo diferente)
    try:
        if os.path.exists(input_file_path):
            auth_ids = []
            f_data = open(input_file_path + 'data', 'r')
            data = json.load(f_data)
            for item in data:
                txt = item.split(":")
                auth_ids.append(txt[1])
            return auth_ids
        else:
            raise IOError(input_file_path + " not found")
    except IOError as error:
        print("Error on get_suspect_id(): " + str(error))
        sys.exit()


def get_suspect_db_path(input_file_path, suspect_id):
    try:
        if not os.path.exists(input_file_path):
            raise IOError(str(input_file_path) + " not found")
        db_file_name = "msys_" + suspect_id + ".db"
        db_path = input_file_path + db_file_name
        return db_path
    except IOError as error:
        print("Error on get_db_path(): " + str(error))
        sys.exit()


def get_input_file_path(user_path):
    try:
        if not os.path.exists(user_path):
            raise IOError(str(user_path) + " not found")
        path = os.path.expandvars(user_path)
        return path + f'\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\'
    except IOError as error:
        print("Error on get_input_file_path(): " + str(error))
        return


def get_output_file_path(path, suspect_id):
    path = get_index_path(path)
    new_path = path + f"{suspect_id}\\"
    try:
        if not os.path.exists(path):
            raise IOError("Error: Given destination output path not found :" + path)
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        return new_path
    except IOError as error:
        print(error)
        sys.exit()


def get_index_path(path):
    path = os.path.expandvars(path)
    new_path = path + f"\\report\\"
    try:
        if not os.path.exists(path):
            raise IOError("Error: Given destination index path not found :" + path)
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        return new_path
    except IOError as error:
        print(error)
        sys.exit()


def has_database(args, db_path):
    try:
        if not os.path.exists(args.input):
            raise IOError(args.input + " not found")
        full_input_path = get_input_file_path(args.input)
        if not os.path.exists(full_input_path):
            raise IOError(full_input_path + " not found")
        if not os.path.exists(db_path):
            return False
        else:
            return True
    except IOError as error:
        print("Error --input: " + str(error))
        sys.exit()


def get_suspect_profile(input_file_path, suspect_id):
    SUSPECT_QUERRY = """
        SELECT
            profile_picture_url,
            name,
            profile_picture_large_url 
        FROM contacts
        WHERE id = """ + str(suspect_id)

    db_path = get_suspect_db_path(input_file_path, suspect_id)

    # Connect to database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(SUSPECT_QUERRY)

    for row in c:
        small_pic = str(row[0])
        name = str(row[1])
        large_pic = str(row[2])

    profile = []
    profile.append(suspect_id)
    profile.append(name)
    profile.append(small_pic)
    profile.append(large_pic)

    return profile


def create_suspect_index_row(html, suspect_profile, depth):
    suspect_id = suspect_profile[0]
    suspect_name = suspect_profile[1]
    suspect_pic = suspect_profile[2]
    suspect_large_pic = suspect_profile[3]

    div_row = html.new_tag('div')
    div_col_left = html.new_tag('div')
    div_col_right = html.new_tag('div')
    div_row['class'] = "row"
    div_col_left['class'] = "col text-right"
    div_col_right['class'] = "col text-left"

    href = html.new_tag('a')
    href['target'] ="_parent"
    href['href'] = f'{suspect_id}/report.html'
    href.append(suspect_name)

    photo = html.new_tag('div')
    filetype = get_filetype(suspect_pic)
    if (depth == "fast"):
        button_tag = html.new_tag('button')
        button_tag['id'] = str(suspect_id) + filetype
        button_tag['class'] = 'btn_download_conversation_contact_image btn btn-outline-dark my-2 my-sm-0 fast-button pb-2'
        button_tag['value'] = suspect_large_pic
        button_tag.append('Download Image')
        photo.append(button_tag)
    elif (depth == "complete"):
        href_tag = html.new_tag('a')
        href['target'] ="_parent"
        href_tag['href'] = f'{suspect_id}\contacts\images\large\{suspect_id}' + filetype
        img_tag = html.new_tag('img')
        img_tag['src'] = f'{suspect_id}\contacts\images\small\{suspect_id}' + filetype
        img_tag['id'] = 'imgParticipant'
        href_tag.append(img_tag)
        photo.append(href_tag)
    div_col_left.append(photo)
    div_col_right.append(href)
    div_row.append(div_col_left)
    div_row.append(div_col_right)
    html.table.insert_before(div_row)

    return html
