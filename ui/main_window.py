import customtkinter as ctk
from tkinter import filedialog


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Historic Training Records")
        self.geometry("900x600")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.training_folder = ctk.StringVar()
        self.output_file = ctk.StringVar()

        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Historic Training Records",
            font=("Helvetica", 28, "bold")
        )

        title.pack(pady=20)

        # ----------------------------
        # Training Folder
        # ----------------------------

        folder_frame = ctk.CTkFrame(self)

        folder_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            folder_frame,
            text="Training Folder"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        folder_entry = ctk.CTkEntry(
            folder_frame,
            textvariable=self.training_folder
        )

        folder_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=10,
            pady=10
        )

        ctk.CTkButton(
            folder_frame,
            text="Browse",
            command=self.select_training_folder
        ).pack(
            side="right",
            padx=10,
            pady=10
        )

        # ----------------------------
        # Output File
        # ----------------------------

        output_frame = ctk.CTkFrame(self)

        output_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            output_frame,
            text="Output Excel File"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        output_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_file
        )

        output_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=10,
            pady=10
        )

        ctk.CTkButton(
            output_frame,
            text="Browse",
            command=self.select_output_file
        ).pack(
            side="right",
            padx=10,
            pady=10
        )

        # ----------------------------
        # Log Window
        # ----------------------------

        ctk.CTkLabel(
            self,
            text="Log"
        ).pack(anchor="w", padx=35)

        self.log_box = ctk.CTkTextbox(
            self,
            height=250
        )

        self.log_box.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        self.log("Application started.")

        # ----------------------------
        # Start Button
        # ----------------------------

        ctk.CTkButton(
            self,
            text="Start Processing",
            height=45,
            command=self.start_processing
        ).pack(
            pady=20
        )

    def log(self, message):

        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def select_training_folder(self):

        folder = filedialog.askdirectory()

        if folder:
            self.training_folder.set(folder)
            self.log(f"Training folder selected:\n{folder}")

    def select_output_file(self):

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Workbook", "*.xlsx")
            ]
        )

        if filename:
            self.output_file.set(filename)
            self.log(f"Output file selected:\n{filename}")

    def start_processing(self):

        self.log("")
        self.log("Processing has not been implemented yet.")