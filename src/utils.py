import os
import hashlib
from datetime import datetime
from itertools import groupby
import sqlite3

raw_extensions = {
    ".cr2",
    ".nef",
    ".arw",
    ".dng",
    ".orf",
    ".raf",
}


def get_file_creation_time(file_path):
    """Get the file creation datetime."""
    timestamp = os.path.getmtime(file_path)
    return datetime.fromtimestamp(timestamp)


def compute_md5(file_path):
    """Compute the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def is_image_unique_by_name(file_path, cursor):
    filename = os.path.basename(file_path)

    # Check if the MD5 hash already exists
    cursor.execute("SELECT 1 FROM photo_index WHERE filename = ?", (filename,))
    if cursor.fetchone() is None:
        return True
    else:
        return False


def is_image_unique_by_md5(file_path, cursor):
    md5_hash = compute_md5(file_path)

    # Check if the MD5 hash already exists
    cursor.execute("SELECT 1 FROM photo_index WHERE md5_hash = ?", (md5_hash,))
    if cursor.fetchone() is None:
        return True
    else:
        return False


def group_by_date(contents):
    # Sort dictionary items by value (modified time) to ensure groupby works correctly
    sorted_contents = sorted(contents.items(), key=lambda x: x[1])

    grouped_contents = {}

    for date, group in groupby(sorted_contents, key=lambda x: x[1].date()):
        grouped_contents[date] = [item[0] for item in group]
    return grouped_contents


def import_photo_metadata(sd_card_directory, file_type_set=set()):
    contents = {}
    try:
        for filename in os.listdir(sd_card_directory):
            filepath = os.path.join(sd_card_directory, filename)
            if len(file_type_set) == 0 or any(
                filename.lower().endswith(ext) for ext in file_type_set
            ):
                if os.path.isfile(filepath):  # Check if it's a file
                    contents[filepath] = get_file_creation_time(filepath)
    except FileNotFoundError:
        print("Directory not found.")
    return contents


def find_existing_images(file_paths, db_path, method="filename"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        if method == "filename":
            filter_func = is_image_unique_by_name
        elif method == "md5":
            filter_func = is_image_unique_by_md5
        else:
            raise ValueError("kwarg method must be either md5 or filename")

        file_paths = [
            (file, filter_func(file, cursor))
            for file in file_paths
            if any(file.lower().endswith(ext) for ext in raw_extensions)
        ]

    return file_paths
