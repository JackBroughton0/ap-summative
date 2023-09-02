import os
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import formatting
import mongodb_interaction
import visualisations


class MyApplication:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def get_csv_files(self):
        """Read the user input CSV files"""
        # Request the antenna data set
        antenna_path = filedialog.askopenfilename(
            initialdir=r"C:\Computer Science\Advanced Programming\Formative\Data sets",
            title="Select the Antenna data",
            filetypes=(("csv file", "*.csv"),))
        # Request the params data set
        params_path = filedialog.askopenfilename(
            initialdir=r"C:\Computer Science\Advanced Programming\Formative\Data sets",
            title="Select the Params data",
            filetypes=(("csv file", "*.csv"),))

        return antenna_path, params_path

    def clean_file(self):
        """Read the user input csv then clean and format.
        Finally, give back the cleaned file for the user to check and reupload"""
        antenna_path, params_path = self.get_csv_files()
        # Check the correct files have been chosen
        if 'antenna' not in antenna_path.lower() or 'params' not in params_path.lower():
            # Retry file selection
            antenna_path, params_path = self.get_csv_files()
        upload_data = formatting.handler(antenna_path, params_path)

    def get_json_file(self):
        """Read the formatted json file"""
        # Request the formatted json data
        json_file = filedialog.askopenfilename(
            initialdir=r"C:\Computer Science\Advanced Programming\Formative\Data sets",
            title="Select json file",
            filetypes=(("json files", "*.json"),))
        return json_file

    def save_clean_file(self):
        """Read the user input and save the file"""
        json_input_file = self.get_json_file()
        df = pd.read_json(json_input_file)
        upload_data = formatting.format_json(df)

    def get_frames_main(self, window):
        """Get frames to contain widgets on main window"""
        # Create a frame to contain the description
        description_frame = tk.Frame(window, borderwidth=5, bg="green")
        description_frame.grid(row=0, column=0)
        # Create a Notebook widget to contain the tabs
        notebook = ttk.Notebook(window)
        notebook.grid(row=1, column=0, padx=10, pady=10)
        # Create two frames (tabs) to add to the Notebook widget
        data_upload_tab = ttk.Frame(notebook, width=400, height=250)
        data_vis_tab = ttk.Frame(notebook, width=400, height=250)
        notebook.add(data_upload_tab, text="Upload Data")
        notebook.add(data_vis_tab, text="Data Visualisations")
        return description_frame, data_upload_tab, data_vis_tab

    def get_description(self, description_frame):
        """Write a brief description of the gui"""
        text = tk.Text(description_frame, height=3)
        text.insert(tk.INSERT, """Please upload your clean data before proceeding to the data visualisations tab.\nIf your data needs cleaning first, please click on the "Upload and Clean" button.""")
        text.pack(anchor=tk.CENTER)

    def get_upload_buttons(self, data_upload_tab):
        """Initialise the data upload buttons"""
        # Create a button to allow the user to upload and clean their data
        upload_and_clean = tk.Button(data_upload_tab, text='Upload and Clean',
                                     width=10, height=3, padx=50, pady=50, command=self.clean_file)
        upload_and_clean.grid(row=0, rowspan=30, column=0, columnspan=20)
        # Create a button to allow the user to upload and save their data
        upload_and_save = tk.Button(data_upload_tab, text='Upload and Save',
                                    width=10, height=3, padx=50, pady=50, command=self.save_clean_file)
        upload_and_save.grid(row=30, rowspan=30, column=0, columnspan=20)

    def get_vis_buttons(self, data_vis_tab):
        """Create radio buttons to enable the user to
        select different types of visualisations and statistics"""
        var = tk.IntVar()
        # Radio buttons: select only 1 from 3
        R1 = tk.Radiobutton(data_vis_tab, text="Correlations", variable=var, value=1)
        R1.grid(row=0, column=0)
        R2 = tk.Radiobutton(data_vis_tab, text="Descriptive Statistics", variable=var, value=2)
        R2.grid(row=1, column=1)
        R3 = tk.Radiobutton(data_vis_tab, text="Bar Charts", variable=var, value=3)
        R3.grid(row=2, column=2)

    def setup_ui(self):
        description_frame, data_upload_tab, data_vis_tab = self.get_frames_main(self.root)
        self.get_description(description_frame)
        self.get_upload_buttons(data_upload_tab)
        self.get_vis_buttons(data_vis_tab)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    app = MyApplication(root)
    app.run()

