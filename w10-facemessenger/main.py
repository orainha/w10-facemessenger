import os
import sys
import argparse

from timeit import default_timer as timer

import core.contacts
import core.messages
import core.images
import core.undark
import utils.files as utils


# XXX (ricardoapl) Apply PEP8
def parse_cmdline():
    description = 'Windows 10 Messenger (Beta) forensic analysis tool'
    parser = argparse.ArgumentParser(description=description)
    required_group = parser.add_argument_group('required arguments')
    required_group.add_argument('--input', required=True, help='set path to user directory')
    parser.add_argument('--output', default=r'%USERPROFILE%\Desktop', help='set output directory for report (defaults to Desktop)')
    parser.add_argument('--format', choices=['html', 'csv'], default='html', help='choose report format (defaults to "html")')
    parser.add_argument('--delimiter', default=',', help='specify csv report delimiter (defaults to ",")')
    # TODO (orainha) Need to write better 'help'
    parser.add_argument('--depth', choices=['fast', 'complete'], default='fast', help='fast: no images, no internet required; complete: with images, internet required, slower')
    args = parser.parse_args()
    return args


def search_cache_images(args):
    print("[-] Searching cache files...")
    core.images.paths(args)
    images_path = core.images.PATH + 'Partitions'
    images_path = os.path.expandvars(images_path)
    core.images.extract_all(images_path)
    if args.format == 'html':
        core.images.report_html(args.depth)
        print("[+] Generated html cache report")
    elif args.format == 'csv':
        delim = args.delimiter
        core.images.report_csv(delim)
        print("[+] Generated csv cache report")
    cwd = os.getcwd()
    core.images.clean(cwd)


# TODO (ricardoapl) Extract responsibility to modules/classes
def run(args):

    print("[-] Starting Messenger (Beta) extraction")
    
    # Common files on report diretory
    if args.format == 'html':
        utils.create_web_files(args.output)
    search_cache_images(args)

    # Get existing suspect accounts
    suspect_ids = []
    input_file_path = utils.get_input_file_path(args.input)
    suspect_ids = utils.get_suspect_ids(input_file_path)

    # Create report for each id
    for id in suspect_ids:
        # Validate database existence
        db_path = utils.get_suspect_db_path(input_file_path, id)
        if not utils.has_database(args, db_path):
            # If there is no database but file path exists, search cache images
            print("[-] Warning: Database " + db_path + " not found")
            continue

        suspect_id = id
        # Set modules paths 
        core.contacts.paths(args, suspect_id)
        core.messages.paths(args, suspect_id)
        core.undark.paths(args, suspect_id)

        if args.format == 'html':
            print("[-] Generating suspect " + suspect_id + " html report")
            core.contacts.report_html(args.depth)
            core.messages.report_html(args.depth)
            core.undark.report_html()
            utils.create_report_html(args, suspect_id)
            utils.create_index_html(args, suspect_id)
            print("[+] Done")

        elif args.format == 'csv':
            print("[-] Generating suspect " + suspect_id + " csv report")
            delim = args.delimiter
            core.contacts.report_csv(delim)
            core.messages.report_csv(delim)
            core.undark.report_csv(delim)
            print("[+] Done")

    print("[+] Extraction completed")


def main():
    args = parse_cmdline()
    run(args)


if __name__ == '__main__':
    main()
