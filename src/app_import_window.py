import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import datetime
import shutil


class ImportWindow:
    def __init__(self, parent, parent_dir, collection_date: datetime.date, file_paths):
        self.root = parent
        # self.root.title("Import Files")
        # self.root.geometry("1200x1200")
        self.window = tk.Toplevel(self.root)
        self.window.title("Import Files")
        self.window.geometry("1200x800")

        self.parent = tk.Frame(self.window)
        self.parent.pack(pady=10, padx=10)
        ## Real

        self.collection_date_str = datetime.datetime.strftime(
            collection_date, "%Y-%m-%d"
        )
        self.parent_dir = parent_dir
        self.file_paths = file_paths
        self.selected_files = set()
        # self.window = tk.Toplevel(parent)
        # self.window.title("Import Files")
        # self.window.geometry("800x1200")

        self.folder_label = tk.Label(self.parent, text="Destination Folder:")
        self.folder_label.grid(row=0, column=0, padx=10)

        # upload_date_str = tk.Label(self.parent, text=self.collection_date_str)
        # upload_date_str.grid(row=0, column=1, padx=10)

        self.folder_entry = tk.Entry(self.parent, width=50)
        self.folder_entry.insert(0, f"{self.collection_date_str} ")
        self.folder_entry.grid(row=0, column=1, padx=10)

        self.upload_button = tk.Button(
            self.parent, text="Upload", command=self.upload_files
        )
        self.upload_button.grid(row=0, column=2, padx=10)

        self.image_frame = ttk.Frame(self.window)
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        self.display_images()

    def load_images(self):
        for file_path in self.file_paths:
            pass

    def display_images(self):
        canvas = tk.Canvas(self.image_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            self.image_frame, orient=tk.VERTICAL, command=canvas.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        row, col = 0, 0
        for file_path in self.file_paths:
            frame = tk.Frame(inner_frame, bd=0, relief=tk.FLAT)
            frame.grid(row=row, column=col, padx=10, pady=10)

            img = Image.open(file_path)
            img.thumbnail((300, 300))
            img = ImageTk.PhotoImage(img)

            label = tk.Label(frame, image=img)
            label.image = img
            label.pack()
            label.bind(
                "<Button-1>",
                lambda e, file_path=file_path, frame=frame: self.toggle_selection(
                    file_path, frame
                ),
            )

            col += 1
            if col == 3:
                col = 0
                row += 1

        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def toggle_selection(self, file_path, frame):
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            frame.config(relief=tk.FLAT, bd=0)
        else:
            self.selected_files.add(file_path)
            frame.config(relief=tk.FLAT, bd=2, bg="white")

    def upload_files(self):
        destination_folder = self.folder_entry.get()

        if destination_folder:
            files_to_import = list(self.selected_files)
            # folder_name = f"{self.collection_date_str} {destination_folder}"
            full_folder_path = os.path.join(self.parent_dir, destination_folder)
            if len(files_to_import) > 0:
                result = messagebox.askyesno(
                    "Confirmation",
                    f"Upload {len(files_to_import)} files to {full_folder_path}?",
                )

                if result:
                    # Ensure that the destination folder exists, create it if it doesn't
                    os.makedirs(full_folder_path, exist_ok=True)
                    for file in files_to_import:

                        destination_file = os.path.join(
                            full_folder_path, os.path.basename(file)
                        )

                        if os.path.exists(destination_file):
                            print(
                                f"Warning: File {destination_file} already exists in destination folder."
                            )
                            # You can choose to handle this case as you wish, for example, skip the copying
                        else:
                            # Copy the file to the destination folder
                            print(f"Copying {file}")
                            shutil.copy(file, full_folder_path)
                    print("Done")
            else:
                print("Must select some files")
        else:
            print("No destination folder specified")


if __name__ == "__main__":
    files_to_import = [
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1951.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1952.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1953.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1954.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1955.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1956.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1957.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1958.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1959.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1963.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1964.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1965.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1966.jpg",
        "/Volumes/EOS_DIGITAL/DCIM/100CANON/IMG_1967.jpg",
    ]
    root = tk.Tk()
    app = ImportWindow(
        root,
        "/Users/benshaughnessy/Dropbox/Photographs/",
        datetime.date(2023, 1, 1),
        files_to_import,
    )
    root.mainloop()
