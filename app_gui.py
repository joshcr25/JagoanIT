import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import List, Dict, Any

from route_finder import RouteFinder
from data_models import Region  # Pastikan impor ini ada dari langkah sebelumnya


class Tooltip:
    """Membuat tooltip untuk widget tertentu."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("Arial", 10, "normal"),
                         fg="#000") # Set text color for tooltip
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None


class AppGUI(tk.Tk):
    """
    Antarmuka pengguna grafis utama untuk aplikasi Jadwal Kereta.
    """

    def __init__(self, app_logic: RouteFinder):
        super().__init__()
        self.app_logic = app_logic
        self.title("Pencari Rute KRL")
        self.geometry("850x650")
        
        # Configure styles for ttk widgets
        style = ttk.Style(self)
        self.option_add("*TCombobox*Listbox.foreground", "#000") # For combobox dropdown items

        # Set foreground color for various ttk widgets
        style.configure("TLabel", font=("Arial", 10), foreground="#000")
        style.configure("TButton", font=("Arial", 10), foreground="#000")
        style.configure("Accent.TButton", font=("Arial", 10, "bold"), foreground="#000")
        style.configure("TCombobox", font=("Arial", 10), foreground="#000") # For the entry part of the combobox
        style.configure("TEntry",font=("Arial", 10), foreground="#000")
        style.configure("TLabelframe.Label",font=("Arial", 10), foreground="#000") # For the title text of LabelFrames


        self.selected_region = tk.StringVar()
        self.regions = {r.value: r for r in Region}

        self.station_info = {
            "Jakarta Kota": {"address": "Jl. Stasiun Kota No. 1, Pinangsia, Taman Sari, Jakarta Barat, 11110", "elevation": "+4 m"},
            "Jayakarta": {"address": "Jl. Pangeran Jayakarta, Mangga Dua Selatan, Sawah Besar, Jakarta Pusat, 10730", "elevation": "+5 m"},
            "Mangga Besar": {"address": "Jl. Karang Anyar, Karang Anyar, Sawah Besar, Jakarta Pusat, 10740", "elevation": "+13 m"},
            "Sawah Besar": {"address": "Jl. K.H. Samanhudi, Ps. Baru, Sawah Besar, Jakarta Pusat, 10710", "elevation": "+15 m"},
            "Juanda": {"address": "Jl. Ir. H. Juanda 1, Ps. Baru, Sawah Besar, Jakarta Pusat, 10710", "elevation": "+17 m"},
            "Gondangdia": {"address": "Jl. Srikaya I, Kb. Sirih, Menteng, Jakarta Pusat, 10340", "elevation": "+20 m"},
            "Cikini": {"address": "Jl. Cikini Raya, Cikini, Menteng, Jakarta Pusat, 10330", "elevation": "+20 m"},
            "Manggarai": {"address": "Jl. Manggarai Utara 1, Manggarai, Tebet, Jakarta Selatan, 12850", "elevation": "+13 m"},
            "Tebet": {"address": "Jl. Tebet Raya, Tebet Timur, Tebet, Jakarta Selatan, 12820", "elevation": "+18 m"},
            "Cawang": {"address": "Jl. Letjen M.T. Haryono, Cikoko, Pancoran, Jakarta Selatan, 12770", "elevation": "+26 m"},
            "Duren Kalibata": {"address": "Jl. Raya Kalibata, Rawajati, Pancoran, Jakarta Selatan, 12750", "elevation": "+28 m"},
            "Pasar Minggu Baru": {"address": "Jl. Rawajati Timur, Rawajati, Pancoran, Jakarta Selatan, 12750", "elevation": "+32 m"},
            "Pasar Minggu": {"address": "Jl. Pasar Minggu, Pasar Minggu, Jakarta Selatan, 12520", "elevation": "+36 m"},
            "Tanjung Barat": {"address": "Jl. Raya Tanjung Barat, Tanjung Barat, Jagakarsa, Jakarta Selatan, 12530", "elevation": "+44 m"},
            "Lenteng Agung": {"address": "Jl. Lenteng Agung Timur, Lenteng Agung, Jagakarsa, Jakarta Selatan, 12610", "elevation": "+55 m"},
            "Universitas Pancasila": {"address": "Jl. Lenteng Agung, Srengseng Sawah, Jagakarsa, Jakarta Selatan, 12640", "elevation": "+57 m"},
            "Universitas Indonesia": {"address": "Jl. Margonda Raya, Pondok Cina, Beji, Depok, Jawa Barat, 16424", "elevation": "+70 m"},
            "Pondok Cina": {"address": "Jl. Margonda Raya, Pondok Cina, Beji, Depok, Jawa Barat, 16424", "elevation": "+78 m"},
            "Depok Baru": {"address": "Jl. Stasiun Depok Baru, Depok, Pancoran Mas, Depok, Jawa Barat, 16431", "elevation": "+93 m"},
            "Depok": {"address": "Jl. Stasiun Depok, Depok, Pancoran Mas, Depok, Jawa Barat, 16436", "elevation": "+93 m"},
            "Citayam": {"address": "Jl. Raya Citayam, Bojong Pondok Terong, Cipayung, Depok, Jawa Barat, 16444", "elevation": "+121 m"},
            "Bojong Gede": {"address": "Jl. Raya Bojong Gede, Bojong Gede, Kabupaten Bogor, Jawa Barat, 16922", "elevation": "+140 m"},
            "Cilebut": {"address": "Jl. Raya Cilebut, Cilebut Timur, Sukaraja, Kabupaten Bogor, Jawa Barat, 16710", "elevation": "+171 m"},
            "Bogor": {"address": "Jl. Nyi Raja Permas No. 1, Cibogor, Bogor Tengah, Bogor, Jawa Barat, 16124", "elevation": "+246 m"},
            "Nambo": {"address": "Jl. Raya Nambo, Bantar Jati, Klapanunggal, Kabupaten Bogor, Jawa Barat, 16710", "elevation": "+103 m"},
            "Cibinong": {"address": "Jl. Pabuaran, Cibinong, Kabupaten Bogor, Jawa Barat, 16916", "elevation": "+126 m"},
            "Pondok Rajeg": {"address": "Jl. Raya Pondok Rajeg, Jatimulya, Cilodong, Depok, Jawa Barat, 16413", "elevation": "+120 m"},
            "Tanah Abang": {"address": "Jl. Jati Baru Raya, Kp. Bali, Tanah Abang, Jakarta Pusat, 10250", "elevation": "+9 m"},
            "Palmerah": {"address": "Jl. Tentara Pelajar, Gelora, Tanah Abang, Jakarta Pusat, 10270", "elevation": "+10 m"},
            "Kebayoran": {"address": "Jl. Masjid Al-Huda, Kebayoran Lama Utara, Kebayoran Lama, Jakarta Selatan, 12240", "elevation": "+22 m"},
            "Pondok Ranji": {"address": "Jl. WR Supratman, Rengas, Ciputat Timur, Tangerang Selatan, Banten, 15412", "elevation": "+24 m"},
            "Jurangmangu": {"address": "Jl. Cenderawasih, Sawah Lama, Ciputat, Tangerang Selatan, Banten, 15413", "elevation": "+24 m"},
            "Sudimara": {"address": "Jl. Jombang Raya, Jombang, Ciputat, Tangerang Selatan, Banten, 15414", "elevation": "+26 m"},
            "Rawa Buntu": {"address": "Jl. Raya Rawa Buntu, Rawa Buntu, Serpong, Tangerang Selatan, Banten, 15318", "elevation": "+40 m"},
            "Serpong": {"address": "Jl. Stasiun Serpong, Serpong, Tangerang Selatan, Banten, 15311", "elevation": "+46 m"},
            "Cisauk": {"address": "Jl. Raya Cisauk, Cisauk, Tangerang, Banten, 15341", "elevation": "+48 m"},
            "Cicayur": {"address": "Jl. Raya Cisauk-Legok, Cicayur, Cisauk, Tangerang, Banten, 15343", "elevation": "+48 m"},
            "Parung Panjang": {"address": "Jl. Ki Hajar Dewantara, Parungpanjang, Kabupaten Bogor, Jawa Barat, 16360", "elevation": "+53 m"},
            "Cilejit": {"address": "Jl. Raya Cilejit, Batok, Tenjo, Kabupaten Bogor, Jawa Barat, 16370", "elevation": "+52 m"},
            "Daru": {"address": "Jl. Sarwani, Daru, Jambe, Tangerang, Banten, 15720", "elevation": "+52 m"},
            "Tenjo": {"address": "Jl. Raya Tenjo, Tenjo, Kabupaten Bogor, Jawa Barat, 16370", "elevation": "+50 m"},
            "Tigaraksa": {"address": "Jl. Aria Jaya Santika, Cikasungka, Solear, Tangerang, Banten, 15730", "elevation": "+47 m"},
            "Cikoya": {"address": "Jl. Raya Cikuya, Cikasungka, Solear, Tangerang, Banten, 15730", "elevation": "+39 m"},
            "Maja": {"address": "Jl. Stasiun Maja, Maja, Lebak, Banten, 42381", "elevation": "+33 m"},
            "Rangkasbitung": {"address": "Jl. Stasiun Rangkasbitung, Muara Ciujung Timur, Rangkasbitung, Lebak, Banten, 42312", "elevation": "+22 m"},
            "Duri": {"address": "Jl. Kali Anyar X, Kali Anyar, Tambora, Jakarta Barat, 11310", "elevation": "+7 m"},
            "Grogol": {"address": "Jl. Prof. Dr. Latumeten, Jelambar, Grogol Petamburan, Jakarta Barat, 11460", "elevation": "+7 m"},
            "Pesing": {"address": "Jl. Daan Mogot, Wijaya Kusuma, Grogol Petamburan, Jakarta Barat, 11460", "elevation": "+6 m"},
            "Taman Kota": {"address": "Jl. Taman Kota, Kembangan Utara, Kembangan, Jakarta Barat, 11610", "elevation": "+10 m"},
            "Bojong Indah": {"address": "Jl. Bojong Indah, Rawa Buaya, Cengkareng, Jakarta Barat, 11740", "elevation": "+8 m"},
            "Rawa Buaya": {"address": "Jl. Stasiun Rawa Buaya, Duri Kosambi, Cengkareng, Jakarta Barat, 11750", "elevation": "+6 m"},
            "Kalideres": {"address": "Jl. Semanan Raya, Semanan, Kalideres, Jakarta Barat, 11850", "elevation": "+8 m"},
            "Poris": {"address": "Jl. Maulana Hasanudin, Poris Gaga, Batuceper, Tangerang, Banten, 15122", "elevation": "+10 m"},
            "Batu Ceper": {"address": "Jl. Stasiun Batutulis, Poris Plawad, Cipondoh, Tangerang, Banten, 15141", "elevation": "+12 m"},
            "Tanah Tinggi": {"address": "Jl. Daan Mogot, Tanah Tinggi, Tangerang, Banten, 15119", "elevation": "+13 m"},
            "Tangerang": {"address": "Jl. Ki Asnawi, Sukarasa, Tangerang, Banten, 15111", "elevation": "+14 m"},
            "Kampung Bandan": {"address": "Jl. Mangga Dua Raya, Ancol, Pademangan, Jakarta Utara, 14430", "elevation": "+2 m"},
            "Angke": {"address": "Jl. Stasiun Angke, Jembatan Lima, Tambora, Jakarta Barat, 11250", "elevation": "+3 m"},
            "Sudirman": {"address": "Jl. Jend. Sudirman, Menteng, Jakarta Pusat, 10220", "elevation": "+7 m"},
            "Karet": {"address": "Jl. K.H. Mas Mansyur, Kebon Melati, Tanah Abang, Jakarta Pusat, 10230", "elevation": "+9 m"},
            "BNI City": {"address": "Jl. Jend. Sudirman Kav. 1, Karet Tengsin, Tanah Abang, Jakarta Pusat, 10220", "elevation": "+9 m"},
            "Cikarang": {"address": "Jl. Yos Sudarso, Karangasih, Cikarang Utara, Bekasi, Jawa Barat, 17530", "elevation": "+18 m"},
            "Metland Telagamurni": {"address": "Jl. Telaga Murni Raya, Telagamurni, Cikarang Barat, Bekasi, Jawa Barat, 17530", "elevation": "+19 m"},
            "Cibitung": {"address": "Jl. Bosih Raya, Wanasari, Cibitung, Bekasi, Jawa Barat, 17520", "elevation": "+19 m"},
            "Tambun": {"address": "Jl. Stasiun Tambun, Mekarsari, Tambun Selatan, Bekasi, Jawa Barat, 17510", "elevation": "+19 m"},
            "Bekasi Timur": {"address": "Jl. Ir. H. Juanda, Duren Jaya, Bekasi Timur, Bekasi, Jawa Barat, 17111", "elevation": "+19 m"},
            "Bekasi": {"address": "Jl. Ir. H. Juanda, Marga Mulya, Bekasi Utara, Bekasi, Jawa Barat, 17142", "elevation": "+19 m"},
            "Kranji": {"address": "Jl. I Gusti Ngurah Rai, Kranji, Bekasi Barat, Bekasi, Jawa Barat, 17135", "elevation": "+18 m"},
            "Cakung": {"address": "Jl. Stasiun Cakung, Pulogebang, Cakung, Jakarta Timur, 13950", "elevation": "+18 m"},
            "Klender Baru": {"address": "Jl. I Gusti Ngurah Rai, Penggilingan, Cakung, Jakarta Timur, 13940", "elevation": "+14 m"},
            "Buaran": {"address": "Jl. I Gusti Ngurah Rai, Jatinegara, Cakung, Jakarta Timur, 13930", "elevation": "+11 m"},
            "Klender": {"address": "Jl. I Gusti Ngurah Rai, Jatinegara, Cakung, Jakarta Timur, 13930", "elevation": "+11 m"},
            "Jatinegara": {"address": "Jl. Raya Bekasi Barat, Pisangan Baru, Matraman, Jakarta Timur, 13110", "elevation": "+16 m"},
            "Pondok Jati": {"address": "Jl. Kayu Manis Timur, Palmeriam, Matraman, Jakarta Timur, 13140", "elevation": "+15 m"},
            "Kramat": {"address": "Jl. Kramat Raya, Kramat, Senen, Jakarta Pusat, 10450", "elevation": "+12 m"},
            "Gang Sentiong": {"address": "Jl. Kramat Pulo Dalam II, Kramat, Senen, Jakarta Pusat, 10450", "elevation": "+10 m"},
            "Pasar Senen": {"address": "Jl. Pasar Senen, Senen, Jakarta Pusat, 10410", "elevation": "+8 m"},
            "Kemayoran": {"address": "Jl. Garuda, Gn. Sahari Sel., Kemayoran, Jakarta Pusat, 10610", "elevation": "+6 m"},
            "Rajawali": {"address": "Jl. Industri 1, Gn. Sahari Utara, Sawah Besar, Jakarta Pusat, 10720", "elevation": "+5 m"},
            "Ancol": {"address": "Jl. R. E. Martadinata, Ancol, Pademangan, Jakarta Utara, 14430", "elevation": "+3 m"},
            "Tanjung Priok": {"address": "Jl. Stasiun Tanjung Priok, Tanjung Priok, Jakarta Utara, 14310", "elevation": "+4 m"},

        }

        self._setup_widgets()
        self.region_cb.set(Region.JABODETABEK.value)
        self._on_region_selected()

    def _setup_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        top_frame.columnconfigure(1, weight=1)

        ttk.Label(top_frame, text="Wilayah Operasi:").grid(
            row=0, column=0, padx=(5, 2), pady=5, sticky="w")
        self.region_cb = ttk.Combobox(
            top_frame,
            textvariable=self.selected_region,
            values=list(self.regions.keys()),
            state="readonly",
            width=30
        )
        self.region_cb.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="ew")
        self.region_cb.bind("<<ComboboxSelected>>", self._on_region_selected)

        # --- TOMBOL BARU UNTUK MELIHAT PETA ---
        map_button = ttk.Button(
            top_frame, text="Lihat Peta Rute", command=self._show_map_clicked)
        map_button.grid(row=0, column=2, padx=(10, 5), pady=5, sticky="e")
        # ------------------------------------

        # Tombol Cari
        search_button = ttk.Button(main_frame, text="Cari Rute Terbaik",
                                   command=self._find_route_clicked, style="Accent.TButton")
        search_button.pack(pady=10, fill=tk.X, padx=5)

        # --- FRAME INPUT PENCARIAN ---
        input_frame = ttk.LabelFrame(main_frame, text="Pencarian Rute")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        input_frame.columnconfigure(1, weight=1)

        # Stasiun Awal
        ttk.Label(input_frame, text="Dari Stasiun:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.from_station_cb = ttk.Combobox(input_frame, state="readonly")
        self.from_station_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Stasiun Tujuan
        ttk.Label(input_frame, text="Ke Stasiun:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.to_station_cb = ttk.Combobox(input_frame, state="readonly")
        self.to_station_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # --- WIDGET TANGGAL DAN WAKTU ---
        ttk.Label(input_frame, text="Tanggal Berangkat:").grid(
            row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Jam Berangkat:").grid(
            row=3, column=0, padx=5, pady=5, sticky="w")
        self.time_entry = ttk.Entry(input_frame)
        self.time_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Frame Hasil
        result_frame = ttk.LabelFrame(main_frame, text="Hasil Rute")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.result_text = tk.Text(
            result_frame, wrap=tk.WORD, height=15, state=tk.DISABLED, font=("Arial", 10), fg="#000")
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # --- FUNGSI BARU UNTUK MENANGANI KLIK TOMBOL PETA ---
    def _show_map_clicked(self):
        """Menangani klik pada tombol lihat peta."""
        # Nama file peta sudah ditentukan dalam proyek
        map_file = "Rute-KRL-1.png"
        self.app_logic.show_map_image(map_file)
    # ----------------------------------------------------

    def _on_region_selected(self, event=None):
        """Memperbarui dropdown stasiun saat wilayah baru dipilih."""
        region_enum = self.regions[self.selected_region.get()]
        stations = self.app_logic.schedule.get_available_stations_by_region(region_enum)
        self.from_station_cb['values'] = stations
        self.to_station_cb['values'] = stations
        self.from_station_cb.set('')
        self.to_station_cb.set('')
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Silakan pilih stasiun keberangkatan dan tujuan.")
        self.result_text.config(state=tk.DISABLED)

    def _find_route_clicked(self):
        from_station = self.from_station_cb.get()
        to_station = self.to_station_cb.get()
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()

        if not from_station or not to_station or not date_str or not time_str:
            messagebox.showwarning(
                "Input Tidak Lengkap", "Harap isi semua kolom: stasiun, tanggal, dan waktu.")
            return

        try:
            departure_datetime = datetime.datetime.strptime(
                f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
            )
            region_enum = self.regions[self.selected_region.get()]
            routes = self.app_logic.find_routes(
                from_station, to_station, departure_datetime, region_enum
            )
            self._display_results(routes)

        except ValueError:
            messagebox.showerror(
                "Format Salah", "Format tanggal (YYYY-MM-DD) atau waktu (HH:MM) tidak valid.")
        except Exception as e:
            messagebox.showerror("Error Tak Terduga",
                                 f"Terjadi kesalahan: {e}")

    def _display_results(self, routes: List[List[Dict[str, Any]]]):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        if not routes:
            self.result_text.insert(tk.END, "Tidak ada rute langsung yang ditemukan untuk waktu yang dipilih.\nCoba cari pada waktu yang berbeda.")
        else:
            header = f"Menampilkan {len(routes)} rute terbaik dari {routes[0][0]['start_station']} ke {routes[0][-1]['destination_station']}:\n"
            self.result_text.insert(tk.END, header)

            for i, route in enumerate(routes):
                line = f"\n--- Rute Alternatif #{i+1} ---\n"
                dep_time = route[0]['departure_time']
                arr_time = route[-1]['estimated_arrival']

                total_duration = route[-1]['_arrival_dt'] - route[0]['_departure_dt']
                hours, remainder = divmod(total_duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                line += f"Perkiraan: Berangkat {dep_time}, Tiba {arr_time} (Durasi: {hours} jam {minutes} menit)\n"

                transits = len(set(leg['train_id'] for leg in route)) - 1
                line += f"Jumlah Transit: {transits}\n"

                # --- Hitung tarif hanya sekali untuk seluruh rute ---
                fare = None
                if hasattr(self.app_logic, "schedule") and hasattr(self.app_logic.schedule, "get_fare_for_train"):
                    # Coba dapatkan train_obj dari leg pertama
                    train_obj = getattr(route[0], "train_obj", None)
                    if train_obj is None and hasattr(self.app_logic.schedule, "station_to_trains_map"):
                        trains = self.app_logic.schedule.station_to_trains_map.get(route[0]['start_station'], [])
                        for t in trains:
                            if t.id == route[0]['train_id']:
                                train_obj = t
                                break
                    if train_obj:
                        # Panggil tanpa from_station/to_station
                        fare = self.app_logic.schedule.get_fare_for_train(train_obj)
                    else:
                        # fallback: hitung manual jika info train_obj tidak ada
                        from train_schedule import calculate_fare
                        region = route[0].get('region', None)
                        # Buat list stasiun dari awal ke akhir
                        route_list = [leg['start_station'] for leg in route] + [route[-1]['destination_station']]
                        if route_list and region:
                            fare = calculate_fare(route_list, region)
                if fare is not None:
                    line += f"Tarif: Rp{fare:,}\n"
                # ---------------------------------------------------

                self.result_text.insert(tk.END, line + "\n")

                for leg in route:
                    details = f"  • Naik KA {leg['train_name']} ({leg['train_id']})\n"
                    details += f"    - Dari: {leg['start_station']} ({leg['departure_time']})\n"
                    details += f"    - Ke: {leg['destination_station']} ({leg['estimated_arrival']})\n"
                    occupancy = leg.get('occupancy_percentage', -1)
                    occupancy_str = f"{occupancy}%" if occupancy != -1 else "N/A"
                    details += f"    - Perkiraan Okupansi: {occupancy_str}\n"
                    # --- Hapus tarif per leg ---
                    # ...hapus blok tarif per leg di sini...
                    # ---------------------------
                    self.result_text.insert(tk.END, details)

        self.result_text.config(state=tk.DISABLED)

