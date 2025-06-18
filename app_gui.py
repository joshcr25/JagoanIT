import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import List, Dict, Any

from route_finder import RouteFinder
import occupancy_predictor as predictor

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
                         font=("tahoma", "8", "normal"))
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

        self.title("Pencarian Rute KRL Jabodetabek")
        self.geometry("1000x600") # Sedikit diperlebar untuk widget baru

        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self):
        """Mengonfigurasi gaya untuk pewarnaan baris Treeview."""
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('SansSerif', 10))
        style.configure("Treeview.Heading", font=('SansSerif', 12, 'bold'))

        # Warna untuk berbagai jalur kereta
        self.line_colors = {
            "bogor": ("#E30A16", "white"),
            "cikarang": ("#0084D8", "black"),
            "tanjung priok": ("#DD0067", "black"),
            "rangkasbitung": ("#16812B", "white"),
            "tangerang": ("#623814", "white"),
            "transit": ("#DCDCDC", "black"),
            "alternatif": ("#DCDCDC", "black")
        }
        for line, (bg, fg) in self.line_colors.items():
            style.configure(f"{line.capitalize()}.Treeview", background=bg, foreground=fg)

    def _create_widgets(self):
        """Membuat dan menata semua widget GUI."""
        # --- Panel Input ---
        input_panel = ttk.Frame(self, padding="10")
        input_panel.pack(fill=tk.X)

        stations = self.app_logic.get_available_stations()
        
        ttk.Label(input_panel, text="Stasiun Awal:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_station_box = ttk.Combobox(input_panel, values=stations, state="readonly", width=25)
        self.start_station_box.pack(side=tk.LEFT, padx=5)

        ttk.Label(input_panel, text="Stasiun Tujuan:").pack(side=tk.LEFT, padx=(10, 5))
        self.dest_station_box = ttk.Combobox(input_panel, values=stations, state="readonly", width=25)
        self.dest_station_box.pack(side=tk.LEFT, padx=5)

        search_button = ttk.Button(input_panel, text="Cari Rute", command=self.find_and_display_routes)
        search_button.pack(side=tk.LEFT, padx=10)
        
        map_button = ttk.Button(input_panel, text="Lihat Peta", command=lambda: RouteFinder.show_map_image("Rute-KRL-1.png"))
        map_button.pack(side=tk.LEFT, padx=5)

        # --- WIDGET BARU UNTUK WAKTU TRANSIT ---
        ttk.Label(input_panel, text="Waktu Transit (menit):").pack(side=tk.LEFT, padx=(15, 5))
        self.transit_time_spinbox = ttk.Spinbox(input_panel, from_=5, to=30, increment=1, width=5, justify=tk.CENTER)
        self.transit_time_spinbox.set(20) # Nilai default 20 menit
        self.transit_time_spinbox.pack(side=tk.LEFT)
        Tooltip(self.transit_time_spinbox, "Atur waktu minimal untuk transit antar kereta (dalam menit).")
        # ------------------------------------

        # --- WIDGET BARU UNTUK WAKTU PERSIAPAN ---
        ttk.Label(input_panel, text="Waktu Persiapan (menit):").pack(side=tk.LEFT, padx=(15, 5))
        self.prep_time_spinbox = ttk.Spinbox(input_panel, from_=2, to=20, increment=1, width=5, justify=tk.CENTER)
        self.prep_time_spinbox.set(15) # Nilai default 15 menit
        self.prep_time_spinbox.pack(side=tk.LEFT)
        Tooltip(self.prep_time_spinbox, "Atur waktu persiapan sebelum keberangkatan (dalam menit).")
        # -----------------------------------------

        # --- Tabel Hasil ---
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("train_name", "departs", "arrives", "occupancy")
        self.result_table = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.result_table.heading("train_name", text="Nama Kereta")
        self.result_table.heading("departs", text="Berangkat")
        self.result_table.heading("arrives", text="Tiba")
        self.result_table.heading("occupancy", text="Okupansi")

        self.result_table.column("train_name", width=400)
        self.result_table.column("departs", width=100, anchor=tk.CENTER)
        self.result_table.column("arrives", width=100, anchor=tk.CENTER)
        self.result_table.column("occupancy", width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.result_table.yview)
        self.result_table.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        for line_name in self.line_colors:
            self.result_table.tag_configure(line_name, font=('SansSerif', 10))
            if line_name in ["transit", "alternatif"]:
                self.result_table.tag_configure(line_name, font=('SansSerif', 10, 'italic'), foreground='black', background='#DCDCDC')


    def find_and_display_routes(self):
        """Mengambil rute dari logika aplikasi dan menampilkannya di tabel."""
        start_station = self.start_station_box.get()
        dest_station = self.dest_station_box.get()

        if not start_station or not dest_station:
            messagebox.showerror("Input Error", "Stasiun awal dan tujuan harus dipilih.")
            return

        if start_station == dest_station:
            messagebox.showerror("Input Error", "Stasiun awal dan tujuan tidak boleh sama.")
            return

        # --- AMBIL NILAI WAKTU TRANSIT DARI SPINBOX ---
        try:
            transit_duration = int(self.transit_time_spinbox.get())
        except ValueError:
            messagebox.showerror("Input Error", "Waktu transit harus berupa angka.")
            return
        # -----------------------------------------

        # --- AMBIL NILAI WAKTU PERSIAPAN DARI SPINBOX ---
        try:
            prep_time_minutes = int(self.prep_time_spinbox.get())
        except ValueError:
            messagebox.showerror("Input Error", "Waktu persiapan harus berupa angka.")
            return
        # -----------------------------------------

        for item in self.result_table.get_children():
            self.result_table.delete(item)
            
        search_start_time = datetime.datetime.now() + datetime.timedelta(minutes=prep_time_minutes)
        
        # --- PASSING PARAMETER BARU KE FUNGSI PENCARIAN ---
        routes = self.app_logic.astar_find_routes(start_station, dest_station, search_start_time, 3, transit_duration)
        # ----------------------------------------------------

        if not routes:
            messagebox.showinfo("Tidak Ada Rute", "Maaf, tidak ditemukan rute untuk pilihan Anda.")
        else:
            for i, route in enumerate(routes):
                leg_idx = 0
                while leg_idx < len(route):
                    leg = route[leg_idx]
                    train_name = leg['train_name']
                    
                    j = leg_idx
                    while j + 1 < len(route) and route[j+1]['train_name'] == train_name:
                        j += 1
                    
                    start_st_from_transit = leg['start_station']
                    end_st = route[j]['destination_station']
                    
                    full_train_name = f"{train_name} ({start_st_from_transit} - {end_st})"
                    departure_time = leg['departure_time']
                    arrival_time = route[j]['estimated_arrival']
                    occupancy = f"{leg['occupancy_percentage']}%" if leg['occupancy_percentage'] is not None else "N/A"
                    
                    tag = "default"
                    for line_name in self.line_colors:
                        if line_name in train_name.lower():
                            tag = line_name
                            break
                    
                    self.result_table.insert("", tk.END, values=(full_train_name, departure_time, arrival_time, occupancy), tags=(tag,))

                    if j + 1 < len(route):
                        # Menampilkan waktu tunggu transit
                        arrival_leg_1 = route[j]['_arrival_dt']
                        departure_leg_2 = route[j+1]['_departure_dt']
                        wait_minutes = round((departure_leg_2 - arrival_leg_1).total_seconds() / 60)
                        transit_text = f"--- TRANSIT (Tunggu {wait_minutes} menit di {leg['destination_station']}) ---"
                        self.result_table.insert("", tk.END, values=(transit_text, "", "", ""), tags=("transit",))


                    leg_idx = j + 1
                
                if i < len(routes) - 1:
                    self.result_table.insert("", tk.END, values=("", "", "", ""))
                    self.result_table.insert("", tk.END, values=("=== RUTE ALTERNATIF ===", "", "", ""), tags=("alternatif",))
                    self.result_table.insert("", tk.END, values=("", "", "", ""))

    def get_station_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Mengembalikan data stasiun KRL Commuter Line, termasuk alamat dan ketinggian.
        Sumber data: Wikipedia
        """
        return {
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
