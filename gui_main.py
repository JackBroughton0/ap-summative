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

def get_user_file():
    """Read the user input csv"""
    user_file_selection = filedialog.askopenfile(
        initialdir=r"C:\Computer Science\Advanced Programming\Formative\Data sets",
        title="Select a csv file",
        filetypes=(("csv files", "*.csv"),))
    try:
        user_file = user_file_selection.name
    except AttributeError:
        "Please select a file pop up window"
    # user_file = "File entered in text above button"
    # try:
    #     with open(user_file, 'r') as csv_file:
    #         all_lines = csv_file.readlines()
    # except NotADirectoryError:
    #     "Please enter a valid directory and file name."
    #UnboundLocalError: cannot access local variable 'user_file' where it is not associated with a value
    return user_file

def clean_file():
    """Read the user input csv then clean and format.
    Finally, give back the cleaned file for the user to check and reupload"""
    user_file = get_user_file()
    try:
        df_input = pd.read_csv(user_file, dtype='str')
    except ValueError:
        "Don't worry about this now, use with open and clean lines"

def save_clean_file():
    """Read the user input and save the file"""
    clean_user_file = get_user_file()


def get_frames_main(window):
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

def get_description(description_frame):
    """Write a brief description of the gui"""
    text = tk.Text(description_frame, height=3)
    text.insert(tk.INSERT, """Please upload your clean data before proceeding to the data visualisations tab.\nIf your data needs cleaning first, please click on the "Upload and Clean" button.""")
    text.pack(anchor=tk.CENTER)

def get_upload_buttons(data_upload_tab):
    """Initialise the data upload buttons"""
    # Create a button to allow the user to upload and clean their data
    upload_and_clean = tk.Button(data_upload_tab, text='Upload and Clean',
                                 width=10, height=3, padx=50, pady=50, command=clean_file)
    upload_and_clean.grid(row=0, rowspan=30, column=0, columnspan=20)
    # Create a button to allow the user to upload and save their data
    upload_and_save = tk.Button(data_upload_tab, text='Upload and Save',
                                width=10, height=3, padx=50, pady=50, command=save_clean_file)
    upload_and_save.grid(row=30, rowspan=30, column=0, columnspan=20)

def get_vis_buttons(data_vis_tab):
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

def handler():
    """Create GUI to accept csv upload and
    present data visualisations"""
    window = tk.Tk()
    window.title("Main Window")
    window.geometry("600x500")

    description_frame, data_upload_tab, data_vis_tab = get_frames_main(window)

    get_description(description_frame)

    get_upload_buttons(data_upload_tab)

    get_vis_buttons(data_vis_tab)



    window.mainloop()

if __name__ == '__main__':
    os.chdir('AP-SUMMATIVE')
    handler()