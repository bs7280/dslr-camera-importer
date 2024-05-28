import os
import hashlib
import sqlite3
from datetime import datetime
import argparse

def compute_md5(file_path):
    """Compute the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_file_creation_time(file_path):
    """Get the file creation datetime."""
    timestamp = os.path.getctime(file_path)
    return datetime.fromtimestamp(timestamp).isoformat()

def index_photos(directory, database, verbose):
    """Index all RAW photos in the directory."""
    raw_extensions = {'.cr2', '.nef', '.arw', '.dng', '.orf', '.raf'}  # Add other RAW file extensions as needed

    if not verbose:
        # Connect to the SQLite database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photo_index (
                id INTEGER PRIMARY KEY,
                filepath TEXT,
                folder TEXT,
                filename TEXT,
                md5_hash TEXT UNIQUE,
                creation_time TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_md5 ON photo_index (md5_hash)')
        conn.commit()

    batch_data = []

    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in raw_extensions):
                file_path = os.path.abspath(os.path.join(root, file))
                folder = os.path.basename(os.path.dirname(file_path))
                filename = file
                md5_hash = compute_md5(file_path)
                creation_time = get_file_creation_time(file_path)
                
                if verbose:
                    print(f"Folder: {folder}, Filename: {filename}, MD5 Hash: {md5_hash}, Creation Time: {creation_time}, Filepath: {file_path}")
                else:
                    # Check if the MD5 hash already exists
                    cursor.execute('SELECT 1 FROM photo_index WHERE md5_hash = ?', (md5_hash,))
                    if cursor.fetchone() is None:
                        batch_data.append((file_path, folder, filename, md5_hash, creation_time))
                
                # Batch insert if the batch size is reached
                if len(batch_data) >= 100:
                    cursor.executemany('''
                        INSERT INTO photo_index (filepath, folder, filename, md5_hash, creation_time)
                        VALUES (?, ?, ?, ?, ?)
                    ''', batch_data)
                    conn.commit()
                    batch_data.clear()

    # Insert any remaining data
    if batch_data:
        cursor.executemany('''
            INSERT INTO photo_index (filepath, folder, filename, md5_hash, creation_time)
            VALUES (?, ?, ?, ?, ?)
        ''', batch_data)
        conn.commit()
    
    if not verbose:
        conn.close()


def import_photos(sd_card_directory, database):
    """Import photos from the SD card and check against the existing index."""
    raw_extensions = {'.cr2', '.nef', '.arw', '.dng', '.orf', '.raf'}  # Add other RAW file extensions as needed

    # Connect to the SQLite database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    for root, _, files in os.walk(sd_card_directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in raw_extensions):
                file_path = os.path.abspath(os.path.join(root, file))
                md5_hash = compute_md5(file_path)

                # Check if the MD5 hash already exists
                cursor.execute('SELECT 1 FROM photo_index WHERE md5_hash = ?', (md5_hash,))
                if cursor.fetchone() is None:
                    print(f"New file found: {file_path}")

    conn.close()

if __name__ == "__main__":

    DEFAULT_INDEX_DB="data/photo_index.db.sqlite"

    parser = argparse.ArgumentParser(description="Manage and index RAW photos.")
    subparsers = parser.add_subparsers(dest="command")

    parser_index = subparsers.add_parser("index", help="Index RAW photos in a directory.")
    parser_index.add_argument("directory", type=str, help="The directory to scan for RAW photos.")
    parser_index.add_argument("--database", type=str, default=DEFAULT_INDEX_DB, help="The SQLite database file.")
    parser_index.add_argument("--verbose", action="store_true", default=False, help="Print the photo information instead of writing to the database.")
    
    # Import command
    parser_import = subparsers.add_parser("import", help="Import photos from an SD card and check against the existing index.")
    parser_import.add_argument("sd_card_directory", type=str, help="The SD card directory to scan for RAW photos.")
    parser_import.add_argument("--database", type=str, default=DEFAULT_INDEX_DB, help="The SQLite database file.")

    args = parser.parse_args()

    if args.command == "index":
        index_photos(args.directory, args.database, args.verbose)
    elif args.command == "import":
        import_photos(args.sd_card_directory, args.database)
#if __name__ == "__main__":
#    directory = "test_data/"
#    database = "database/photo_index.db.sqlite"
#    index_photos(directory, database)
