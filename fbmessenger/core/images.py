import os
import sys
import subprocess
import csv
import json

import bs4


# XXX (ricardoapl) Fix this non-pythonic mess!
TEMPLATE_FILENAME = os.path.join(os.path.dirname(__file__), r'..\templates\template_images.html')
REPORT_FILENAME = 'report_images.html'
NEW_FILE_PATH = ''
PATH = ''


class ImagesCollector():
    def __init__(self):
        pass


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
def report_html(template_path, report_path):
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
                append_html(image_content, html)
    with open(report_path, 'w') as report:
        output = html.prettify()
        report.write(output)


def append_html(data, html):
    tbody = html.tbody
    for datum in data:
        profile_tag = html.new_tag('td')
        profile_tag.string = datum['profile']
        location_tag = html.new_tag('td')
        location_tag.string = datum['location']
        datetime_tag = html.new_tag('td')
        datetime_tag.string = datum['datetime']
        link_tag = html.new_tag('a')
        link_tag['href'] = datum['url']
        link_tag.string = datum['url']
        url_tag = html.new_tag('td')
        url_tag.append(link_tag)
        row_tag = html.new_tag('tr')
        row_tag.append(profile_tag)
        row_tag.append(location_tag)
        row_tag.append(datetime_tag)
        row_tag.append(url_tag)
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
    path = os.path.expandvars(path)
    NEW_FILE_PATH = path + "\\report\\"
    try:
        if not os.path.exists(path):
            raise IOError("Error: Given destination output path not found")
        if not os.path.exists(NEW_FILE_PATH):
            os.makedirs(NEW_FILE_PATH)
    except IOError as error:
        print(error)
        exit()
