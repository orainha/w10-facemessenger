import os
import subprocess
import utils.files as utils


NEW_FILE_PATH = ''
PATH = ''


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
        subprocess.Popen(args,stdout=f)


def paths(args):
    input_file_path(args.input)
    output_file_path(args.output)


def input_file_path(path):
    # XXX (orainha) Procurar por utilizadores dando apenas o drive?
    # XXX (orainha) Where is PATH used?
    global PATH
    PATH = utils.get_input_file_path(path)


def output_file_path(path):
    global NEW_FILE_PATH
    NEW_FILE_PATH = utils.get_output_file_path(path)
