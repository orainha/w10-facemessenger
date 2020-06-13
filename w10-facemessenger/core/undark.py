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
# TEMPLATE_FILENAME = os.path.join(os.path.dirname(__file__), r'..\templates\template_images.html')
# REPORT_FILENAME = 'report_images.html'
NEW_FILE_PATH = ''
PATH = ''
DB_PATH = ''


def report_csv(delim):
    """
    Search for deleted data from src directory into dst file by running undark.exe.
    """
    input_path = PATH
    dst_path = NEW_FILE_PATH 
    db_path = DB_PATH
    filename = '\\report-undark.csv'
    dst_path = dst_path + filename
    undark = os.path.join(os.path.dirname(__file__), '..\\undark.exe')
    with open(dst_path,'w') as f:
        args = [
            undark,
            '-i', db_path,
            '--freespace',
            # '--fine-search',
            # '--removed-only',
        ]
        subprocess.Popen(args,stdout=f)

def paths(args, suspect_id):
    input_file_path(args.input, suspect_id)
    output_file_path(args.output, suspect_id)


def input_file_path(path, suspect_id):
    # XXX (orainha) Procurar por utilizadores dando apenas o drive?
    # XXX (orainha) Where is PATH used?
    global PATH
    global DB_PATH
    PATH = utils.get_input_file_path(path)
    DB_PATH = utils.get_suspect_db_path(PATH, suspect_id)


def output_file_path(path, suspect_id):
    global NEW_FILE_PATH
    NEW_FILE_PATH = utils.get_output_file_path(path, suspect_id)



