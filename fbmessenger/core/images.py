import os
import sys
import subprocess
import csv
import json
import bs4
import requests
import shutil

import utils.files as utils


# XXX (ricardoapl) Fix this non-pythonic mess!
TEMPLATE_FILENAME = os.path.join(os.path.dirname(__file__), r'..\templates\template_images.html')
REPORT_FILENAME = 'report_images.html'
NEW_FILE_PATH = ''
IMAGES_PATH = ''
PATH = ''


class ImagesCollector():
    def __init__(self):
        pass

def test(self, path):
    print (path)

# XXX (ricardoapl) Improve docstring according to PEP8
def extract_one(src, dst):
    """
    Extract data from src directory into dst file by running hindsight.exe.
    """
    # XXX (ricardoapl) Fix this non-pythonic mess!
    hindsight = os.path.join(os.path.dirname(__file__), '..\hindsight.exe')
    fileformat = 'jsonl'
    args = [
        hindsight,
        '-i', src,
        '-o', dst,
        '-f', fileformat,
    ]
    subprocess.run(args, stdout=subprocess.DEVNULL)


# XXX (ricardoapl) Add destination path/file argument?
# XXX (ricardoapl) Improve docstring according to PEP8
def extract_all(path):
    """
    Carve Chromium artifacts contained in subdirectories of path.
    """
    prefix = 'tmp'
    suffix = 1
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                filename = f'{prefix}-{suffix}'
                extract_one(entry, filename)
                suffix += 1


def clean(path):
    """
    Delete files produced by extract_one() and/or extract_all().
    """
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith('tmp') and entry.name.endswith('.jsonl'):
                os.remove(entry.name)


# XXX (ricardoapl) Specify assumptions like 'extract_all() has been run'
def report_html(template_path, report_path, depth):
    with open(template_path, 'r') as template:
        content = template.read()
    html = bs4.BeautifulSoup(content, features='html.parser')
    # XXX (ricardoapl) If we add destination path/file argument to extract_all,
    #     we must change argument of os.scandir()
    with os.scandir() as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith('tmp') and entry.name.endswith('.jsonl'):
                content = read_jsonl(entry.name)
                image_content = filter_image_content(content)
                append_html(image_content, html, depth)
    with open(report_path, 'w') as report:
        output = html.prettify()
        report.write(output)


def append_html(data, html, depth):
    tbody = html.tbody
    filename_counter = 1
    previous_filename = ''
    for datum in data:
        # print(datum)
        profile_tag = html.new_tag('td')
        profile_tag.string = datum['profile']
        location_tag = html.new_tag('td')
        location_tag.string = datum['location']
        datetime_tag = html.new_tag('td')
        datetime_tag.string = datum['datetime']

        image_tag = html.new_tag('td')
        # Get file name
        # strSplit = datum['profile'].split('\\')
        # filename = strSplit[len(strSplit)-1]
        filename = utils.get_filename_from_url(datum['url'])
        # Get file type
        filetype = utils.get_filetype(datum['url'])
        if (depth == "fast"):
            # Create button
            button_tag = html.new_tag('button')
            button_tag['id'] = filename + filetype
            button_tag['class'] = 'btn_download_images_file'
            button_tag['value'] = datum['url']
            button_tag.append('Download Image')
            image_tag.append(button_tag)
        elif (depth == "complete"):
            # filename = filename.split('/')
            # if (previous_filename == filename):
            #     filename = filename + '('+str(filename_counter)+')'
            #     filename_counter = filename_counter + 1
            #filename = utils.get_filename_from_url(datum['url'])
            img_tag = html.new_tag('img')
            # We are now ready for extract
            extract_image(NEW_FILE_PATH, datum['url'], filename, filetype)
            # Show on html
            img_tag['src'] = f'images-search\{filename}{filetype}'
            image_tag.append(img_tag)
            previous_filename = filename

        row_tag = html.new_tag('tr')
        row_tag.append(profile_tag)
        row_tag.append(location_tag)
        row_tag.append(datetime_tag)
        row_tag.append(image_tag)
        tbody.append(row_tag)


# XXX (ricardoapl) Specify assumptions like 'extract_all() has been run'
def report_csv(delim):
    # XXX (ricardoapl) If we add destination path/file argument to extract_all,
    #     we must change argument of os.scandir()
    rows = []
    with os.scandir() as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith('tmp') and entry.name.endswith('.jsonl'):
                content = read_jsonl(entry.name)
                image_content = filter_image_content(content)
                append_rows(image_content, rows)
    # XXX (ricardoapl) Rename columns according to HTML report
    columns = [
        'profile',
        'location',
        'datetime',
        'url'
    ]
    # XXX (ricardoapl) Remove reference to NEW_FILE_PATH?
    filename = NEW_FILE_PATH + 'report_images.csv'
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=delim, quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow(columns)
        writer.writerows(rows)


# XXX (ricardoapl) Specify assumptions like 'new_rows and old_rows are lists whose elements are in JSON format'
def append_rows(new_rows, old_rows):
    for row in new_rows:
        old_rows.append(row.values())


def read_jsonl(filename):
    with open(filename, 'r') as jsonlfile:
        content = jsonlfile.read()
    jsonl = [json.loads(line) for line in content.splitlines()]
    return jsonl


def filter_image_content(data):
    http_data = [
        datum for datum in data
        if 'http_headers_dict' in datum
    ]
    image_data = [
        datum for datum in http_data
        if datum['http_headers_dict']['content-type'].startswith('image/')
    ]
    filtered_data = [
        {
            'profile': datum['profile'],
            'location': datum['location'],
            'datetime': datum['datetime'],
            'url': datum['url']
        }
        for datum in image_data
    ]
    return filtered_data


def input_file_path(path):
    # XXX (orainha) Procurar por utilizadores dando apenas o drive?
    global PATH
    PATH = path + f'\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\'


def output_file_path(path):
    global NEW_FILE_PATH
    global IMAGES_PATH
    path = os.path.expandvars(path)
    NEW_FILE_PATH = path + "\\report\\"
    IMAGES_PATH = NEW_FILE_PATH + "images-search\\"
    try:
        if not os.path.exists(path):
            raise IOError("Error: Given destination output path not found")
        if not os.path.exists(NEW_FILE_PATH):
            os.makedirs(NEW_FILE_PATH)
        if not os.path.exists(IMAGES_PATH):
            os.makedirs(IMAGES_PATH)
    except IOError as error:
        print(error)
        exit()



def extract_image(path, url, name, filetype):
    global PATH
    PATH = os.path.expandvars(path)
    IMAGES_PATH = PATH + f'images-search'
    utils.extract(path, IMAGES_PATH, url, name, filetype)



