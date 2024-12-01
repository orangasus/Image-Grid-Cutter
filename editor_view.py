# Tkinter imports
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from PIL import ImageTk, Image, ImageDraw

# My modules
import cutting_module
import styling_module


class EditorView:
    MAX_IMAGE_RESOLUTION = (700, 700)
    WINDOW_TITLE = 'Editor View'
    PARAMETERS_NAME = ['num_horiz_rect', 'num_vert_rect', 'rect_width', 'rect_height', 'rect_horiz_dist',
                       'rect_vert_dist', 'top_left_rect_x', 'top_left_rect_y']
    FILETYPES = [('All Files', '*.*'),
                 ('JSON', '*.json')]

    def __init__(self, parent_widget, path_to_image):
        self.parent_widget = parent_widget
        self.parent_widget.title(self.WINDOW_TITLE)
        # Making editor view a full screen window
        self.parent_widget.state('zoomed')
        self.parent_widget.resizable(False, False)

        self.parent_widget.config(bg=styling_module.BACKGROUND_DARK_GRAY)

        # Dictionary with current values of each entry widget as value, key is the parameters name
        self.entries_reference_dict = {name: tk.StringVar() for name in self.PARAMETERS_NAME}
        # List of all entries widgets
        self.entries_widgets = []

        self.img_scaling_coefficient = 1

        # Dictionary with real parameters of the cutting grid - used for actual cutting
        self.cutting_grid_params = {}
        # Dictionary with real parameters of the cutting grid - used for working with scaled images (in UI)
        self.scaled_cutting_grid_params = {}

        self.create_grid_for_layout()

        self.img_to_cut = Image.open(path_to_image)
        # Tkinter uses ImageTk to display images
        self.tk_img = ImageTk.PhotoImage(self.img_to_cut)
        self.image_canvas = tk.Canvas(self.parent_widget, bg=styling_module.BACKGROUND_SOFT_BLACK)

        self.cut_button = ttk.Button(self.parent_widget, text='CUT', command=self.cut_btn_clicked)
        self.save_params_button = ttk.Button(self.parent_widget, text='SAVE PARAMS', command=self.save_params_clicked)
        self.upload_params_button = ttk.Button(self.parent_widget, text='UPLOAD PARAMS',
                                               command=self.upload_params_clicked)

        self.create_layout()

        # Functions called after a small delay, so canvas width and height are defined
        self.parent_widget.after(100, self.get_image_scaling_coefficient)
        self.parent_widget.after(110, self.center_image_on_canvas)

        self.cur_mouse_x = parent_widget.winfo_pointerx()
        self.cur_mouse_y = parent_widget.winfo_pointery()

        self.window_state = {'rect_is_dragged': False, 'up_key_pressed': False,
                             'down_key_pressed': False, 'shift_key_pressed': False}

    def create_layout(self):
        """
        Creates layout of the Editor View and
        performs necessary bindings
        """
        cur_label_row, cur_label_col = 0, 0
        cur_entry_row, cur_entry_col = 1, 0
        for ind, param_name in enumerate(self.PARAMETERS_NAME):
            cur_entry_label = ttk.Label(self.parent_widget, text=param_name.replace('_', ' '))
            cur_entry_label.grid(row=cur_label_row, column=cur_label_col + 1)

            cur_entry = ttk.Entry(self.parent_widget, textvariable=self.entries_reference_dict[param_name])
            cur_entry.bind('<KeyRelease>', self.on_entry_change)
            cur_entry.bind('<Up>', self.up_key_pressed)
            cur_entry.bind('<KeyRelease-Up>', self.up_key_released)
            cur_entry.bind('<Down>', self.down_key_pressed)
            cur_entry.bind('<KeyRelease-Down>', self.down_key_released)
            cur_entry.grid(row=cur_entry_row, column=cur_entry_col + 1)
            self.entries_widgets.append(cur_entry)

            # switch row if last column
            if ind % 2 != 0:
                cur_label_row += 2
                cur_entry_row += 2

            cur_label_col = (cur_label_col + 1) % 2
            cur_entry_col = (cur_entry_col + 1) % 2

        self.cut_button.grid(row=8, column=1, columnspan=2, pady=5)
        self.save_params_button.grid(row=9, column=1, columnspan=2, pady=5)
        self.upload_params_button.grid(row=10, column=1, columnspan=2, pady=5)
        self.image_canvas.grid(row=0, column=0, rowspan=12, sticky='news')

        self.parent_widget.bind('<Shift_L>', self.shift_key_pressed)
        self.parent_widget.bind('<KeyRelease-Shift_L>', self.shift_key_released)
        self.parent_widget.bind('<Shift_R>', self.shift_key_pressed)
        self.parent_widget.bind('<KeyRelease-Shift_R>', self.shift_key_released)

        self.image_canvas.tag_bind('rect', '<ButtonPress-1>', self.on_rectangle_mouse_click)
        self.image_canvas.tag_bind('rect', '<B1-Motion>', self.on_rectangle_mouse_held)

    def create_grid_for_layout(self):
        """
        Creates layout grid for tkinter window
        """
        self.parent_widget.columnconfigure(1, weight=0)
        self.parent_widget.columnconfigure(2, weight=0)
        self.parent_widget.columnconfigure(0, weight=1)

        for i in range(10):
            self.parent_widget.rowconfigure(i, weight=0)
        self.parent_widget.rowconfigure(11, weight=1)

    def get_image_scaling_coefficient(self):
        """
        Calculates image scaling coefficient for it to fit in the window
        """
        canv_width = self.image_canvas.winfo_width()
        canv_height = self.image_canvas.winfo_height()

        img_width = self.img_to_cut.width
        img_height = self.img_to_cut.height

        if img_height > canv_height or img_width > canv_width:
            self.img_scaling_coefficient = min(canv_width / img_width, canv_height / img_height)
            img_copy = self.img_to_cut.copy()
            img_copy.thumbnail((canv_width, canv_height))
            self.tk_img = ImageTk.PhotoImage(img_copy)

    def center_image_on_canvas(self):
        """
        Centers image on canvas widget, because by default image center
        is put in the top left corder
        """
        canv_width = self.image_canvas.winfo_width()
        canv_height = self.image_canvas.winfo_height()

        x_center = canv_width // 2
        y_center = canv_height // 2

        self.image_canvas.create_image(x_center, y_center,
                                       anchor=tk.CENTER, image=self.tk_img)
        self.image_canvas.image = self.tk_img

    # Functions responsible for updating parameters on change
    def on_params_change(self, event=None):
        for ind, k in enumerate(self.cutting_grid_params.keys()):
            self.set_text_entry_widget(self.entries_widgets[ind], str(self.cutting_grid_params[k]))

    def on_entry_change(self, event=None):
        """
        Updates real and scalable parameters when entries change
        """
        if self.check_that_all_entries_non_empty():
            self.update_real_params_from_entries()
            self.update_scaled_params_from_real_params()
            print('Real\n', self.cutting_grid_params)
            print('Scaled\n', self.scaled_cutting_grid_params)
            print()
            self.draw_cutting_grid_on_canvas()

    # Button handler function
    def save_params_clicked(self):
        """
        Saves cutting parameters in a json file
        """
        if self.check_if_all_params_int():
            json_filename = tk.filedialog.asksaveasfilename(filetypes=self.FILETYPES, defaultextension='.json')
            self.update_real_params_from_entries()
            self.update_scaled_params_from_real_params()
            with open(json_filename, 'w') as params_file:
                params_file.write(json.dumps(self.cutting_grid_params))

    def cut_btn_clicked(self):
        """
        Perform cuts based on cutting grid parameters
        """
        self.update_real_params_from_entries()
        self.update_scaled_params_from_real_params()
        if cutting_module.check_if_cutting_grid_fits(self.img_to_cut.width, self.img_to_cut.height,
                                                     self.cutting_grid_params):
            saving_dir = filedialog.askdirectory(title='Select folder to save cut images')
            if not saving_dir:
                tk.messagebox.showinfo('Error', 'No folder selected')
            else:
                cutting_module.perform_cuts(self.img_to_cut.width, self.img_to_cut.height,
                                            saving_dir, self.img_to_cut, self.cutting_grid_params,
                                            self.image_canvas.winfo_width(), self.image_canvas.winfo_height())
        else:
            tk.messagebox.showinfo('Error', 'Grid outside the image')

    def upload_params_clicked(self):
        """
        Uploads cutting parameters from a json file
        """
        params_file_path = tk.filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        with open(params_file_path) as params_file:
            data = json.load(params_file)
            for key, val in data.items():
                self.entries_reference_dict[key].set(str(val))
        self.on_entry_change()

    # Functions responsible for performing parameters check
    def check_if_all_params_int(self):
        for key, val in self.entries_reference_dict.items():
            if val == '' or not val.get().isnumeric():
                tk.messagebox.showinfo("Invalid Input",
                                       "All entries should be positive numbers and non-empty")
                return False
            return True

    def check_that_all_entries_non_empty(self):
        for entry in self.entries_widgets:
            if entry.get() == "":
                return False
        return True

    # Functions responsible for drawing cutting grid
    def draw_rectangle_on_canvas(self, x0, y0, rect_width, rect_height):
        """
        Draws a semi-transparent rectangle on canvas
        """
        rect_image = Image.new('RGBA', (rect_width, rect_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(rect_image)

        draw.rectangle(((0, 0), (rect_width, rect_height)), fill=(0, 0, 0, 127))  # Red with 50% transparency

        tk_rect_image = ImageTk.PhotoImage(rect_image)

        self.image_canvas.create_image(x0, y0, anchor=tk.NW, image=tk_rect_image, tags='rect')

        if not hasattr(self, 'image_references'):
            self.image_references = []
        self.image_references.append(tk_rect_image)

    def draw_cutting_grid_on_canvas(self):
        """
        Draws cutting grid on canvas
        """
        self.image_canvas.delete('rect')
        self.update_scaled_params_from_real_params()
        for el in cutting_module.get_coords_of_all_rect_scaled(
                round(self.img_to_cut.width * self.img_scaling_coefficient),
                round(self.img_to_cut.height * self.img_scaling_coefficient),
                self.image_canvas.winfo_width(),
                self.image_canvas.winfo_height(),
                self.scaled_cutting_grid_params
        ):
            x0 = el[0]
            y0 = el[1]
            rect_width = self.scaled_cutting_grid_params['rect_width']
            rect_height = self.scaled_cutting_grid_params['rect_height']
            self.draw_rectangle_on_canvas(x0, y0, rect_width, rect_height)

    # Functions responsible for using mouse to drag cutting grid
    def on_rectangle_mouse_held(self, event):
        """
        Changes cutting grid coordinates based on mouse drag motion
        """
        delta_mouse_x = event.x - self.cur_mouse_x
        delta_mouse_y = event.y - self.cur_mouse_y

        self.cur_mouse_x = event.x
        self.cur_mouse_y = event.y

        # Update the positions of all rectangles
        self.cutting_grid_params['top_left_rect_x'] += round(delta_mouse_x / self.img_scaling_coefficient)
        self.cutting_grid_params['top_left_rect_y'] += round(delta_mouse_y / self.img_scaling_coefficient)

        self.image_canvas.move('rect', delta_mouse_x, delta_mouse_y)
        print('Real\n', self.cutting_grid_params)
        print('Scaled\n', self.scaled_cutting_grid_params)
        print()
        self.update_entries_from_params()

    def on_rectangle_mouse_click(self, event):
        self.cur_mouse_x = event.x
        self.cur_mouse_y = event.y

    # Functions responsible for handling arrow keys and changing the entries values accordingly
    def set_text_entry_widget(self, entry_widget, text):
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, text)

    def up_key_pressed(self, event=None):
        self.window_state['up_key_pressed'] = True
        self.start_incrementing()

    def up_key_released(self, event=None):
        self.window_state['up_key_pressed'] = False

    def down_key_pressed(self, event=None):
        self.window_state['down_key_pressed'] = True
        self.start_incrementing()

    def down_key_released(self, event=None):
        self.window_state['down_key_pressed'] = False

    def shift_key_pressed(self, event=None):
        self.window_state['shift_key_pressed'] = True

    def shift_key_released(self, event=None):
        self.window_state['shift_key_pressed'] = False

    def start_incrementing(self):
        """
        Changes the entry widget value after user used arrow keys
        """
        try:
            ind = self.entries_widgets.index(self.parent_widget.focus_get())
        except ValueError:
            return
        else:
            num = 10 if self.window_state['shift_key_pressed'] else 1
            if self.window_state['down_key_pressed']:
                num *= -1
            if self.entries_widgets[ind].get() == '':
                self.set_text_entry_widget(self.entries_widgets[ind], '0')
            else:
                new_val = int(self.entries_widgets[ind].get()) + num
                if new_val >= 0:
                    self.set_text_entry_widget(self.entries_widgets[ind], str(new_val))
                    self.on_entry_change()

    def update_real_params_from_entries(self):
        self.cutting_grid_params = {key: int(val.get()) for key, val in self.entries_reference_dict.items()}

    def update_entries_from_params(self):
        for ind, k in enumerate(self.cutting_grid_params.keys()):
            self.set_text_entry_widget(self.entries_widgets[ind], self.cutting_grid_params[k])
        self.update_scaled_params_from_real_params()

    def update_scaled_params_from_real_params(self):
        for key, value in self.cutting_grid_params.items():
            if key not in ('num_vert_rect', 'num_horiz_rect'):
                self.scaled_cutting_grid_params[key] = round(int(value) * self.img_scaling_coefficient)
            else:
                self.scaled_cutting_grid_params[key] = int(value)
