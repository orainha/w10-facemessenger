import hashlib


class Hash():

    DEFAULT_CHUNK_SIZE = 65536

    def sha256(cls, filename):
        """
        Return SHA256 string representation of file specified by filename.
        """
        DEFAULT_CHUNK_SIZE = 65536
        sha256 = hashlib.sha256()
        with open(filename, 'rb') as content:
            while True:
                chunk = content.read(DEFAULT_CHUNK_SIZE)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()