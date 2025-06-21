# main.py

import tkinter as tk
from tkinter import messagebox
import os

from train_schedule import TrainSchedule
from route_finder import RouteFinder
from app_gui import AppGUI

def main():
    """
    Fungsi utama untuk menginisialisasi dan menjalankan aplikasi.
    """
    # Pastikan file yang diperlukan ada sebelum memulai
    csv_file = "trainKRL_schedule.csv"
    map_files = ["Rute-KRL-Jabodetabek.png", "Rute-KRL-YogyakartaSoloKutoarjo.png"]
    
    if not os.path.exists(csv_file):
        messagebox.showerror(
            "Fatal Error",
            f"Gagal memuat jadwal kereta: File '{csv_file}' tidak ditemukan."
        )
        return
        
    # Peringatan jika salah satu atau kedua file peta tidak ada
    missing_maps = [f for f in map_files if not os.path.exists(f)]
    if missing_maps:
        messagebox.showwarning(
             "File Peta Hilang",
            "File peta berikut tidak ditemukan:\n" +
            ", ".join(missing_maps) + "\n" +
            "Fitur lihat peta mungkin tidak berfungsi untuk wilayah tertentu."
        )

    try:
        # 1. Muat data jadwal
        schedule = TrainSchedule(csv_file)
        
        # 2. Inisialisasi logika aplikasi
        app_logic = RouteFinder(schedule)
        
        # 3. Buat dan jalankan GUI
        gui = AppGUI(app_logic)
        gui.mainloop()

    except Exception as e:
        messagebox.showerror(
            "Fatal Error",
            f"Terjadi kesalahan yang tidak terduga: {e}"
        )
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()