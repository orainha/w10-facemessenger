import subprocess
import sys
import os
import json
import bs4
import argparse

REPORT_FILENAME = 'report_user_search.html'
TEMPLATE_FILENAME = r'templates\template_search_results.html'
NEW_FILE_PATH = ''
PATH = ''

def extract(dirpath, filepath):
    """Extract data from dirpath into filepath by running hindsight.exe."""
    fileformat = 'jsonl'
    args = [
        'hindsight.exe',
        '-i', dirpath,
        '-o', filepath,
        '-f', fileformat,
    ]
    subprocess.run(args, stdout=subprocess.DEVNULL)

def traverse(dirpath):
    # XXX (ricardoapl) Maybe extract() doesn't need to be a separate method - update clean() docstring if so
    prefix = 'tmp'
    suffix = 1
    with os.scandir(dirpath) as entries:
        for entry in entries:
            if entry.is_dir():
                filename = f'{prefix}-{suffix}'
                extract(entry, filename)
                suffix += 1

def clean():
    """Delete files produced by calling extract()."""
    with os.scandir() as entries:
        for entry in entries:
            # XXX (ricardoapl) Add and startswith('tmp') for certainty
            if entry.is_file() and entry.name.endswith('.jsonl'):
                os.remove(entry.name)

def report():
    # TODO (ricardoapl) Write docstring
    with open(TEMPLATE_FILENAME, 'r') as template:
        content = template.read()
    html = bs4.BeautifulSoup(content, features='html.parser')
    with os.scandir() as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith('.jsonl'):
                content = read_jsonl(entry.name)
                append(content, html)
    with open(REPORT_FILENAME, 'w') as report:
        output = html.prettify()
        report.write(output)

def read_jsonl(filepath):
    # XXX (ricardoapl) Maybe its not worth having a separate method
    with open(filepath, 'r') as jsonlfile:
        content = jsonlfile.read()
    jsonl = [json.loads(line) for line in content.splitlines()]
    return jsonl

def append(data, html):
    # TODO (ricardoapl) Write docstring
    # TODO (ricardoapl) 'Fix' list comprehensions!
    data_http = [datum for datum in data if 'http_headers_dict' in datum]
    # XXX (ricardoapl) Consider 'image/gif' as well
    data_images = [datum for datum in data_http if datum['http_headers_dict']['content-type'] == 'image/jpeg']
    results = [{'profile': req['profile'], 'location': req['location'], 'datetime': req['datetime'], 'url': req['url']} for req in data_images]
    # XXX (ricardoapl) Where the append (actually) happens!
    tbody = html.tbody
    for result in results:
        profile_tag = html.new_tag('td')
        profile_tag.string = result['profile']
        location_tag = html.new_tag('td')
        location_tag.string = result['location']
        datetime_tag = html.new_tag('td')
        datetime_tag.string = result['datetime']
        link_tag = html.new_tag('a')
        link_tag['href'] = result['url']
        link_tag.string = result['url']
        url_tag = html.new_tag('td')
        url_tag.append(link_tag)
        row_tag = html.new_tag('tr')
        row_tag.append(profile_tag)
        row_tag.append(location_tag)
        row_tag.append(datetime_tag)
        row_tag.append(url_tag)
        tbody.append(row_tag)

def export_to_csv(delimiter):
    #TODO: Insert csv export code   
    print ("Exported to CSV with delimiter: " + delimiter)

def input_file_path(path):
    #TODO: procurar por utilizadores dando apenas o drive?
    global PATH
    #get full path
    PATH = path + f'\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\\'

def output_file_path(path):
    global NEW_FILE_PATH 
    path = os.path.expandvars(path)
    NEW_FILE_PATH = path + "\\report\\"
    try:
        if not os.path.exists(path):
            raise IOError ("Error: Given destination output path not found")
        if not os.path.exists(NEW_FILE_PATH):
            os.makedirs(NEW_FILE_PATH)
    except IOError as error:
        print(error)
        exit()  

def load_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e','--export', choices=['csv'], help='Export to %(choices)s')
    parser.add_argument('-d','--delimiter', choices=[',','»','«'], help='Delimiter to csv')
    #parser.add_argument('-src','--source', help='Windows user path. Usage %(prog)s -src C:\Users\User', required=True)
    #parser.add_argument('-dst','--destination', default=r'%USERPROFILE%\Desktop', help='Save report path')
    group1 = parser.add_argument_group('mandatory arguments')
    group1.add_argument('-i','--input', help=r'Windows user path. Usage: %(prog)s -i C:\Users\User', required=True)
    parser.add_argument('-o','--output', default=r'%USERPROFILE%\Desktop', help='Output destination path')

    args = parser.parse_args()
    
    export_options = {"csv" : export_to_csv}
    file_options = {"input" : input_file_path, "output" : output_file_path}

    for arg, value in vars(args).items():
        if value is not None and arg=='export':
            delimiter = args.delimiter if args.delimiter is not None else ','
            export_options[value](delimiter)
        elif value is not None and arg!='delimiter':
            file_options[arg](value)

def main():
    load_command_line_arguments()
    #dirpath = r'%LOCALAPPDATA%\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\Partitions'
    dirpath = PATH + 'Partitions'
    dirpath = os.path.expandvars(dirpath)
    traverse(dirpath)
    report()
    clean()

if __name__ == '__main__':
    main()