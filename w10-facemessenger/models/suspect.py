import utils.files as utils
import sqlite3

class Suspect:
    #variaveis comuns a todas as instâncias

    def __init__(self, id, name, small_pic, large_pic, db_path):
        #variaveis comuns apenas à instancia
        self.id = id 
        self.name = name
        self.small_pic = small_pic
        self.large_pic = large_pic
        self.db_path = db_path

    def get_small_pic(self):
        return self.small_pic
    def get_large_pic(self):
        return self.large_pic
    def get_db_path(self):
        return self.db_path



def create_suspect(id, input_file_path):
    # get suspect info
    SUSPECT_QUERRY = """
    SELECT
        profile_picture_url,
        name,
        profile_picture_large_url 
    FROM contacts
    WHERE id = """ + str(id)

    # get suspect db_path
    db_path = utils.get_suspect_db_path(input_file_path, id)

    # Connect to database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(SUSPECT_QUERRY)

    for row in c:
        small_pic = str(row[0])
        name = str(row[1])
        large_pic = str(row[2])

    # create suspect instance
    suspect = Suspect(id, name, small_pic, large_pic, db_path)
    return suspect