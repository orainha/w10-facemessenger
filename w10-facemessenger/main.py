import os
import sys
import argparse
import threading

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
    parser.add_argument('--delimiter', choices=[',', '»', '«'], default=',', help='specify csv report delimiter (defaults to ",")')
    # TODO (orainha) Need to write better 'help'
    parser.add_argument('--depth', choices=['fast', 'complete'], default='fast', help='fast: no images, no internet required; complete: with images, internet required, slower')
    args = parser.parse_args()
    return args


def search_cache_images(args):
    print("Searching cache files...")
    core.images.input_file_path(args.input)
    core.images.output_file_path(args.output)
    # XXX (orainha) Repeated var image_path on run()
    images_path = core.images.PATH + 'Partitions'
    images_path = os.path.expandvars(images_path)
    x = threading.Thread(target=core.images.extract_all, args=(images_path,))
    x.start()
    if args.format == 'html':
        utils.create_web_files(args.output)
        core.images.report_html(args.depth)
    elif args.format == 'csv':
        delim = args.delimiter
        core.images.report_csv(delim)
    cwd = os.getcwd()
    core.images.clean(cwd)
    x.join()


def validate_input_arg(args):
    # XXX (ricardoapl) This method is not responsible for execution, only validation!
    # XXX (ricardoapl) Why raise exceptions only to catch afterwards?
    try:
        if not os.path.exists(args.input):
            raise IOError(args.input + " not found")
        full_input_path = utils.get_input_file_path(args.input)
        if not os.path.exists(full_input_path):
            raise IOError(full_input_path + " not found")
        db_path = utils.get_db_path(full_input_path)
        if not os.path.exists(db_path):
            print("Warning: Database " + db_path + " not found")
            # If there is no database but file path exists, search cache images
            search_cache_images(args)
            sys.exit()
    except IOError as error:
        print("Error --input: " + str(error))
        sys.exit()


# TODO (ricardoapl) Extract responsibility to modules/classes
def run(args):
    threads = list()
    start = timer()

    # Check if input file exists
    validate_input_arg(args)
    
    # XXX (orainha) Simplify? 
    core.contacts.paths(args)
    core.messages.paths(args)
    core.images.paths(args)
    core.undark.paths(args)
    
    # XXX (orainha) Repeated var image_path on search_cache_images()
    images_path = core.images.PATH + 'Partitions'
    images_path = os.path.expandvars(images_path)
    t = threading.Thread(target=core.images.extract_all, args=(images_path,))
    threads.append(t)
    t.start()
    
    if args.format == 'html':
        utils.create_web_files(args.output)
        core.contacts.report_html(args.depth)
        core.messages.report_html(args.depth)
        core.images.report_html(args.depth)
        utils.create_index_html(args)

    elif args.format == 'csv':
        delim = args.delimiter
        core.contacts.report_csv(delim)
        core.messages.report_csv(delim)
        core.images.report_csv(delim)
        core.undark.report_csv(delim)

    for thread in threads:
        thread.join()
    
    cwd = os.getcwd()
    core.images.clean(cwd)

    end = timer()
    print("Report processed in " + str(end - start) + " seconds")


def main():
    args = parse_cmdline()
    run(args)


if __name__ == '__main__':
    main()
