import os  # XXX (ricardoapl) Remove after refactoring modules
import argparse

import core.contacts
import core.messages
import core.images
import core.downloads

# XXX (ricardoapl) Apply PEP8
def parse_cmdline():
    prog = 'fbmessenger'
    description = 'Facebook Messenger (Beta) forensic artifacts extractor'
    parser = argparse.ArgumentParser(prog=prog, description=description)
    required_group = parser.add_argument_group('required arguments')
    required_group.add_argument('--input', required=True, help='set path to user directory')
    parser.add_argument('--output', default=r'%USERPROFILE%\Desktop', help='set output directory for report (defaults to Desktop)')
    parser.add_argument('--format', choices=['html', 'csv'], default='html', help='choose report format (defaults to "html")')
    parser.add_argument('--delimiter', choices=[',', '»', '«'], default=',', help='specify csv report delimiter (defaults to ",")')
    # TODO (ricardoapl) Add argument for downloads
    # TODO (ogiosvaldo) What? Hieeeeeeeer.. (Need to write better 'help')
    parser.add_argument('--depth', choices=['fast', 'complete'], default='fast', help='fast: no images, no internet required; complete: with images, internet required, slower')
    args = parser.parse_args()
    return args


# TODO (ricardoapl) Extract responsibility to modules/classes
def run(args):
    core.contacts.input_file_path(args.input)
    core.contacts.output_file_path(args.output)
    core.messages.input_file_path(args.input)
    core.messages.output_file_path(args.output)
    core.images.input_file_path(args.input)
    core.images.output_file_path(args.output)

    images_path = core.images.PATH + 'Partitions'
    images_path = os.path.expandvars(images_path)
    # TODO (orainha) Don't forget to this uncomment this line
    core.images.extract_all(images_path)
    
    if args.format == 'html':
        # XXX (ricardoapl) It's not core.messages responsibility to create such files!
        core.messages.create_js_files()
        # XXX (ricardoapl) Don't other modules make use of DB_PATH?
        db_path = core.contacts.DB_PATH
        contacts_template = core.contacts.CONTACTS_TEMPLATE_FILE_PATH
        # TODO (orainha) Don't forget to this uncomment this line
        core.contacts.report_html(db_path, contacts_template, args.depth)
        # TODO (ricardoapl) Fill HTML headers for core.contacts
        conversations_template = core.messages.CONVERSATIONS_TEMPLATE_FILENAME
        messages_template = core.messages.MESSAGES_TEMPLATE_FILENAME
        # XXX (ricardoapl) There should be only one core.messages.report_html method to call
        core.messages.report_html_conversations(conversations_template, args.depth)
        # TODO (orainha) Don't forget to this uncomment this line
        core.messages.report_html_messages(messages_template, args.depth)
        # TODO (ricardoapl) Fill HTML headers for core.messages
        images_template = core.images.TEMPLATE_FILENAME
        images_report = core.images.NEW_FILE_PATH + core.images.REPORT_FILENAME
        # XXX (orainha) Don't forget to this uncomment this line
        core.images.report_html(images_template, images_report)
        # TODO (ricardoapl) Open HTML report (which one?)

    elif args.format == 'csv':
        delim = args.delimiter
        core.contacts.report_csv(delim)
        core.messages.report_csv(delim)
        core.images.report_csv(delim)

    cwd = os.getcwd()
    core.images.clean(cwd)


def main():
    args = parse_cmdline()
    run(args)


if __name__ == '__main__':
    main()