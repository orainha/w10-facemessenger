import os
import sys
from subprocess import Popen, PIPE
import csv
import json
import bs4
import requests
import shutil

import utils.files as utils


# XXX (ricardoapl) Fix this non-pythonic mess!
TEMPLATE_FILENAME = os.path.join(os.path.dirname(__file__), r'..\templates\template_undark.html')
REPORT_FILENAME = 'report_undark.html'
NEW_FILE_PATH = ''
PATH = ''
DB_PATH = ''


def report_html():
    db_path = DB_PATH
    undark = os.path.join(os.path.dirname(__file__), '..\\undark.exe')

    with open(TEMPLATE_FILENAME, 'r') as template:
        content = template.read()
    html = bs4.BeautifulSoup(content, features='html.parser')

    args = [
        undark,
        '-i', db_path,
        '--freespace',
    ]    
    pipe = Popen(args, stdout=PIPE)
    text = pipe.communicate()[0]
    text = text.decode("utf-8") 
    
    tr_tag = html.new_tag('tr')
    td_text = html.new_tag('td')
    for letter in text:
        td_text.append(letter)
        if (letter == '\n'):
            tr_tag.append(td_text)
            html.table.tbody.append(tr_tag)
            tr_tag = html.new_tag('tr')
            td_text = html.new_tag('td')

    report_path = NEW_FILE_PATH + REPORT_FILENAME
    with open(report_path, 'w') as report:
        output = html.prettify()
        report.write(output)


def report_csv(delim):
    """
    Search for deleted data from src directory into dst file by running undark.exe.
    """
    input_path = PATH
    dst_path = NEW_FILE_PATH 
    filename = '\\report-undark.csv'
    dst_path = dst_path + filename
    db_path = utils.get_db_path(input_path)
    undark = os.path.join(os.path.dirname(__file__), '..\\undark.exe')
    with open(dst_path, 'w') as f:
        args = [
            undark,
            '-i', db_path,
            '--freespace',
            # '--fine-search',
            # '--removed-only',
        ]
        Popen(args,stdout=f)


def paths(args):
    input_file_path(args.input)
    output_file_path(args.output)


def input_file_path(path):
    # XXX (orainha) Procurar por utilizadores dando apenas o drive?
    # XXX (orainha) Where is PATH used?
    global PATH
    global DB_PATH
    PATH = utils.get_input_file_path(path)
    DB_PATH = utils.get_db_path(PATH)


def output_file_path(path):
    global NEW_FILE_PATH
    NEW_FILE_PATH = utils.get_output_file_path(path)
