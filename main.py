import tkinter as tk
from tkinter import messagebox
import os

from train_schedule import TrainSchedule
from route_finder import RouteFinder
from app_gui import AppGUI

def main():
    """
    Main function to initialize and run the application.
    """
    # Ensure necessary files exist before starting
    csv_file = "train_schedule_Jabodetabek.csv"
    map_file = "Rute-KRL-1.png"
    
    if not os.path.exists(csv_file):
        messagebox.showerror(
            "Fatal Error",
            f"Gagal memuat jadwal kereta: File '{csv_file}' tidak ditemukan."
        )
        return
    if not os.path.exists(map_file):
        messagebox.showwarning(
             "File Hilang",
            f"File peta '{map_file}' tidak ditemukan. Fitur peta tidak akan berfungsi."
        )

    try:
        # 1. Load the schedule data
        schedule = TrainSchedule(csv_file)
        
        # 2. Initialize the application logic
        app_logic = RouteFinder(schedule)
        
        # 3. Create and run the GUI
        gui = AppGUI(app_logic)
        gui.mainloop()

    except Exception as e:
        messagebox.showerror(
            "Fatal Error",
            f"Terjadi kesalahan yang tidak terduga: {e}"
        )
        # For debugging purposes
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()