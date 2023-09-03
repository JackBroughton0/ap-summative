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
        self.configure_style()
        self.selected_visualisation = tk.StringVar()
        self.c18a_var = tk.BooleanVar()
        self.c18f_var = tk.BooleanVar()
        self.c188_var = tk.BooleanVar()
        self.create_widgets()

    def configure_style(self):
        # Configure the background color to light blue
        self.root.configure(bg="light blue")

    def create_description(self):
        """Write and format the description for
          the app and position at the top of the window"""
        # Description of the app's functionality and how to use it
        description = ("Visualise your DAB radio stations data!\n"
                       " Upload a clean json file or raw csv files"
                       " to be processed.\nThen generate"
                       " your data visualisations.")
        description_label = tk.Label(self.root, text=description, font=("Helvetica", 14), bg='white')
        description_label.pack(anchor='n')

    def create_upload_buttons(self):
        """Create buttons to allow the user to upload their
        data, one for clean data and one for raw data"""
        # Clean and Upload button
        clean_raw_button = ttk.Button(self.root, text="Clean and Upload",
                                      padding=(10, 5), width=20,
                                      command=self.clean_file)
        clean_raw_button.pack(anchor='nw')

        # Upload JSON Button
        upload_json_button = ttk.Button(self.root, text="Upload JSON",
                                        padding=(10, 5), width=20,
                                        command=self.save_json_file)
        upload_json_button.pack(anchor='nw')

    def create_message_label(self):
        """Create a label to display a message initially"""
        self.message_label = tk.Label(self.canvas_widget, text="No visualisation available yet", font=("Helvetica", 12))
        self.message_label.pack(fill=tk.BOTH, expand=True)

    def create_visualisation_canvas(self):
        """Create a canvas to display visualisations
        on the main window"""
        self.canvas = FigureCanvasTkAgg(plt.figure(figsize=(6, 4)), master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def create_dab_checkbuttons(self):
        """Provide checkbuttons to determine which
        DAB multiplexes to generate visualisations for"""
        # DAB multiplex selection
        dab_multiplex = tk.Label(self.visualisation_frame, text="Select DAB Multiplex:")
        dab_multiplex.grid(row=0, column=0, padx=10, sticky="w")
        # Check buttons for 'C18A', 'C18F', 'C188'
        c18a_checkbox = ttk.Checkbutton(self.visualisation_frame, text="C18A", variable=self.c18a_var)
        c18a_checkbox.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        c18f_checkbox = ttk.Checkbutton(self.visualisation_frame, text="C18F", variable=self.c18f_var)
        c18f_checkbox.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        c188_checkbox = ttk.Checkbutton(self.visualisation_frame, text="C188", variable=self.c188_var)
        c188_checkbox.grid(row=0, column=3, padx=5, pady=2, sticky="w")

    def create_vis_combobox(self):
        """Create a combobox where the dropdown
        provides a list of the available visualisations"""
        visualisation_label = tk.Label(self.visualisation_frame, text="Select Visualisation:")
        visualisation_label.grid(row=1, column=0, padx=10, pady=(10,2), sticky="w")
        # Instantiate combobox and set state to read only
        visualisation_options = ttk.Combobox(self.visualisation_frame,
                                            values=["Summary Statistics",
                                                    "Correlation",
                                                    "Bar Graphs"],
                                            textvariable=self.selected_visualisation,
                                            state="readonly")
        visualisation_options.grid(row=2, column=0, padx=10, pady=(2,50))
        # Set to the client's initial information needs
        visualisation_options.set("Summary Statistics")

    def create_vars_listbox(self):
        """Create a listbox containing the variables
        that can be included in the visualisations"""
        variables_label = tk.Label(self.visualisation_frame, text="Select Variables:")
        variables_label.grid(row=3, column=0, padx=10, pady=(5,1), sticky="w")

        self.variables_listbox = tk.Listbox(self.visualisation_frame, selectmode=tk.MULTIPLE)
        self.variables_listbox.grid(row=4, column=0, padx=10, pady=2)
        # Populate the Listbox with variables
        variables = ["Site", "Freq", "Block", "Serv Label1", "Serv Label2",
                      "Serv Label3", "Serv Label4", "Serv Label10"]
        for variable in variables:
            self.variables_listbox.insert(tk.END, variable)

    def format_visual_frame(self):
        """Organise the Data Visualisation Frame by
        creating and positioning the necessary widgets"""
        # Provide DAB multiplex options 
        self.create_dab_checkbuttons()
        # Provide visualisation type options
        self.create_vis_combobox()
        # Provide variables options
        self.create_vars_listbox()

    def create_generate_button(self):
        """Create a button to allow visualisations
        to be displayed"""
        generate_button = ttk.Button(self.visualisation_frame, text="Generate", command=self.generate_visualisation)
        generate_button.grid(row=5, column=0, padx=10, pady=5)
    
    def create_widgets(self):
        """Create widgets for the user interface and
        organise positioning"""
        # Create a description of the app
        self.create_description()
        # Create buttons to allow file uploads
        self.create_upload_buttons()
        # Canvas for Matplotlib plots
        self.create_visualisation_canvas()
        # Display a message before the first visualisation is created
        self.create_message_label()
        # Data Visualisations Section
        self.visualisation_frame = ttk.Frame(self.root)
        self.visualisation_frame.pack(fill=tk.BOTH, expand=True)
        # Organise the Data Visualisation frame
        self.format_visual_frame()
        # Create generate button to display visualisations
        self.create_generate_button()

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
        """Pass the selected visualisation options to
        the visualisations module and plot the outputs"""
        # Get the indices of the selected variables
        selected_indices = self.variables_listbox.curselection()
        # Retrieve the selected variable names
        selected_vars = [self.variables_listbox.get(idx) for idx in selected_indices]   
        # Store the user's visualisation requirements
        vis_input = {"C18A": self.c18a_var.get(),
                     "C18F": self.c18f_var.get(),
                     "C188": self.c188_var.get(),
                     "Visualisation": self.selected_visualisation.get(),
                     "Columns": selected_vars}
        # Create the visualisation in the visualisations module
        vis = visualisations.handler(vis_input)


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

        # Hide the message label and display the visualisation
        self.message_label.pack_forget()
        self.canvas_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas.draw()


if __name__ == '__main__':
    root = tk.Tk()
    app = MyApplication(root)
    root.mainloop()
