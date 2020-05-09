import hashlib
import datetime

import bs4


def fill_header(src_filename, dst_filename):
    """
    Populate HTML <header></header> of file specified by dst_filename.
    """
    filename = src_filename
    hashsum = sha256sum(src_filename)
    timezone = datetime.timezone.utc
    timestamp = datetime.datetime.now(timezone)
    with open(dst_filename, 'r', encoding='utf-8', errors='ignore') as file:
        html = bs4.BeautifulSoup(file, features='html.parser')
    filename_tag = html.new_tag('p')
    filename_tag['id'] = 'filename'
    filename_tag.string = f'File: {filename}'
    hashsum_tag = html.new_tag('p')
    hashsum_tag.string = f'Hash (SHA256): {hashsum}'
    timestamp_tag = html.new_tag('p')
    timestamp_tag.string = f'Time (UTC): {timestamp}'
    header = html.header
    header.append(filename_tag)
    header.append(hashsum_tag)
    header.append(timestamp_tag)
    with open(dst_filename, 'w', encoding='utf-8') as file:
        file.write(html.prettify())
        file.truncate()


def sha256sum(filename):
    """
    Return the SHA256 string representation of file specified by filename.
    """
    CHUNK_SIZE = 65536
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()
