import java.awt.*;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;

/**
 * KELAS BARU: TrainScheduleGUI
 * Kelas ini mengelola semua komponen UI Swing
 */

public class TrainScheduleGUI extends JFrame {
    private final TrainSchedulePredictorApp app;
    private final JComboBox<String> startStationBox;
    private final JComboBox<String> destStationBox;
    private final JTable resultTable;
    private final DefaultTableModel tableModel;

    public TrainScheduleGUI(TrainSchedulePredictorApp app) {
        this.app = app;
        setTitle("Pencarian Rute KRL Jabodetabek");
        setSize(900, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // --- Panel Input ---
        JPanel inputPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 10, 10));
        List<String> stations = app.getAvailableStations();
        startStationBox = new JComboBox<>(stations.toArray(new String[0]));
        destStationBox = new JComboBox<>(stations.toArray(new String[0]));

        // --- MULAI PERUBAHAN ---

        // 1. Buat data alamat stasiun
        Map<String, String> stationAddresses = new HashMap<>();
        stationAddresses.put("Tanah Abang", "Jl. Jatibaru Raya, Kp. Bali, Tanah Abang, Jakarta Pusat, 10250");
        stationAddresses.put("Manggarai", "Jl. Manggarai Utara, Manggarai, Tebet, Jakarta Selatan, 12850");
        stationAddresses.put("Depok", "Jl. Stasiun, Depok, Pancoran Mas, Kota Depok, 16431");
        // (Tambahkan stasiun dan alamat lainnya sesuai kebutuhan)

        // 2. Buat instance renderer kustom
        StationRenderer renderer = new StationRenderer(stationAddresses);

        // 3. Terapkan renderer ke kedua JComboBox
        startStationBox.setRenderer(renderer);
        destStationBox.setRenderer(renderer);

        // --- SELESAI PERUBAHAN ---

        JButton searchButton = new JButton("Cari Rute");
        searchButton.setToolTipText("Klik untuk mencari rute kereta berdasarkan stasiun yang dipilih.");
        JButton mapButton = new JButton("Lihat Peta");
        mapButton.setToolTipText("Klik untuk menampilkan peta rute KRL Jabodetabek.");

        inputPanel.add(new JLabel("Stasiun Awal:"));
        inputPanel.add(startStationBox);
        inputPanel.add(new JLabel("Stasiun Tujuan:"));
        inputPanel.add(destStationBox);
        inputPanel.add(searchButton);
        inputPanel.add(mapButton);

        // --- Tabel Hasil ---
        String[] columnNames = { "Nama Kereta", "Berangkat", "Tiba", "Okupansi" };
        tableModel = new DefaultTableModel(columnNames, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false; // Membuat sel tidak dapat diedit
            }
        };
        resultTable = new JTable(tableModel);
        resultTable.setFillsViewportHeight(true);
        resultTable.setRowHeight(25);
        resultTable.getTableHeader().setFont(new Font("SansSerif", Font.BOLD, 14));

        // ** SET RENDERER KUSTOM UNTUK PEWARNAAN **
        resultTable.setDefaultRenderer(Object.class, new TrainRouteRenderer());

        JScrollPane scrollPane = new JScrollPane(resultTable);

        // --- Layout Utama ---
        Container contentPane = getContentPane();
        contentPane.setLayout(new BorderLayout(0, 10));
        contentPane.add(inputPanel, BorderLayout.NORTH);
        contentPane.add(scrollPane, BorderLayout.CENTER);

        // --- Action Listeners ---
        searchButton.addActionListener(e -> findAndDisplayRoutes());
        mapButton.addActionListener(e -> TrainSchedulePredictorApp.showMapImage("Rute-KRL-1.png"));
    }

    public void findAndDisplayRoutes() {
        // Gunakan OccupancyPredictor.normalizeStation untuk normalisasi nama stasiun
        String startStation = OccupancyPredictor.normalizeStation((String) startStationBox.getSelectedItem());
        String destStation = OccupancyPredictor.normalizeStation((String) destStationBox.getSelectedItem());

        if (startStation.equals(destStation)) {
            JOptionPane.showMessageDialog(this, "Stasiun awal dan tujuan tidak boleh sama.", "Input Error",
                    JOptionPane.ERROR_MESSAGE);
            return;
        }

        // Hapus hasil sebelumnya
        tableModel.setRowCount(0);

        // Tambahkan waktu persiapan minimal, misalnya 15 menit
        final int PREPARATION_TIME_MINUTES = 15;
        LocalDateTime searchStartTime = LocalDateTime.now().plusMinutes(PREPARATION_TIME_MINUTES);

        // Gunakan searchStartTime untuk memulai pencarian
        List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit(startStation, destStation,
                searchStartTime,
                3);

        if (routes.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Maaf, tidak ditemukan rute untuk pilihan Anda.", "Tidak Ada Rute",
                    JOptionPane.INFORMATION_MESSAGE);
        } else {
            for (List<Map<String, Object>> route : routes) {
                // Proses setiap segmen perjalanan (leg) dalam satu rute
                int i = 0;
                while (i < route.size()) {
                    Map<String, Object> leg = route.get(i);
                    String trainName = (String) leg.get("train_name");
                    String startStationFromTransit = (String) leg.get("start_station");
                    String departureTime = (String) leg.get("departure_time");
                    String occupancyInfo = leg.get("occupancy_percentage") != null
                            ? leg.get("occupancy_percentage") + "%"
                            : "N/A";

                    // Gabungkan segmen yang menggunakan kereta yang sama
                    int j = i;
                    while (j + 1 < route.size() && route.get(j + 1).get("train_name").equals(trainName)) {
                        j++;
                    }
                    String endStation = (String) route.get(j).get("destination_station");
                    String arrivalTime = (String) route.get(j).get("estimated_arrival");

                    String fullTrainName = trainName + " (" + startStationFromTransit + " - " + endStation + ")";

                    tableModel.addRow(new Object[] { fullTrainName, departureTime, arrivalTime, occupancyInfo });

                    // Jika ada transit, tambahkan baris penanda
                    if (j + 1 < route.size()) {
                        tableModel.addRow(new Object[] { "--- TRANSIT ---", "", "", "" });
                    }

                    i = j + 1;
                }
                // Tambahkan pemisah antar rute jika ada lebih dari satu rute ditemukan
                if (routes.size() > 1 && routes.indexOf(route) < routes.size() - 1) {
                    tableModel.addRow(new Object[] { "", "", "", "" });
                    tableModel.addRow(new Object[] { "=== RUTE ALTERNATIF ===", "", "", "" });
                    tableModel.addRow(new Object[] { "", "", "", "" });
                }
            }
        }
    }
}