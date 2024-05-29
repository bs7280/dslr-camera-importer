import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import os

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        print("Selected folder:", folder_path)
        display_jpg_files(folder_path)
    else:
        print("No folder selected")

def display_jpg_files(folder_path):
    for widget in image_frame.winfo_children():
        widget.destroy()
    
    jpg_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
    
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

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Selector")
        self.root.geometry("800x600")  # Set window size

        self.select_button = tk.Button(root, text="Select Folder", command=select_folder)
        self.select_button.pack(pady=20)

        self.canvas = tk.Canvas(root)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        global image_frame
        image_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=image_frame, anchor="nw")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()