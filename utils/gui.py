import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")


class GUI:
    def set_grid_data(self):
        self.data["dim_x"] = int(self.dimx_line.get())
        self.data["dim_y"] = int(self.dimy_line.get())
        self.data["dim_z"] = int(self.dimz_line.get())
        self.data["spacing"] = float(self.spacing_line.get())
        self.data["advanced"] = self.checkbox_var.get()
        if (
            self.data["dim_x"]
            and self.data["dim_y"]
            and self.data["dim_z"]
            and self.data["spacing"]
            and self.data["advanced"]
        ):
            self.display_grid.delete(0, ctk.END)
            self.display_grid.insert(
                ctk.END,
                f"Your Simulation will contain an environment of {self.data['dim_x']}m x {self.data['dim_y']}m x {self.data['dim_z']}m and with a cell size of {self.data['spacing']}m^3 in extended mode",
            )
        if (
            self.data["dim_x"]
            and self.data["dim_y"]
            and self.data["dim_z"]
            and self.data["spacing"]
            and not self.data["advanced"]
        ):
            self.display_grid.delete(0, ctk.END)
            self.display_grid.insert(
                ctk.END,
                f"Your Simulation will contain an environment of {self.data['dim_x']}m x {self.data['dim_y']}m x {self.data['dim_z']}m and with a cell size of {self.data['spacing']}m^3 in normal mode",
            )

    def set_path(self):
        self.data["save_path"] = ctk.filedialog.askdirectory()
        if self.data["save_path"]:
            results_path = self.data["save_path"]
            self.path_display.delete(0, ctk.END)
            self.path_display.insert(ctk.END, results_path)

    def set_name(self):
        self.data["folder_name"] = self.entry_line.get()
        if self.data["folder_name"]:
            self.display_line.delete(0, ctk.END)
            self.display_line.insert(
                ctk.END, f"{self.data['folder_name']} is the name of your simulation"
            )

    def set_vehicle(self):
        self.data["vehicle_path"] = ctk.filedialog.askopenfilename()
        if self.data["vehicle_path"]:
            self.vehicle_display.delete(0, ctk.END)
            self.vehicle_display.insert(ctk.END, self.data["vehicle_path"])

    def set_slices(self):
        self.data["slice_number"] = int(self.number_line.get())
        self.data["slice_distance"] = float(self.distance_line.get())
        if self.data["slice_number"] and self.data["slice_distance"]:
            self.display_slices.delete(0, ctk.END)
            self.display_slices.insert(
                ctk.END,
                f"Your Simulation will contain {self.data['slice_number']} cross-sections in an interval of "
                f"{self.data['slice_distance']}m in z-direction",
            )

    def __init__(self):
        self.root = ctk.CTk()
        self.data = {}
        self.setup_ui()

    def setup_ui(self):
        left_column = ctk.CTkFrame(self.root)
        left_column.pack(side="left")
        right_column = ctk.CTkFrame(self.root)
        right_column.pack(side="left")

        # ---- frame for the grid data -------
        frame_grid = ctk.CTkFrame(master=right_column)
        frame_grid.pack(pady=15, padx=15, fill="both", expand=True)
        title_grid = ctk.CTkLabel(
            master=frame_grid, text="Simulation settings", font=("Roboto", 18), pady=10
        )
        title_grid.grid(row=0, column=0, sticky="ew", columnspan=3)
        line1 = ttk.Separator(master=frame_grid, orient="horizontal")
        line1.grid(row=1, column=0, sticky="ew", columnspan=3)
        entry0 = ctk.CTkLabel(
            master=frame_grid,
            pady=5,
            text="In this section you select the settings for the simulation. The environment is centered at (0, 0, 0).",
        )
        entry0.grid(row=2, column=0, sticky="ew", columnspan=3)
        line11 = ttk.Separator(master=frame_grid, orient="horizontal")
        line11.grid(row=3, column=0, sticky="ew", columnspan=3)
        entry00 = ctk.CTkLabel(
            master=frame_grid,
            pady=5,
            text="Please enter the the dimensions of the environment you want to simulate in meters (integer value):",
        )
        entry00.grid(row=4, column=0, sticky="ew", columnspan=3)
        line12 = ttk.Separator(master=frame_grid, orient="horizontal")
        line12.grid(row=7, column=0, sticky="ew", columnspan=3, pady=5)
        entry01 = ctk.CTkLabel(
            master=frame_grid,
            pady=5,
            text="Please enter the edge length of the cells in meters (float value, e.g. 0.12):",
        )
        entry01.grid(row=8, column=0, sticky="ew", columnspan=3)
        self.dimx_line = ctk.CTkEntry(master=frame_grid, width=100)
        self.dimx_line.grid(row=6, column=0)
        self.dimy_line = ctk.CTkEntry(master=frame_grid, width=100)
        self.dimy_line.grid(row=6, column=1)
        self.dimz_line = ctk.CTkEntry(master=frame_grid, width=100)
        self.dimz_line.grid(row=6, column=2)
        title_dimx = ctk.CTkLabel(master=frame_grid, text="Dimension in x-Direction:")
        title_dimx.grid(row=5, column=0)
        title_dimy = ctk.CTkLabel(master=frame_grid, text="Dimension in y-Direction:")
        title_dimy.grid(row=5, column=1)
        title_dimz = ctk.CTkLabel(master=frame_grid, text="Dimension in z-Direction:")
        title_dimz.grid(row=5, column=2)
        title_spacing = ctk.CTkLabel(master=frame_grid, text="Edge length of cells:")
        title_spacing.grid(row=9, column=1)
        self.spacing_line = ctk.CTkEntry(master=frame_grid, width=100)
        self.spacing_line.grid(row=10, column=1, pady=5)

        entry02 = ctk.CTkLabel(
            master=frame_grid,
            pady=5,
            text="Please check the box if you want to use extended mode and click confirm:",
        )
        entry02.grid(row=11, column=0, sticky="ew", columnspan=3)
        self.checkbox_var = tk.BooleanVar()
        checkbox = ctk.CTkCheckBox(
            frame_grid, text="Extended mode", variable=self.checkbox_var
        )
        checkbox.grid(row=12, column=1)
        confirm_button0 = ctk.CTkButton(
            master=frame_grid, text="Confirm", command=self.set_grid_data
        )
        confirm_button0.grid(row=13, column=1, pady=5)
        self.display_grid = ctk.CTkEntry(master=frame_grid, width=700)
        self.display_grid.grid(row=14, column=0, sticky="ew", columnspan=3, pady=5)

        # ---- frame for the 3d model for the vehicle  ------
        frame_vehicle = ctk.CTkFrame(master=right_column)
        frame_vehicle.pack(pady=15, padx=15, fill="both", expand=True)
        title_vehicle = ctk.CTkLabel(
            master=frame_vehicle,
            text="Select 3-D Model for Vehicle",
            font=("Roboto", 18),
            pady=10,
        )
        title_vehicle.pack()
        line2 = ttk.Separator(master=frame_vehicle, orient="horizontal")
        line2.pack(fill="x")
        entry3 = ctk.CTkLabel(
            master=frame_vehicle,
            pady=5,
            text="Please select the 3-D Model, that the application should load"
            " and use as the vehicle",
        )
        entry3.pack()
        browse_button2 = ctk.CTkButton(
            master=frame_vehicle, text="Browse", command=self.set_vehicle
        )
        browse_button2.pack()
        entry4 = ctk.CTkLabel(
            master=frame_vehicle, text="The following 3-D Model is currently selected:"
        )
        entry4.pack()
        self.vehicle_display = ctk.CTkEntry(master=frame_vehicle, width=500)
        self.vehicle_display.pack(pady=5)

        # ----- frame for the name and path  -------
        frame_path = ctk.CTkFrame(master=left_column)
        frame_path.pack(pady=15, padx=15, fill="both", expand=True)
        title_save = ctk.CTkLabel(
            master=frame_path, text="Save results", font=("Roboto", 18), pady=10
        )
        title_save.pack()
        line1 = ttk.Separator(master=frame_path, orient="horizontal")
        line1.pack(fill="x")
        entry1 = ctk.CTkLabel(
            master=frame_path,
            pady=5,
            text="Please select, where the simulation results should be saved.\n"
            "If no path is selected the results will be saved to simulation_"
            "results in the applications directory\n",
        )
        entry1.pack()
        browse_button = ctk.CTkButton(
            master=frame_path, text="Browse", command=self.set_path
        )
        browse_button.pack()
        entry2 = ctk.CTkLabel(
            master=frame_path, text="The following path is currently selected:"
        )
        entry2.pack()
        self.path_display = ctk.CTkEntry(master=frame_path, width=500)
        self.path_display.pack(pady=5)

        text = ctk.CTkLabel(
            master=frame_path,
            text="Please enter the name for the simulation and click confirm:",
        )
        text.pack()
        self.entry_line = ctk.CTkEntry(master=frame_path, width=500)
        self.entry_line.pack(pady=5)
        confirm_button = ctk.CTkButton(
            master=frame_path, text="Confirm", command=self.set_name
        )
        confirm_button.pack()
        self.display_line = ctk.CTkEntry(master=frame_path, width=500)
        self.display_line.pack(pady=5)
        text2 = ctk.CTkLabel(
            master=frame_path,
            text="If no name is entered, a timestamp is used as a name.",
        )
        text2.pack()

        # ----- frame for the slices  ------
        frame_slices = ctk.CTkFrame(master=left_column)
        frame_slices.pack(pady=15, padx=15, fill="both", expand=True)
        title_slices = ctk.CTkLabel(
            master=frame_slices,
            text="Select cross-sections in z-direction",
            font=("Roboto", 18),
            pady=10,
        )
        title_slices.pack()
        line3 = ttk.Separator(master=frame_slices, orient="horizontal")
        line3.pack(fill="x")
        entry5 = ctk.CTkLabel(
            master=frame_slices,
            pady=5,
            text="The first cross section is cut at z=0m.\nPlease enter the "
            "number of cross sections for your simulation(integer value):",
        )
        entry5.pack()
        self.number_line = ctk.CTkEntry(master=frame_slices, width=500)
        self.number_line.pack(pady=5)
        entry6 = ctk.CTkLabel(
            master=frame_slices,
            pady=5,
            text="Please enter the distance between each cross section in meters(float value, e.g. 0.35) and "
            "click confirm:",
        )
        entry6.pack()
        self.distance_line = ctk.CTkEntry(master=frame_slices, width=500)
        self.distance_line.pack(pady=5)
        confirm_button2 = ctk.CTkButton(
            master=frame_slices, text="Confirm", command=self.set_slices
        )
        confirm_button2.pack()
        self.display_slices = ctk.CTkEntry(master=frame_slices, width=500)
        self.display_slices.pack(pady=5)

        final_text = ctk.CTkLabel(
            master=right_column,
            text="To start the application, recheck your inputs and close this window",
            font=("Roboto", 18),
            pady=5,
        )
        final_text.pack()

    def get_inputs(self):
        return self.data

    def run(self):
        self.root.mainloop()
