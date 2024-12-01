import json
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk

from PIL import Image, ImageTk

import os

import cutting_module
import styling_module
from editor_view import EditorView

import text_constants

class MainMenu:
    MAIN_MENU_GEOMETRY = '480x480'
    MAX_IMAGE_RESOLUTION = (200, 200)
    WINDOW_TITLE = 'Image Cutter'
    FILETYPES = (
        ('Image files', '*.png;*.jpg;*.jpeg'),
        ('All files', '*.*')
    )

    def __init__(self, root):
        self.root = root
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry(self.MAIN_MENU_GEOMETRY)
        self.root.resizable(False, False)

        self.window_state = {'image_uploaded': False}

        # Styling
        self.root.config(bg=styling_module.BACKGROUND_DARK_GRAY)
        self.load_custom_theme()
        ttk_style = ttk.Style()
        ttk_style.map("TButton",
                      background=[('active', styling_module.ACCENT_BLUE), ('!active', styling_module.BACKGROUND_BLACK)],
                      foreground=[('disabled', styling_module.FOREGROUND_LIGHT_GRAY),
                                  ('!disabled', styling_module.FOREGROUND_WHITE)],
                      highlightbackground=[('focus', styling_module.ACCENT_BLUE),
                                           ('!focus', styling_module.BACKGROUND_BLACK)],
                      highlightcolor=[('focus', styling_module.ACCENT_BLUE),
                                      ('!focus', styling_module.BACKGROUND_BLACK)],
                      highlightthickness=[('focus', 1), ('!focus', 0)])
        ttk_style.configure("TLabel", background=styling_module.BACKGROUND_DARK_GRAY)

        self.uploaded_image = None
        self.path_to_image = None

        self.create_grid_for_layout()

        # initializing image label
        temp_img = Image.open('./Resources/noimage.jpg')
        temp_img.thumbnail(self.MAX_IMAGE_RESOLUTION)
        self.default_image = temp_img
        self.image_canvas = tk.Canvas(self.root, background=styling_module.BACKGROUND_DARK_GRAY, width=200, height=200)
        self.image_canvas.grid(row=0, column=0, columnspan=2, pady=20)
        # initializing buttons
        self.editor_view_btn = ttk.Button(self.root, text="Editor View", command=self.open_editor_view)
        self.editor_view_btn.grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        self.upload_img_btn = ttk.Button(self.root, text="Upload Image", command=self.upload_image)
        self.upload_img_btn.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky=tk.N)
        self.upload_params_btn = ttk.Button(self.root, text="Run a Preset", command=self.upload_params_and_cut)
        self.upload_params_btn.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        # initializing text label
        self.text_label = ttk.Label(self.root, text=text_constants.MAIN_MENU_SUMMARY, wraplength=440, font=('TkDefaultFont', 10))
        self.text_label.grid(row=1, column=0, columnspan=2, pady=5, padx=10)

        self.root.after(100, self.center_image_on_canvas)

    def center_image_on_canvas(self):
        """
        Centers image on canvas widget, because by default image center
        is put in the top left corder
        """

        canv_width = self.image_canvas.winfo_width()
        canv_height = self.image_canvas.winfo_height()

        if self.window_state['image_uploaded']:
            temp = self.uploaded_image.copy()
            temp.thumbnail(self.MAX_IMAGE_RESOLUTION)
            tk_obj = ImageTk.PhotoImage(temp)
        else:
            tk_obj = ImageTk.PhotoImage(self.default_image)

        x_center = canv_width // 2
        y_center = canv_height // 2

        self.image_canvas.create_image(x_center, y_center, anchor=tk.CENTER, image=tk_obj)
        self.image_canvas.image = tk_obj

    def load_custom_theme(self):
        """Loads custom awdark tkinter ui theme"""
        theme_dir = './TTK Themes'
        print(f"Loading custom theme from: {theme_dir}")

        if os.path.exists(theme_dir):
            self.root.tk.call('lappend', 'auto_path', theme_dir)
            try:
                self.root.tk.call('package', 'require', 'awthemes')  # Loading awthemes which is main
                self.root.tk.call('package', 'require', 'ttk::theme::awdark')  # Then load specific theme
                self.root.tk.call('package', 'require', 'awdark')  # Alternate method

                self.style = ttk.Style()
                self.style.theme_use('awdark')

                print("Theme loaded successfully.")
            except tk.TclError as e:
                print(f"Error loading theme: {e}")
        else:
            print(f"Theme directory {theme_dir} does not exist")

    def create_grid_for_layout(self):
        """
        Creates layout grid for tkinter window
        :return:
        """
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=0)
        self.root.rowconfigure(3, weight=0)

    def upload_image(self):
        """
        Uploads image
        :return:
        """
        try:
            path_to_image = fd.askopenfilename(title='Select Image',
                                                initialdir='/',
                                                filetypes=self.FILETYPES)
            print('Path:', path_to_image)
            uploaded_img = Image.open(path_to_image)
        except:
            print('Image wasn\'t uploaded')
        else:
            self.uploaded_image = uploaded_img
            self.path_to_image = path_to_image
            self.window_state['image_uploaded'] = True
            self.center_image_on_canvas()

    def open_editor_view(self):
        if self.window_state['image_uploaded']:
            EditorView(tk.Toplevel(self.root), self.path_to_image)
        else:
            tk.messagebox.showinfo('Not so Fast', 'Please select an image first')

    def upload_params_and_cut(self):
        """
        Uploads cutting grid parameters from a json file
        and performs cuts on the image based on them
        :return:
        """
        if self.window_state['image_uploaded']:
            params_file_path = fd.askopenfilename(filetypes=[('JSON', '*.json')])
            with open(params_file_path) as params_file:
                data = json.load(params_file)
                if cutting_module.check_if_cutting_grid_fits(self.uploaded_image.width,
                                                             self.uploaded_image.height, data):
                    saving_folder = fd.askdirectory(title='Select folder to save cut images')
                    cutting_module.perform_cuts(self.uploaded_image.width, self.uploaded_image.height, saving_folder,
                                                self.uploaded_image, data)
                else:
                    print(params_file)
                    print(data)
                    tk.messagebox.showinfo('Error', 'Grid could\'t be applied to the image')
        else:
            tk.messagebox.showinfo('Not so Fast', 'Please select an image first')
