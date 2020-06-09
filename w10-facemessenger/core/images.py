import os
import sys
import subprocess
import csv
import json
import bs4
import requests
import shutil

import utils.files as utils
import threading


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

def extract_entry(entry, prefix, suffix):
    if entry.is_dir():
        filename = f'{prefix}-{suffix}'
        extract_one(entry, filename)
        suffix += 1

# XXX (ricardoapl) Add destination path/file argument?
# XXX (ricardoapl) Improve docstring according to PEP8
def extract_all(path):
    """
    Carve Chromium artifacts contained in subdirectories of path.
    """
    prefix = 'tmp'
    suffix = 1
    threads = list()
    with os.scandir(path) as entries:
        for entry in entries:
            x = threading.Thread(target=extract_entry, args=(entry, prefix, suffix,))
            threads.append(x)
            x.start()
        for thread in threads:
            thread.join()





def clean(path):
    """
    Delete files produced by extract_one() and/or extract_all().
    """
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith('tmp') and entry.name.endswith('.jsonl'):
                os.remove(entry.name)


# XXX (ricardoapl) Specify assumptions like 'extract_all() has been run'
def report_html(depth):
    with open(TEMPLATE_FILENAME, 'r') as template:
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
    report_path = NEW_FILE_PATH + REPORT_FILENAME
    with open(report_path, 'w') as report:
        output = html.prettify()
        report.write(output)


def append_html(data, html, depth):
    tbody = html.tbody
    previous_filename = ''
    extract_images_list = list()
    for datum in data:
        profile_tag = html.new_tag('td')
        profile_tag.string = datum['profile']
        location_tag = html.new_tag('td')
        location_tag.string = datum['location']
        datetime_tag = html.new_tag('td')
        datetime_tag.string = datum['datetime']

        image_tag = html.new_tag('td')
        # Get file name
        filename = utils.get_filename_from_url(datum['url'])
        # Get file type
        filetype = utils.get_filetype(datum['url'])
        if (depth == "fast"):
            # Create button
            button_tag = html.new_tag('button')
            button_tag['id'] = filename + filetype
            button_tag['class'] = 'btn_download_images_file btn btn-outline-dark my-2 my-sm-0'
            button_tag['value'] = datum['url']
            button_tag.append('Download Image')
            image_tag.append(button_tag)
        elif (depth == "complete"):
            url = datum['url']
            image = [NEW_FILE_PATH, url, filename, filetype]
            extract_images_list.append(image)
            # Show on html
            img_tag = html.new_tag('img')
            img_tag['src'] = f'images-search\{filename}{filetype}'
            image_tag.append(img_tag)
            previous_filename = filename

        row_tag = html.new_tag('tr')
        row_tag.append(profile_tag)
        row_tag.append(location_tag)
        row_tag.append(datetime_tag)
        row_tag.append(image_tag)
        tbody.append(row_tag)
    if (depth == "complete"):
        extract_image(extract_images_list)


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
    columns = [
        'Source Directory',
        'File[Offset]',
        'Date Accessed',
        'Url'
    ]
    # XXX (ricardoapl) Remove reference to NEW_FILE_PATH?
    filename = NEW_FILE_PATH + 'report_images.csv'
    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
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


def paths(args):
    input_file_path(args.input)
    output_file_path(args.output)


def input_file_path(path):
    # XXX (orainha) Procurar por utilizadores dando apenas o drive?
    global PATH
    # PATH = path + f'\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\'
    PATH = utils.get_input_file_path(path)


def output_file_path(path):
    global NEW_FILE_PATH
    global IMAGES_PATH
    NEW_FILE_PATH = utils.get_output_file_path(path)
    IMAGES_PATH = NEW_FILE_PATH + "images-search\\"
    try:
        if not os.path.exists(IMAGES_PATH):
            os.makedirs(IMAGES_PATH)
    except IOError as error:
        print(error)
        sys.exit()


def extract_image(extract_images_list):
    images_path = IMAGES_PATH
    threads = list()
    for image in extract_images_list:
        new_file_path = image[0]
        url = image[1]
        filename = image[2]
        filetype = image[3]
        x = threading.Thread(target=utils.extract, args=(new_file_path, images_path, url, filename, filetype,))
        threads.append(x)
        x.start()
    for thread in threads:
        thread.join()



