import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

import formatting
import mongodb_interaction
import visualisations

class MyApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Visualisation App")
        self.root.geometry("950x600")
        self.configure_style()  # Configure the style
        self.create_widgets()

    def configure_style(self):
        # Configure the background color to light blue
        self.root.configure(bg="light blue")

    def create_description(self):
        """Write and format the description for
          the app and position at the top of the window"""
        # Description of the app's functionality and how to use it
        description = ("This app allows users to visualise their DAB radio"
                       " stations data.\nThe user can either upload clean"
                       " data in json format or raw csv files to be"
                       " processed and formatted automatically.\nFollowing"
                       " this, the user is free to select and manipulate"
                       " data visualisations.")
        description_label = tk.Label(self.root, text=description, font=("Helvetica", 14), bg='white')
        description_label.pack()

    def create_upload_buttons(self):
        """Create buttons to allow the user to upload their
        data, one for clean data and one for raw data"""
        upload_clean_button = ttk.Button(self.root, text="Clean and Upload", command=self.clean_file)
        upload_clean_button.pack()

        # Upload JSON Button
        upload_json_button = ttk.Button(self.root, text="Upload JSON", command=self.save_json_file)
        upload_json_button.pack()

    def create_widgets(self):
        """Create widgets for the user interface and
        organise positioning"""
        # Create a description of the app
        self.create_description()
        # Create buttons to allow file uploads
        self.create_upload_buttons()
        # Canvas for Matplotlib Plot
        self.canvas = FigureCanvasTkAgg(plt.figure(figsize=(6, 4)), master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Data Visualisations Section
        self.visualisation_frame = ttk.Frame(self.root)
        self.visualisation_frame.pack(fill=tk.BOTH, expand=True)

        # Visualisation Options
        visualisation_options = ttk.Combobox(self.visualisation_frame, values=["Summary Statistics", "Correlation", "Bar Graphs"])
        visualisation_options.grid(row=0, column=0, padx=10, pady=10)
        visualisation_options.set("Select Visualisation")

        # Variables Selection (you can customize this based on your data)
        variables_label = tk.Label(self.visualisation_frame, text="Select Variables:")
        variables_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Variables List (you can customize this based on your data)
        variables_listbox = tk.Listbox(self.visualisation_frame, selectmode=tk.MULTIPLE)
        variables_listbox.grid(row=2, column=0, padx=10, pady=5)

        # Generate Button
        generate_button = ttk.Button(self.visualisation_frame, text="Generate", command=self.generate_visualisation)
        generate_button.grid(row=3, column=0, padx=10, pady=5)

    def get_csv_files(self):
        """Read the user input CSV files"""
        # Request the antenna data set
        antenna_path = filedialog.askopenfilename(
            initialdir=r"C:\Computer Science\Advanced Programming\Formative\Data sets",
            title="Select the Antenna data",
            filetypes=(("csv file", "*.csv"),))
        # Check if the user canceled or no file or the wrong file was selected
        if not antenna_path:
            return None, None
        if 'antenna' not in antenna_path.lower():
            # Give feedback to the user requesting correct file
            messagebox.showinfo("Incorrect input file", "Please select the Antenna csv file")
            return None, None
        # Request the params data set
        params_path = filedialog.askopenfilename(
            initialdir=r"C:\Computer Science\Advanced Programming\Formative\Data sets",
            title="Select the Params data",
            filetypes=(("csv file", "*.csv"),))
        # Check if the user canceled or no file or the wrong file was selected
        if not params_path:
            return None, None
        if 'params' not in params_path.lower():
            # Give feedback to the user requesting correct file
            messagebox.showinfo("Incorrect input file", "Please select the Params csv file")
            return None, None
        return antenna_path, params_path

    def clean_file(self):
        """Read the user input csv then clean, format and upload"""
        # Retrieve the relevant csv file paths
        antenna_path, params_path = self.get_csv_files()
        # Check the correct files have been chosen
        if antenna_path:
            upload_data = formatting.handler(antenna_path, params_path)
            # Upload the data to the formatted_data collection
            mongodb_interaction.upload_to_mongo(upload_data)
            # Give feedback to the user notifying successful upload
            messagebox.showinfo("Success!", "Your data has been uploaded.\n"
                                "Please proceed to the Data Visualisations tab.")

    def get_json_file(self):
        """Read the formatted json file"""
        # Request the formatted json data
        json_file = filedialog.askopenfilename(
            initialdir=r"C:\Computer Science\Advanced Programming\Formative\Data sets",
            title="Select json file",
            filetypes=(("json files", "*.json"),))
        return json_file

    def save_json_file(self):
        """Read the formatted user input and upload the data"""
        # Retrieve the json file path
        json_input_file = self.get_json_file()
        if json_input_file:
            df = pd.read_json(json_input_file)
            # Get subset of data required for visualisations
            upload_data = formatting.format_json(df)
            # Upload the data to the formatted_data collection
            mongodb_interaction.upload_to_mongo(upload_data)
            # Give feedback to the user notifying successful upload
            messagebox.showinfo("Success!", 
                "Your JSON file has been uploaded.\n"
                "Please proceed to the Data Visualizations tab.")
        else:
            # Give feedback to the user notifying unsuccessful upload
            messagebox.showinfo("No file selected", "Please select your json file")

    def generate_visualisation(self):
        # Sample data for demonstration
        x = [1, 2, 3, 4, 5]
        y = [5, 4, 3, 2, 1]

        # Clear the previous plot (if any)
        plt.clf()

        # Create a simple line plot
        plt.plot(x, y, marker='o', linestyle='-')
        plt.title("Sample Line Plot")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")

        # Display the Matplotlib plot on the canvas
        self.canvas.draw()


if __name__ == '__main__':
    root = tk.Tk()
    app = MyApplication(root)
    root.mainloop()
