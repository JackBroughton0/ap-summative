import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import matplotlib.pyplot as plt
import pandas as pd

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

    def create_widgets(self):
        # Description 
        description = ("This app allows users to visualise their DAB radio"
                       " stations data.\nThe user can either upload clean"
                       " data in json format or raw csv files to be"
                       " processed and formatted automatically.\nFollowing"
                       " this, the user is free to select and manipulate"
                       " data visualisations.")
        description_label = tk.Label(self.root, text=description, font=("Helvetica", 14), bg='white')
        description_label.pack()

        # Upload and Clean Button
        upload_clean_button = ttk.Button(self.root, text="Upload and Clean", command=self.upload_and_clean)
        upload_clean_button.pack()

        # Upload JSON Button
        upload_json_button = ttk.Button(self.root, text="Upload JSON", command=self.upload_json)
        upload_json_button.pack()

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

    def upload_and_clean(self):
        # Implement your file upload and cleaning logic here
        # You can use filedialog.askopenfilename() for file selection

        # For demonstration, we'll just print a message
        print("Uploading and Cleaning Data")

    def upload_json(self):
        # Implement your JSON upload logic here
        # You can use filedialog.askopenfilename() for JSON file selection

        # For demonstration, we'll just print a message
        print("Uploading JSON Data")

    def generate_visualisation(self):
        # Implement your data visualisation logic here based on user selections
        # You can use matplotlib for plotting

        # For demonstration, we'll just show a sample plot
        plt.figure(figsize=(6, 4))
        plt.plot([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
        plt.title("Sample Plot")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.show()

if __name__ == '__main__':
    root = tk.Tk()
    app = MyApplication(root)
    root.mainloop()
