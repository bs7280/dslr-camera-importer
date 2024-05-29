import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import os
from utils import (
    import_photo_metadata,
    group_by_date,
    find_existing_images,
    raw_extensions,
)
from app_import_window import ImportWindow


def display_jpg_files(folder_path):
    for widget in image_frame.winfo_children():
        widget.destroy()

    jpg_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".jpg")]

    if jpg_files:
        row, col = 0, 0
        for file in jpg_files:
            file_path = os.path.join(folder_path, file)
            img = Image.open(file_path)
            img.thumbnail((150, 150))  # Resize the image to thumbnail
            img = ImageTk.PhotoImage(img)

            label = tk.Label(image_frame, image=img)
            label.image = img
            label.grid(row=row, column=col, padx=10, pady=10)

            col += 1
            if col == 4:  # Change the number of columns as needed
                col = 0
                row += 1
    else:
        no_files_label = tk.Label(image_frame, text="No JPG files found.")
        no_files_label.pack()


def select_database():
    db_path = filedialog.askopenfilename(filetypes=[("SQLite Database", "*.sqlite")])
    if db_path:
        print("Selected database:", db_path)
    else:
        print("No database selected")


def toggle_pane(date, files, pane, button):
    if len(pane.winfo_children()) > 1:
        for widget in pane.winfo_children()[1:]:
            widget.destroy()
        button.config(text="Show")
    else:
        button.config(text="Hide")
        display_images(date, files, pane)


def display_images(date, files, pane):
    img_frame = ttk.Frame(pane)
    img_frame.pack(fill=tk.X, padx=5, pady=2)

    canvas = tk.Canvas(img_frame, height=200, width=700)  # Adjust height as needed
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(img_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    row, col = 0, 0
    for filepath in files[:10]:
        img = Image.open(filepath)
        img.thumbnail((150, 150))
        img = ImageTk.PhotoImage(img)

        label = tk.Label(inner_frame, image=img)
        label.image = img
        label.grid(row=row, column=col, padx=10, pady=10)

        col += 1
        if col == 4:
            col = 0
            row += 1

    inner_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


class App:
    def select_database(self):
        db_path = filedialog.askopenfilename(
            filetypes=[("SQLite Database", "*.sqlite")]
        )
        self.db_path = db_path
        if db_path:
            print("Selected database:", db_path)
            self.db_info_label.config(text=f"DB Path: {self.db_path}")
        else:
            print("No database selected")

    def select_folder(
        self,
    ):
        folder_path = filedialog.askdirectory()
        if folder_path:
            contents = import_photo_metadata(folder_path)  # , {"jpg", "jpeg"})
            grouped_files = group_by_date(contents)
            self.display_dates(grouped_files)
        else:
            print("No folder selected")

    def display_dates(self, grouped_files):
        for widget in date_canvas_frame.winfo_children():
            widget.destroy()

        for date, files in grouped_files.items():
            files_jpg = [
                filename
                for filename in files
                if any(filename.lower().endswith(ext) for ext in {"jpg", "jpeg"})
            ]
            files_raw = [
                filename
                for filename in files
                if any(filename.lower().endswith(ext) for ext in raw_extensions)
            ]
            pane = ttk.Frame(date_canvas_frame)
            pane.pack(fill=tk.X, padx=5, pady=2)

            header_frame = ttk.Frame(pane)
            header_frame.pack(fill=tk.X)

            # Calc unique RAW files
            if self.db_path is not None:
                matches = find_existing_images(files, self.db_path, method="filename")
                existing_count = len([x[0] for x in matches if x[1] == False])
            else:
                matches = None
                existing_count = "N/A"

            header = ttk.Label(
                header_frame,
                text=f"{date} ({len(files_jpg)} files {existing_count} Existing)",
            )
            header.pack(side=tk.LEFT, padx=5, pady=2)

            toggle_button = ttk.Button(header_frame, text="Show", width=6)
            toggle_button.pack(side=tk.RIGHT, padx=5)
            toggle_button.bind(
                "<Button-1>",
                lambda event, date=date, files=files_jpg, pane=pane, button=toggle_button: toggle_pane(
                    date, files, pane, button
                ),
            )

            upload_button = ttk.Button(header_frame, text="Upload", width=6)
            upload_button.pack(side=tk.RIGHT, padx=5)
            upload_button.bind(
                "<Button-1>",
                lambda event, date=date, files=files_raw: self.open_import_window(
                    date, files
                ),
            )

    def __init__(self, root):
        self.root = root
        self.root.title("Folder Selector")
        self.root.geometry("1200x800")

        input_frame = tk.Frame(root)
        input_frame.pack(pady=10, padx=10)

        self.select_button = tk.Button(
            input_frame, text="Select Folder", command=self.select_folder
        )
        self.select_button.grid(row=0, column=0, padx=10)

        self.db_path = (
            "/Users/benshaughnessy/Dropbox/Photographs/photo_db_real.db.sqlite"
        )
        self.db_button = tk.Button(
            input_frame, text="Select Database", command=self.select_database
        )
        self.db_button.grid(row=0, column=1, padx=10)

        self.db_info_label = tk.Label(input_frame, text=f"DB Path: {self.db_path}")
        self.db_info_label.grid(row=0, column=3, padx=10)

        global date_frame, date_canvas_frame
        date_frame = tk.Frame(root)
        date_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        date_canvas = tk.Canvas(date_frame)
        date_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        date_scrollbar = ttk.Scrollbar(
            date_frame, orient=tk.VERTICAL, command=date_canvas.yview
        )
        date_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        date_canvas.configure(yscrollcommand=date_scrollbar.set)

        date_canvas_frame = ttk.Frame(date_canvas)
        date_canvas.create_window((0, 0), window=date_canvas_frame, anchor="nw")

        date_canvas_frame.bind(
            "<Configure>",
            lambda e: date_canvas.configure(scrollregion=date_canvas.bbox("all")),
        )

    def open_import_window(self, collection_date, files_to_import):
        ImportWindow(
            self.root,
            "/Users/benshaughnessy/Dropbox/Photographs/",
            collection_date,
            files_to_import,
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
