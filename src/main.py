import os
import sqlite3
from datetime import datetime
import argparse
from tqdm import tqdm
from itertools import groupby
from utils import (
    group_by_date,
    import_photo_metadata,
    get_file_creation_time,
    raw_extensions,
    compute_md5,
    is_image_unique_by_md5,
)


def write_batch_to_db(cursor, batch_data):
    """Write batch data to the database."""
    try:
        cursor.executemany(
            """
            INSERT INTO photo_index (filepath, folder, filename, md5_hash, creation_time)
            VALUES (?, ?, ?, ?, ?)
        """,
            batch_data,
        )
    except sqlite3.IntegrityError as e:
        print(f"Error inserting batch: {e}")
        for item in batch_data:
            try:
                cursor.execute(
                    """
                    INSERT INTO photo_index (filepath, folder, filename, md5_hash, creation_time)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    item,
                )
            except sqlite3.IntegrityError as e:
                print(f"Error inserting file: {item[0]} with MD5 hash: {item[3]} - {e}")


def index_photos(directory, database, verbose, batch_size=100):
    """Index all RAW photos in the directory."""
    # Add other RAW file extensions as needed

    if not verbose:
        # Connect to the SQLite database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS photo_index (
                id INTEGER PRIMARY KEY,
                filepath TEXT,
                folder TEXT,
                filename TEXT,
                md5_hash TEXT UNIQUE,
                creation_time TEXT
            )
        """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_md5 ON photo_index (md5_hash)")
        conn.commit()

    batch_data = []

    folders = [folder for folder in os.walk(directory)]
    for root, _, files in tqdm(folders, desc="Folders"):
        files = [
            file
            for file in files
            if any(file.lower().endswith(ext) for ext in raw_extensions)
        ]

        # Gets iterations folder name to mention in
        iter_folder_name = os.path.basename(root)
        for file in tqdm(files, desc=f"Files: {iter_folder_name}", leave=False):
            file_path = os.path.abspath(os.path.join(root, file))
            folder = os.path.basename(os.path.dirname(file_path))
            filename = file
            md5_hash = compute_md5(file_path)
            creation_time = get_file_creation_time(file_path).isoformat()

            if verbose:
                print(
                    f"Folder: {folder}, Filename: {filename}, MD5 Hash: {md5_hash}, Creation Time: {creation_time}, Filepath: {file_path}"
                )
            else:
                # Check if the MD5 hash already exists in the database
                cursor.execute(
                    "SELECT 1 FROM photo_index WHERE md5_hash = ?", (md5_hash,)
                )
                if cursor.fetchone() is None:
                    batch_data.append(
                        (file_path, folder, filename, md5_hash, creation_time)
                    )

                # Check for duplicates within the batch
                batch_md5_hashes = [item[3] for item in batch_data]
                if batch_md5_hashes.count(md5_hash) > 1:
                    print(
                        f"Duplicate file in batch: {file_path} with MD5 hash: {md5_hash}"
                    )
                    batch_data = [item for item in batch_data if item[3] != md5_hash]

                # Batch insert if the batch size is reached
                if not verbose and len(batch_data) >= batch_size:
                    write_batch_to_db(cursor, batch_data)
                    conn.commit()
                    batch_data.clear()

    # Insert any remaining data
    if batch_data:
        write_batch_to_db(cursor, batch_data)
        conn.commit()

    if not verbose:
        conn.close()


def import_photos(sd_card_directory, database):
    """Import photos from the SD card and check against the existing index."""
    raw_extensions = {
        ".cr2",
        ".nef",
        ".arw",
        ".dng",
        ".orf",
        ".raf",
    }  # Add other RAW file extensions as needed

    # Connect to the SQLite database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    for root, _, files in os.walk(sd_card_directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in raw_extensions):
                file_path = os.path.abspath(os.path.join(root, file))
                if is_image_unique_by_md5(file_path, cursor):
                    print(f"New file found: {file_path}")

    conn.close()


if __name__ == "__main__":

    DEFAULT_INDEX_DB = "data/photo_db_real.db.sqlite"

    parser = argparse.ArgumentParser(description="Manage and index RAW photos.")
    subparsers = parser.add_subparsers(dest="command")

    parser_index = subparsers.add_parser(
        "index", help="Index RAW photos in a directory."
    )
    parser_index.add_argument(
        "directory", type=str, help="The directory to scan for RAW photos."
    )
    parser_index.add_argument(
        "--database",
        type=str,
        default=DEFAULT_INDEX_DB,
        help="The SQLite database file.",
    )
    parser_index.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Print the photo information instead of writing to the database.",
    )
    parser_index.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="The batch size for database insertion.",
    )

    # Import command
    parser_import = subparsers.add_parser(
        "import",
        help="Import photos from an SD card and check against the existing index.",
    )
    parser_import.add_argument(
        "sd_card_directory",
        type=str,
        help="The SD card directory to scan for RAW photos.",
    )
    parser_import.add_argument(
        "--database",
        type=str,
        default=DEFAULT_INDEX_DB,
        help="The SQLite database file.",
    )

    args = parser.parse_args()

    if args.command == "index":
        index_photos(args.directory, args.database, args.verbose)
    elif args.command == "import":
        contents = import_photo_metadata(
            args.sd_card_directory, file_type_set={"jpg", "jpeg"}
        )
        grouped_files = group_by_date(contents=contents)

        summary = [(k, len(grouped_files[k])) for k in grouped_files.keys()]
        breakpoint()

        # import_photos(args.sd_card_directory, args.database)
# if __name__ == "__main__":
#    directory = "test_data/"
#    database = "database/photo_index.db.sqlite"
#    index_photos(directory, database)

"""
Ok make these modifcations:
- I have a helper method that takes a list of filenames and returns a subset of files in a dicitonary organized by file create time. 
  if you click the dropdown below - it will load display the images

See this code snippet demonstrating the new helper methods. DO NOT IMPLEMENT THEM they are already working in my code. Save tokens.
```
contents = import_photo_metadata(args.sd_card_directory, file_type_set={"jpg", "jpeg"})
grouped_files = group_by_date(contents=contents)
print(grouped_files)

{
    datetime.date(2020, 9, 21): ['IMG_1951.JPG', 'IMG_1952.JPG', 'IMG_1953.JPG', 'IMG_1977.JPG'], 
    datetime.date(2021, 8, 23): ['IMG_3107.JPG', 'IMG_3108.JPG', 'IMG_3109.JPG', 'IMG_3110.JPG',  'IMG_3184.JPG'],
    ...
}

[(k, len(grouped_files[k])) for k in grouped_files.keys()]

[
    (datetime.date(2020, 9, 21), 24), 
    (datetime.date(2021, 8, 23), 18), 
    (datetime.date(2021, 9, 23), 70), 
    (datetime.date(2021, 10, 11), 25), 
... ]
```

I want the UI to list the date and number of files in that date with drop down. 
- if I click on the dropdown to ufold, I want a scrollbar of images in that date to appear.
- Provide another input box on the same row as the existing input that lets me pick a sqlite database that I will use later.


be efficient, I don't need a detailed writeup explaining the code, just the updated code. Be Brief
"""
