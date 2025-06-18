import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import List, Dict, Any

from route_finder import RouteFinder
import occupancy_predictor as predictor

class Tooltip:
    """Creates a tooltip for a given widget."""
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
    The main graphical user interface for the Train Schedule application.
    """
    def __init__(self, app_logic: RouteFinder):
        super().__init__()
        self.app_logic = app_logic

        self.title("Pencarian Rute KRL Jabodetabek")
        self.geometry("900x600")

        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self):
        """Configure styles for Treeview row coloring."""
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('SansSerif', 10))
        style.configure("Treeview.Heading", font=('SansSerif', 12, 'bold'))

        # Colors for different train lines
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
        """Create and layout all the GUI widgets."""
        # --- Input Panel ---
        input_panel = ttk.Frame(self, padding="10")
        input_panel.pack(fill=tk.X)

        stations = self.app_logic.get_available_stations()
        
        ttk.Label(input_panel, text="Stasiun Awal:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_station_box = ttk.Combobox(input_panel, values=stations, state="readonly", width=25)
        self.start_station_box.pack(side=tk.LEFT, padx=5)

        ttk.Label(input_panel, text="Stasiun Tujuan:").pack(side=tk.LEFT, padx=(10, 5))
        self.dest_station_box = ttk.Combobox(input_panel, values=stations, state="readonly", width=25)
        self.dest_station_box.pack(side=tk.LEFT, padx=5)

        # In a real-world app, load addresses from a file or database
        # For this example, it's empty. Tooltips would need this data.
        station_addresses = self.get_station_addresses()
        Tooltip(self.start_station_box, "Pilih stasiun keberangkatan")
        Tooltip(self.dest_station_box, "Pilih stasiun tujuan")
        # To add address tooltips, you would need to listen to combobox selection changes
        # and update the tooltip text dynamically.

        search_button = ttk.Button(input_panel, text="Cari Rute", command=self.find_and_display_routes)
        search_button.pack(side=tk.LEFT, padx=10)
        Tooltip(search_button, "Klik untuk mencari rute kereta berdasarkan stasiun yang dipilih.")
        
        map_button = ttk.Button(input_panel, text="Lihat Peta", command=lambda: RouteFinder.show_map_image("Rute-KRL-1.png"))
        map_button.pack(side=tk.LEFT, padx=5)
        Tooltip(map_button, "Klik untuk menampilkan peta rute KRL Jabodetabek.")

        # --- Results Table ---
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

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.result_table.yview)
        self.result_table.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tags for row coloring
        for line_name in self.line_colors:
            self.result_table.tag_configure(line_name, font=('SansSerif', 10))
            if line_name in ["transit", "alternatif"]:
                self.result_table.tag_configure(line_name, font=('SansSerif', 10, 'italic'), foreground='black', background='#DCDCDC')


    def find_and_display_routes(self):
        """Fetches routes from the app logic and displays them in the table."""
        start_station = self.start_station_box.get()
        dest_station = self.dest_station_box.get()

        if not start_station or not dest_station:
            messagebox.showerror("Input Error", "Stasiun awal dan tujuan harus dipilih.")
            return

        if start_station == dest_station:
            messagebox.showerror("Input Error", "Stasiun awal dan tujuan tidak boleh sama.")
            return

        # Clear previous results
        for item in self.result_table.get_children():
            self.result_table.delete(item)
            
        # Search parameters
        prep_time_minutes = 15
        search_start_time = datetime.datetime.now() + datetime.timedelta(minutes=prep_time_minutes)
        
        routes = self.app_logic.bfs_find_routes(start_station, dest_station, search_start_time, 3)

        if not routes:
            messagebox.showinfo("Tidak Ada Rute", "Maaf, tidak ditemukan rute untuk pilihan Anda.")
        else:
            for i, route in enumerate(routes):
                # Process each segment in the route
                leg_idx = 0
                while leg_idx < len(route):
                    leg = route[leg_idx]
                    train_name = leg['train_name']
                    
                    # Consolidate segments with the same train
                    j = leg_idx
                    while j + 1 < len(route) and route[j+1]['train_name'] == train_name:
                        j += 1
                    
                    start_st_from_transit = leg['start_station']
                    end_st = route[j]['destination_station']
                    
                    full_train_name = f"{train_name} ({start_st_from_transit} - {end_st})"
                    departure_time = leg['departure_time']
                    arrival_time = route[j]['estimated_arrival']
                    occupancy = f"{leg['occupancy_percentage']}%" if leg['occupancy_percentage'] else "N/A"
                    
                    # Determine tag for coloring
                    tag = "default"
                    for line_name in self.line_colors:
                        if line_name in train_name.lower():
                            tag = line_name
                            break
                    
                    self.result_table.insert("", tk.END, values=(full_train_name, departure_time, arrival_time, occupancy), tags=(tag,))

                    # Add transit marker if necessary
                    if j + 1 < len(route):
                        self.result_table.insert("", tk.END, values=("--- TRANSIT ---", "", "", ""), tags=("transit",))

                    leg_idx = j + 1
                
                # Add alternative route separator
                if i < len(routes) - 1:
                    self.result_table.insert("", tk.END, values=("", "", "", ""))
                    self.result_table.insert("", tk.END, values=("=== RUTE ALTERNATIF ===", "", "", ""), tags=("alternatif",))
                    self.result_table.insert("", tk.END, values=("", "", "", ""))

    def get_station_addresses(self) -> Dict[str, str]:
        """
        Returns a dictionary of station addresses.
        NOTE: This is hardcoded as in the original Java code. In a real application,
        this data should be loaded from a file or a database.
        """
        return {
            "Ancol": "Jalan R.E. Martadinata, Pademangan Barat, Pademangan, Jakarta Utara, DKI Jakarta,14420, Indonesia (Ketinggian: 3 mdpl)",
            "Angke": "Jalan Stasiun Angke, Angke, Tambora, Jakarta Barat, DKI Jakarta, 11330, Indonesia (Ketinggian: 3 mdpl)",
            "BNI City": "Jalan Tanjung Karang No. 1, Kebon Melati, Tanah Abang, Jakarta Pusat, DKI Jakarta 10230, Indonesia (Ketinggian: 6 mdpl)",
            "Bogor": "Jl. Nyi Raja Permas (pintu timur), Jl. Mayor Oking (pintu barat), Cibogor, Bogor Tengah, Kota Bogor, Jawa Barat 16124, Indonesia (Ketinggian: 246 mdpl)",
            # ... Add all other stations from the original Java file here
        }