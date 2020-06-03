import hashlib
import datetime
import os
import sqlite3
import utils.files as utils

import bs4


def fill_index_header(html, input_file_path, depth):

    suspect_id = utils.get_suspect_id(input_file_path)

    SUSPECT_QUERRY = """
        SELECT
            profile_picture_url,
            name,
            profile_picture_large_url 
        FROM contacts
        WHERE id = """ + str(suspect_id)

    db_path = utils.get_db_path(input_file_path)

    # Connect to database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(SUSPECT_QUERRY)

    for row in c:
        small_pic = str(row[0])
        name = str(row[1])
        large_pic = str(row[2])

    div_container_fluid = html.new_tag("div")
    div_container_fluid["class"] = "container-fluid"
    div_container_row = html.new_tag("div")
    div_container_row["class"] = "row"

    # LOGO
    div_logo = html.new_tag("div")
    div_logo["class"] = "col-xl-1 mt-2"
    img_logo = html.new_tag("img")
    img_logo["id"] = "imgLogo"
    img_logo["src"] = "images/logo.png"
    div_logo.append(img_logo)

    # HASH


    filename = db_path
    hashsum = sha256sum(db_path)
    timezone = datetime.timezone.utc
    timestamp = datetime.datetime.now(timezone).ctime()

    left_style_tag = "p"
    right_style_tag = "p"

    div_hash = html.new_tag("div")
    div_hash["class"] = "col-xl-8 text-center mt-3"
    div_hash_row_1 = html.new_tag("div")
    div_hash_row_1["class"] = "row"
    div_hash_row_1_col_left = html.new_tag("div")
    div_hash_row_1_col_left["class"] = "col text-right"
    div_hash_row_1_col_right = html.new_tag("div")
    div_hash_row_1_col_right["class"] = "col text-left"
    file_tag = html.new_tag(left_style_tag)
    file_tag.append("Source file")
    small_file_tag = html.new_tag("small")
    small_file_tag.append(file_tag)
    div_hash_row_1_col_left.append(small_file_tag)
    filename_tag = html.new_tag(right_style_tag)
    filename_tag.append(filename)
    small_filename = html.new_tag("small")
    small_filename.append(filename_tag)
    div_hash_row_1_col_right.append(small_filename)
    div_hash_row_1.append(div_hash_row_1_col_left)
    div_hash_row_1.append(div_hash_row_1_col_right)

    div_hash_row_2 = html.new_tag("div")
    div_hash_row_2["class"] = "row"
    div_hash_row_2_col_left = html.new_tag("div")
    div_hash_row_2_col_left["class"] = "col text-right"
    div_hash_row_2_col_right = html.new_tag("div")
    div_hash_row_2_col_right["class"] = "col text-left"
    sha_tag = html.new_tag(left_style_tag)
    sha_tag.append("Hash (SHA256)")
    small_sha_tag = html.new_tag("small")
    small_sha_tag.append(sha_tag)
    div_hash_row_2_col_left.append(small_sha_tag)
    shaname_tag = html.new_tag(right_style_tag)
    shaname_tag.append(hashsum)
    small_shaname = html.new_tag("small")
    small_shaname.append(shaname_tag)
    div_hash_row_2_col_right.append(small_shaname)
    div_hash_row_2.append(div_hash_row_2_col_left)
    div_hash_row_2.append(div_hash_row_2_col_right)

    div_hash_row_3 = html.new_tag("div")
    div_hash_row_3["class"] = "row"
    div_hash_row_3_col_left = html.new_tag("div")
    div_hash_row_3_col_left["class"] = "col text-right"
    div_hash_row_3_col_right = html.new_tag("div")
    div_hash_row_3_col_right["class"] = "col text-left"
    timestamp_tag = html.new_tag(left_style_tag)
    timestamp_tag.append("Date Accessed")
    small_timestamp_tag = html.new_tag("small")
    small_timestamp_tag.append(timestamp_tag)
    div_hash_row_3_col_left.append(small_timestamp_tag)
    timestamp_name_tag = html.new_tag(right_style_tag)
    timestamp_name_tag.append(str(timestamp))
    small_timestamp_name = html.new_tag("small")
    small_timestamp_name.append(timestamp_name_tag)
    div_hash_row_3_col_right.append(small_timestamp_name)
    div_hash_row_3.append(div_hash_row_3_col_left)
    div_hash_row_3.append(div_hash_row_3_col_right)

    div_hash.append(div_hash_row_1)
    div_hash.append(div_hash_row_2)
    div_hash.append(div_hash_row_3)


    # SUSPECT

    div_suspect = html.new_tag("div")
    div_suspect["class"] = "col-xl-3"
    div_suspect_row = html.new_tag("div")
    div_suspect_row["class"] = "row mt-4"
    div_suspect_col_name = html.new_tag("div")
    div_suspect_col_name["class"] = "col mt-3 ml-2 text-right"
    name_tag = html.new_tag("h5")
    name_tag["name"] = "suspect"
    name_tag.append(name)
    div_suspect_col_name.append(name_tag)
    div_suspect_col_img = html.new_tag("div")
    div_suspect_col_img["class"] = "col mt-2 pr-3"

    filetype = utils.get_filetype(small_pic)
    if (depth == "fast"):
        button_tag = html.new_tag('button')
        button_tag['id'] = str(suspect_id) + filetype
        button_tag['class'] = 'btn_download_conversation_contact_image btn btn-outline-dark my-2 my-sm-0'
        button_tag['value'] = large_pic
        button_tag.append('Download Image')
        div_suspect_col_img.append(button_tag)
    elif (depth == "complete"):
        href_tag = html.new_tag('a')
        href_tag['href'] = f'contacts\images\large\{suspect_id}' + filetype
        img_tag = html.new_tag('img')
        img_tag['src'] = f'contacts\images\small\{suspect_id}' + filetype
        img_tag['id'] = 'imgSuspect'
        href_tag.append(img_tag)
        div_suspect_col_img.append(href_tag)

    div_suspect_row.append(div_suspect_col_name)
    div_suspect_row.append(div_suspect_col_img)
    div_suspect.append(div_suspect_row)

    div_container_row.append(div_logo)
    div_container_row.append(div_hash)
    div_container_row.append(div_suspect)

    div_container_fluid.append(div_container_row)

    html.header.append(div_container_fluid)

    return html




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
