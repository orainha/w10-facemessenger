import os  # XXX (ricardoapl) Remove after refactoring modules
import argparse
import threading
import sqlite3

import core.contacts
import core.messages
import core.images
import core.undark
import models.suspect

import utils.files as utils

from timeit import default_timer as timer


# XXX (ricardoapl) Apply PEP8
def parse_cmdline():
    description = 'Windows 10 Messenger (Beta) forensic analysis tool'
    parser = argparse.ArgumentParser(description=description)
    required_group = parser.add_argument_group('required arguments')
    required_group.add_argument('--input', required=True, help='set path to user directory')
    parser.add_argument('--output', default=r'%USERPROFILE%\Desktop', help='set output directory for report (defaults to Desktop)')
    parser.add_argument('--format', choices=['html', 'csv'], default='html', help='choose report format (defaults to "html")')
    parser.add_argument('--delimiter', choices=[',', '»', '«'], default=',', help='specify csv report delimiter (defaults to ",")')
    # TODO (ricardoapl) Add argument for downloads
    # TODO (orainha) Need to write better 'help'
    parser.add_argument('--depth', choices=['fast', 'complete'], default='fast', help='fast: no images, no internet required; complete: with images, internet required, slower')
    args = parser.parse_args()
    return args


def search_cache_images(args, suspect_id):
    print("Searching cache files...")
    # XXX (orainha) Find better way to pass a suspect instance just because the id
    class TempSuspect:
        def __init__(self, id):
            self.id = id
    temp_suspect = TempSuspect(suspect_id)
    core.images.paths(args, temp_suspect)
    # XXX (orainha) Repeated var image_path on run()
    images_path = core.images.PATH + 'Partitions'
    images_path = os.path.expandvars(images_path)
    x = threading.Thread(target=core.images.extract_all, args=(images_path,))
    x.start()
    if args.format == 'html':
        core.images.report_html(args.depth)
    elif args.format == 'csv':
        delim = args.delimiter
        core.images.report_csv(delim)
    cwd = os.getcwd()
    core.images.clean(cwd)
    x.join()


# TODO (ricardoapl) Extract responsibility to modules/classes
def run(args):
    threads = list()
    start = timer()

    # Get existing suspect accounts
    suspect_ids = []
    input_file_path = utils.get_input_file_path(args.input)
    suspect_ids = utils.get_suspect_ids(input_file_path)

    #Create report for each id
    for id in suspect_ids:
        # Validate database existence
        db_path = utils.get_suspect_db_path(input_file_path, id)
        if not utils.has_database(args, db_path):
            # If there is no database but file path exists, search cache images
            print("Warning: Database " + db_path + " not found")
            search_cache_images(args, id)
            continue
        
        # Create suspect instance
        suspect = models.suspect.create_suspect(id, input_file_path)
        

        # Set modules paths 
        core.contacts.paths(args, suspect)
        core.messages.paths(args, suspect)
        core.images.paths(args, suspect)
        core.undark.paths(args, suspect)


        # XXX (orainha) Repeated var image_path on search_cache_images()
        images_path = core.images.PATH + 'Partitions'
        images_path = os.path.expandvars(images_path)
        t = threading.Thread(target=core.images.extract_all, args=(images_path,))
        threads.append(t)
        t.start()
        
        if args.format == 'html':
            utils.create_web_files(args.output, suspect)
            core.contacts.report_html(args.depth)
            core.messages.report_html(args.depth)
            core.images.report_html(args.depth)
            # Create report.html
            utils.create_index_html(args, suspect)

        elif args.format == 'csv':
            delim = args.delimiter
            core.contacts.report_csv(delim)
            core.messages.report_csv(delim)
            core.images.report_csv(delim)
            core.undark.report_csv(delim)

        cwd = os.getcwd()
        core.images.clean(cwd)

        for thread in threads:
            thread.join()

    end = timer()
    print("Report processed in " + str(end - start) + " seconds")


def main():
    args = parse_cmdline()
    run(args)


if __name__ == '__main__':
    main()
