from bs4 import BeautifulSoup
from datetime import datetime, timezone
import hashlib

# XXX We may want to suppress soupsieve warning later on

def fill_header(src_filename, dst_filename):
    """Populate HTML <header></header> of file specified by dst_filename."""
    filename = src_filename
    hashsum = sha256sum(src_filename)
    timestamp = datetime.now(timezone.utc)
    with open(dst_filename, 'r+', encoding='utf-8') as file:
        html_doc = BeautifulSoup(file, features='html.parser')
        filename_tag = html_doc.new_tag('p')
        filename_tag['id'] = 'filename'
        filename_tag.string = f'File: {filename}'
        hashsum_tag = html_doc.new_tag('p')
        hashsum_tag.string = f'Hash (SHA256): {hashsum}'
        timestamp_tag = html_doc.new_tag('p')
        timestamp_tag.string = f'Time (UTC): {timestamp}'
        header = html_doc.header
        header.append(filename_tag)
        header.append(hashsum_tag)
        header.append(timestamp_tag)
        # Overwrite previous content
        file.seek(0)
        file.write(html_doc.prettify())
        file.truncate()

def sha256sum(filename):
    """Return the SHA256 string representation of file specified by filename."""
    CHUNK_SIZE = 65536
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()

if __name__ == '__main__':
    # Usage example
    src = r'C:\Users\IEUser\AppData\Local\Packages\Facebook.FacebookMessenger_8xx8rvfyw5nnt\LocalState\msys_100047488492327.db'
    dst = r'C:\Users\IEUser\Desktop\stub.html'
    fill_header(src, dst)
