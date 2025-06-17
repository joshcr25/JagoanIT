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
        stationAddresses.put("Ancol",
                "Jalan R.E. Martadinata, Pademangan Barat, Pademangan, Jakarta Utara, DKI Jakarta,14420, Indonesia (Ketinggian: 3 mdpl)");
        stationAddresses.put("Angke", "Jalan Stasiun Angke, \r\n" + //
                "Angke, Tambora, Jakarta Barat, DKI Jakarta, 11330, \r\n" + //
                "Indonesia (Ketinggian: 3 mdpl)");
        stationAddresses.put("BNI City",
                "Jalan Tanjung Karang No. 1, Kebon Melati, Tanah Abang, Jakarta Pusat, DKI Jakarta 10230, Indonesia (Ketinggian: 6 mdpl)");
        stationAddresses.put("Batu Ceper", "Jalan K.H. Agus Salim (pintu utara khusus kereta api bandara), \r\n" + //
                "Jalan Benteng Betawi (pintu selatan khusus kereta api komuter), \r\n" + //
                "Poris Plawad, Cipondoh, Tangerang, Banten 15141, \r\n" + //
                "Indonesia (Ketinggian: 11 mdpl)");
        stationAddresses.put("Bekasi", "Jalan Ir. H. Juanda (pintu selatan), \r\n" + //
                "Jalan Perjuangan (pintu utara), \r\n" + //
                "Marga Mulya, Bekasi Utara, Kota Bekasi, Jawa Barat 17126, \r\n" + //
                "Indonesia (Ketinggian: 19 mdpl)");
        stationAddresses.put("Bekasi Timur",
                "Jalan Ir. H. Juanda, Duren Jaya, Bekasi Timur, Kota Bekasi, Jawa Barat 17111, Indonesia (Ketinggian: 19 mdpl)");
        stationAddresses.put("Bogor", "Jl. Nyi Raja Permas (pintu timur), \r\n" + //
                "Jl. Mayor Oking (pintu barat), \r\n" + //
                "Cibogor, Bogor Tengah, Kota Bogor, Jawa Barat 16124, \r\n" + //
                "Indonesia (Ketinggian: 246 mdpl)");
        stationAddresses.put("Bojong Gede",
                "Jalan Raya Bojonggede, Bojonggede, Bojonggede, Kabupaten Bogor, Jawa Barat 16922, Indonesia (Ketinggian: 140 mdpl)");
        stationAddresses.put("Bojong Indah", "Jalan Bojong Indah, \r\n" + //
                "Rawa Buaya, Cengkareng, Jakarta Barat, 11740, \r\n" + //
                "Indonesia (Ketinggian: 6 mdpl)");
        stationAddresses.put("Buaran",
                "Jalan I Gusti Ngurah Rai, Jatinegara, Cakung, Jakarta Timur, 13930, Indonesia (Ketinggian: 11 mdpl)");
        stationAddresses.put("Cakung", "Jalan Stasiun Cakung, \r\n" + //
                "Bintara, Bekasi Barat, Bekasi, 17134, Indonesia (Ketinggian: 18 mdpl)");
        stationAddresses.put("Cawang",
                "Jalan Tebet Timur Dalam 11 Tebet Timur, Tebet, Jakarta Selatan, 12820, Indonesia (Ketinggian: 13 mdpl)");
        stationAddresses.put("Cibinong",
                "Jalan Kampung Kebon Kopi / Jalan Padurenan Pabuaran, Cibinong, Kabupaten Bogor, Jawa Barat 16916, Indonesia (Ketinggian: 155 mdpl)");
        stationAddresses.put("Cibitung", "Jalan Bosih Raya, \r\n" + //
                "Wanasari, Cibitung, Kabupaten Bekasi, Jawa Barat 17521, \r\n" + //
                "Indonesia (Ketinggian: 19 mdpl)");
        stationAddresses.put("Cicayur",
                "Cisauk, Cisauk, Kabupaten Tangerang, Banten 15841, Indonesia (Ketinggian: 47 mdpl)");
        stationAddresses.put("Cikarang",
                "Jalan Yos Sudarso, Karangasih, Cikarang Utara, Kabupaten Bekasi, Jawa Barat 17839, Indonesia (Ketinggian: 18 mdpl)");
        stationAddresses.put("Cikini",
                "Jalan Cikini Raya, Cikini, Menteng, Jakarta Pusat, 10330, Indonesia (Ketinggian: 20 mdpl)");
        stationAddresses.put("Cikoya",
                "Jalan Raya Cikuya, Cikasungka, Solear, Kabupaten Tangerang, Banten 15744, Indonesia (Ketinggian: 53 mdpl)");
        stationAddresses.put("Cilebut",
                "Jalan Raya Cilebut, Cilebut Timur, Sukaraja, Kabupaten Bogor, Jawa Barat 16718, Indonesia (Ketinggian: 171 mdpl)");
        stationAddresses.put("Cilejit",
                "Batok, Tenjo, Kabupaten Bogor, Jawa Barat 16377, Indonesia (Ketinggian: 53 mdpl)");
        stationAddresses.put("Cisauk",
                "Jalan Stasiun Cisauk, Cibogo, Cisauk, Kabupaten Tangerang, Banten 15844, Indonesia (Ketinggian: 48 mdpl)");
        stationAddresses.put("Citayam",
                "Jalan Raya Citayam, Bojong Pondok Terong, Cipayung, Kota Depok, Jawa Barat 16444 (Ketinggian: 120 mdpl)");
        stationAddresses.put("Citeras",
                "Mekarsari, Rangkasbitung, Kabupaten Lebak, Banten, Indonesia (Ketinggian: 48 mdpl)");
        stationAddresses.put("Daru",
                "Jalan Sarwani, Daru, Jambe, Kabupaten Tangerang, Banten 15923, Indonesia (Ketinggian: 50 mdpl)");
        stationAddresses.put("Depok", "Jalan Stasiun, Depok, Pancoran Mas, Kota Depok, 16431 (Ketinggian: 93 mdpl)");
        stationAddresses.put("Depok Baru",
                "Jalan Stasiun Depok, Pancoran Mas, Pancoran Mas, Kota Depok, Jawa Barat 16436, Indonesia (Ketinggian: 93 mdpl)");
        stationAddresses.put("Duren Kalibata",
                "Jalan Pengadegan Timur, Rawa Jati, Pancoran, Jakarta Selatan, 12750, Indonesia (Ketinggian: 26 mdpl)");
        stationAddresses.put("Duri",
                "Jalan Duri Utara, Duri Utara, Tambora, Jakarta Barat, 11270, Indonesia (Ketinggian: 9 mdpl)");
        stationAddresses.put("Gang Sentiong",
                "Jalan Kramat Dalam 1, Kramat, Senen, Jakarta Pusat, 10450, Indonesia (Ketinggian: 7 mdpl)");
        stationAddresses.put("Gondangdia",
                "Jalan Srikaya No. 1, Kebon Sirih, Menteng, Jakarta Pusat, 10340, Indonesia (Ketinggian: 17 mdpl)");
        stationAddresses.put("Grogol",
                "Jalan Prof Dr. Latumeten, Jelambar, Grogol Petamburan, Jakarta Barat, 11460, Indonesia (Ketinggian: 4 mdpl)");

        stationAddresses.put("Jakarta Kota",
                "Jalan Stasiun Kota No. 1, Pinangsia, Taman Sari, Jakarta Barat, 11110, Indonesia (Ketinggian: 4 mdpl)");
        stationAddresses.put("Jatinegara",
                "Jalan Raya Bekasi Barat, Pisangan Baru, Matraman, Jakarta Timur, 13110, Indonesia (Ketinggian: 16 mdpl)");
        stationAddresses.put("Jayakarta",
                "Jalan Pangeran Jayakarta no. 28, Mangga Dua Selatan, Sawah Besar, Jakarta Pusat, 10730, Indonesia (Ketinggian: 13 mdpl)");
        stationAddresses.put("Juanda",
                "Jalan Ir. H. Juanda No. 1, Pasar Baru, Sawah Besar, Jakarta Pusat, 10710, Indonesia (Ketinggian: 15 mdpl)");
        stationAddresses.put("Jurang Mangu",
                "Jalan Cenderawasih Sawah, Ciputat, Kota Tangerang Selatan, Banten 15413, Indonesia (Ketinggian: 25 mdpl)");
        stationAddresses.put("Kali Deres",
                "Jalan Semanan Raya, Semanan, Kalideres, Jakarta Barat, 11850, Indonesia (Ketinggian: 7 mdpl)");
        stationAddresses.put("Kampung Bandan",
                "Jalan Gunung Sahari, Ancol, Pademangan, Jakarta Utara, 14430, Indonesia (Ketinggian: 3 mdpl (sisi bawah), 5 mdpl (sisi atas))");
        stationAddresses.put("Karet",
                "Jalan K.H. Mas Mansyur, Kebon Melati, Tanah Abang, Jakarta Pusat, 10230, Indonesia (Ketinggian: 11 mdpl)");
        stationAddresses.put("Kebayoran",
                "Jalan Masjid Al-Huda Nomor 12, Kebayoran Lama Utara, Kebayoran Lama, Jakarta Selatan, DKI Jakarta 12240, Indonesia (Ketinggian: 4,2 mdpl)");
        stationAddresses.put("Kemayoran",
                "Jalan Garuda Gunung Sahari Selatan, Kemayoran, Jakarta Pusat, 10610, Indonesia (Ketinggian: 4 mdpl)");
        stationAddresses.put("Klender",
                "Jalan Haji Darip Raya, Jatinegara Kaum, Pulo Gadung, Jakarta Timur, 13250, Indonesia (Ketinggian: 10 mdpl)");
        stationAddresses.put("Klender Baru",
                "Jalan I Gusti Ngurah Rai, Pondok Kopi, Duren Sawit, Jakarta Timur, 13460, Indonesia (Ketinggian: 11 mdpl)");
        stationAddresses.put("Kramat",
                "Jalan Percetakan Negara III, Paseban, Senen, Jakarta Pusat, 10440, Indonesia (Ketinggian: 10 mdpl)");
        stationAddresses.put("Kranji",
                "Jalan I Gusti Ngurah Rai, Kranji, Bekasi Barat, Kota Bekasi, Jawa Barat 17135, Indonesia (Ketinggian: 18 mdpl)");
        stationAddresses.put("Lenteng Agung", "Jl. Raya Lenteng Agung Timur, Lenteng Agung, Jagakarsa, Jakarta Selatan, Indonesia (Ketinggian: +57 mdpl)");
        stationAddresses.put("Maja", "Jl. Maja, Maja, Kabupaten Lebak, Banten, Indonesia (Ketinggian: +40 mdpl)");
        stationAddresses.put("Mangga Besar", "Jl. Karang Anyar, Karang Anyar, Sawah Besar, Jakarta Pusat, Indonesia (Ketinggian: +13 mdpl)");
        stationAddresses.put("Manggarai", "Jl. Manggarai Utara 1, Manggarai, Tebet, Jakarta Selatan, Indonesia (Ketinggian: +13 mdpl)");
        stationAddresses.put("Matraman", "Jalan Matraman Raya, Kebon Manggis, Matraman, Jakarta Timur, Indonesia (Ketinggian: +26 mdpl)");
        stationAddresses.put("Metland Telaga Murni", "Kompleks Metland Cibitung, Telagamurni, Cikarang Barat, Kabupaten Bekasi, Jawa Barat, Indonesia (Ketinggian: +18 mdpl)");
        stationAddresses.put("Nambo", "Bantar Jati, Klapanunggal, Kabupaten Bogor, Jawa Barat, Indonesia (Ketinggian: +135 mdpl)");
        stationAddresses.put("Palmerah", "Jl. Tentara Pelajar, Gelora, Tanah Abang, Jakarta Pusat, Indonesia (Ketinggian: +13 mdpl)");
        stationAddresses.put("Parung Panjang", "Jalan Marga Mekar no.54, Parung Panjang, Parung Panjang, Kabupaten Bogor, Jawa Barat, Indonesia (Ketinggian: +54 mdpl)");
        stationAddresses.put("Pasar Minggu", "Jl. Raya Pasar Minggu, Pasar Minggu, Jakarta Selatan, Indonesia (Ketinggian: +44 mdpl)");
        stationAddresses.put("Pasar Minggu Baru", "Jl. Rawajati Timur, Rawajati, Pancoran, Jakarta Selatan, Indonesia (Ketinggian: +36 mdpl)");
        stationAddresses.put("Pasar Senen", "Jl. Stasiun Senen No. 14, Senen, Senen, Jakarta Pusat, Indonesia (Ketinggian: +4.7 mdpl)");
        stationAddresses.put("Pesing", "Jl. Daan Mogot, Wijaya Kusuma, Grogol Petamburan, Jakarta Barat, Indonesia (Ketinggian: +7 mdpl)");
        stationAddresses.put("Pondok Cina", "Jl. Margonda Raya, Pondok Cina, Beji, Depok, Jawa Barat, Indonesia (Ketinggian: +68 mdpl)");
        stationAddresses.put("Pondok Jati", "Jalan Bunga 2, Palmeriam, Matraman, Jakarta Timur, Indonesia (Ketinggian: +14 mdpl)");
        stationAddresses.put("Pondok Rajeg", "Jalan Raya Pondok Rajeg, Jatimulya, Cilodong, Depok, Jawa Barat, Indonesia (Ketinggian: +121 mdpl)");
        stationAddresses.put("Pondok Ranji", "Jalan W.R. Supratman, Rengas, Ciputat Timur, Tangerang Selatan, Banten, Indonesia (Ketinggian: +24 mdpl)");
        stationAddresses.put("Poris", "Jl. Maulana Hasanuddin, Poris Gaga, Batuceper, Tangerang, Banten, Indonesia (Ketinggian: +7 mdpl)");
        stationAddresses.put("Rajawali", "Jalan Industri 1, Gunung Sahari Utara, Sawah Besar, Jakarta Pusat, Indonesia (Ketinggian: +5 mdpl)");
        stationAddresses.put("Rangkasbitung", "Jl. Stasiun Rangkasbitung No.1, Muara Ciujung Timur, Rangkasbitung, Kabupaten Lebak, Banten, Indonesia (Ketinggian: +22 mdpl)");
        stationAddresses.put("Rawa Buaya", "Jl. Stasiun Rawa Buaya, Duri Kosambi, Cengkareng, Jakarta Barat, Indonesia (Ketinggian: +6 mdpl)");
        stationAddresses.put("Rawa Buntu", "Jl. Raya Rawa Buntu, Rawa Buntu, Serpong, Tangerang Selatan, Banten, Indonesia (Ketinggian: +40 mdpl)");
        stationAddresses.put("Sawah Besar", "Jl. Sawah Besar, Kebon Kelapa, Gambir, Jakarta Pusat, Indonesia (Ketinggian: +15 mdpl)");
        stationAddresses.put("Serpong", "Jl. Stasiun Serpong, Serpong, Serpong, Tangerang Selatan, Banten, Indonesia (Ketinggian: +24 mdpl)");
        stationAddresses.put("Sudimara", "Jl. Jombang Raya, Jombang, Ciputat, Tangerang Selatan, Banten, Indonesia (Ketinggian: +25 mdpl)");
        stationAddresses.put("Sudirman", "Jl. Jenderal Sudirman, Dukuh Atas, Setiabudi, Jakarta Selatan, Indonesia (Ketinggian: +20 mdpl)");
        stationAddresses.put("Taman Kota", "Jl. Taman Kota, Kedaung Kali Angke, Cengkareng, Jakarta Barat, Indonesia (Ketinggian: +7 mdpl)");
        stationAddresses.put("Tambun", "Jl. Stasiun Tambun, Mekarsari, Tambun Selatan, Kabupaten Bekasi, Jawa Barat, Indonesia (Ketinggian: +19 mdpl)");
        stationAddresses.put("Tanah Abang", "Jl. Jati Baru Raya, Kampung Bali, Tanah Abang, Jakarta Pusat, Indonesia (Ketinggian: +9 mdpl)");
        stationAddresses.put("Tanah Tinggi", "Jl. Tanah Tinggi, Tanah Tinggi, Johar Baru, Jakarta Pusat, Indonesia (Ketinggian: +7 mdpl)");
        stationAddresses.put("Tangerang", "Jl. Ki Asnawi, Sukarasa, Tangerang, Kota Tangerang, Banten, Indonesia (Ketinggian: +10 mdpl)");
        stationAddresses.put("Tanjung Barat", "Jl. Raya Tanjung Barat, Tanjung Barat, Jagakarsa, Jakarta Selatan, Indonesia (Ketinggian: +44 mdpl)");
        stationAddresses.put("Tanjung Priok", "Jl. Taman Stasiun Tanjung Priok, Tanjung Priok, Tanjung Priok, Jakarta Utara, Indonesia (Ketinggian: +4 mdpl)");
        stationAddresses.put("Tebet", "Jl. Tebet Raya, Tebet Timur, Tebet, Jakarta Selatan, Indonesia (Ketinggian: +26 mdpl)");
        stationAddresses.put("Tenjo", "Jl. Raya Tenjo, Tenjo, Tenjo, Bogor, Jawa Barat, Indonesia (Ketinggian: +52 mdpl)");
        stationAddresses.put("Tigaraksa", "Jl. Raya Tigaraksa, Cikasungka, Solear, Tangerang, Banten, Indonesia (Ketinggian: +54 mdpl)");
        stationAddresses.put("Universitas Indonesia", "Jl. Margonda Raya, Pondok Cina, Beji, Depok, Jawa Barat, Indonesia (Ketinggian: +74 mdpl)");
        stationAddresses.put("Universitas Pancasila", "Jl. Raya Lenteng Agung, Srengseng Sawah, Jagakarsa, Jakarta Selatan, Indonesia (Ketinggian: +55 mdpl)");


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