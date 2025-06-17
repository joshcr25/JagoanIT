import java.awt.*;
import java.io.IOException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.List;
import javax.swing.*;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;

// Kelas Train, TrainSchedule, dan OccupancyPredictor tetap sama persis
// Tidak perlu diubah dari kode asli Anda



// Di dalam file Kode_JagoanIT.java, modifikasi kelas TrainSchedule



class TrainSchedulePredictorApp {
    private final TrainSchedule schedule;
    private final int maxResultCount = 3; // Tampilkan hingga 3 rute terbaik

    // --- PERUBAHAN 1: Mendefinisikan Stasiun Transit dan Aturan Lintas Jalur ---
    // Menggunakan enum Line dari kelas OccupancyPredictor
    private static final Map<String, Set<OccupancyPredictor.Line>> INTERCHANGE_STATIONS;

    static {
        INTERCHANGE_STATIONS = new HashMap<>();
        // Normalisasikan nama stasiun agar konsisten (lowercase, no extra space)
        INTERCHANGE_STATIONS.put("manggarai",
                new HashSet<>(Arrays.asList(OccupancyPredictor.Line.BOGOR, OccupancyPredictor.Line.CIKARANG)));
        INTERCHANGE_STATIONS.put("tanah abang",
                new HashSet<>(Arrays.asList(OccupancyPredictor.Line.CIKARANG, OccupancyPredictor.Line.RANGKASBITUNG)));
        INTERCHANGE_STATIONS.put("duri",
                new HashSet<>(Arrays.asList(OccupancyPredictor.Line.CIKARANG, OccupancyPredictor.Line.TANGERANG)));
        INTERCHANGE_STATIONS.put("kampung bandan",
                new HashSet<>(Arrays.asList(OccupancyPredictor.Line.CIKARANG, OccupancyPredictor.Line.TANJUNG_PRIOK)));
        INTERCHANGE_STATIONS.put("jakarta kota",
                new HashSet<>(Arrays.asList(OccupancyPredictor.Line.BOGOR, OccupancyPredictor.Line.TANJUNG_PRIOK)));
        // Tambahkan stasiun transit lain jika diperlukan
    }

    public TrainSchedulePredictorApp() {
        this.schedule = new TrainSchedule();
    }

    public TrainSchedulePredictorApp(TrainSchedule schedule) {
        this.schedule = schedule;
    }

    public static void showMapImage(String imagePath) {
        try {
            ImageIcon icon = new ImageIcon(
                    new ImageIcon(imagePath).getImage().getScaledInstance(800, 600, Image.SCALE_SMOOTH));
            JLabel label = new JLabel(icon);
            JFrame frame = new JFrame("Peta Rute KRL");
            frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            frame.getContentPane().add(label, BorderLayout.CENTER);
            frame.pack();
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Gagal memuat gambar peta: " + imagePath + "\nError: " + e.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    public List<List<Map<String, Object>>> predictRoutesWithTransit(
            String startStation, String destStation, LocalDateTime currentTime, int maxTransit) {
        return bfsFindRoutes(startStation, destStation, currentTime, maxTransit);
    }

    

    // --- PERUBAHAN 2: Algoritma BFS yang sudah dioptimalkan ---
    public List<List<Map<String, Object>>> bfsFindRoutes(
            String startStation, String destStation, LocalDateTime currentTime, int maxTransit) {

        Queue<RouteNode> queue = new LinkedList<>();
        List<List<Map<String, Object>>> results = new ArrayList<>();
        // Visited set sekarang lebih kompleks untuk menangani transit dengan benar
        Set<String> visited = new HashSet<>();

        queue.add(new RouteNode(startStation, currentTime, new ArrayList<>(), 0));
        long bestDuration = Long.MAX_VALUE;

        while (!queue.isEmpty()) {
            RouteNode node = queue.poll();
            String currentStation = node.station;
            LocalDateTime time = node.time;
            List<Map<String, Object>> routeSoFar = node.route;
            int transitCount = node.transit;

            if (transitCount > maxTransit)
                continue;

            // Kunci visit: stasiun|kereta_terakhir|jumlah_transit. Mencegah loop aneh di
            // stasiun yang sama.
            String lastTrainId = routeSoFar.isEmpty() ? "START"
                    : (String) routeSoFar.get(routeSoFar.size() - 1).get("train_id");
            String visitKey = currentStation + "|" + lastTrainId + "|" + transitCount;
            if (visited.contains(visitKey))
                continue;
            visited.add(visitKey);

            // --- INTI PERUBAHAN: TIDAK LAGI MELAKUKAN LOOP SEMUA KERETA ---
            // Langsung ambil daftar kereta yang relevan dari map yang sudah dibuat.
            List<Train> relevantTrains = schedule.getTrainsForStation(currentStation);

            for (Train train : relevantTrains) {
                List<String> route = train.getRoute();
                Map<String, String> departureTimes = train.getDepartureTimes();

                // --- Logika Cek Validitas Transit ---
                if (!routeSoFar.isEmpty()) {
                    String previousTrainId = (String) routeSoFar.get(routeSoFar.size() - 1).get("train_id");
                    if (!train.getId().equals(previousTrainId)) { // Ini adalah sebuah transit

                        // Normalisasi nama stasiun untuk lookup di map INTERCHANGE_STATIONS
                        String normalizedCurrentStation = currentStation.trim().toLowerCase().replaceAll("\\s+", " ");

                        // 1. Cek apakah stasiun ini adalah stasiun transit resmi
                        if (!INTERCHANGE_STATIONS.containsKey(normalizedCurrentStation)) {
                            continue; // Jika bukan stasiun transit, lewati kereta ini (tidak boleh pindah di sini)
                        }

                        // 2. Cek apakah perpindahan antar-jalur ini valid
                        OccupancyPredictor.Line currentTrainLine = OccupancyPredictor.getLine(train.getRoute());
                        // Dapatkan jalur kereta sebelumnya (perlu cari ulang train objectnya)
                        Train previousTrain = schedule.getTrains().stream()
                                .filter(t -> t.getId().equals(previousTrainId)).findFirst().orElse(null);
                        if (previousTrain == null)
                            continue; // seharusnya tidak terjadi

                        OccupancyPredictor.Line previousTrainLine = OccupancyPredictor
                                .getLine(previousTrain.getRoute());

                        Set<OccupancyPredictor.Line> allowedLines = INTERCHANGE_STATIONS.get(normalizedCurrentStation);
                        if (!allowedLines.contains(currentTrainLine) || !allowedLines.contains(previousTrainLine)) {
                            continue; // Perpindahan antar jalur ini tidak diizinkan di stasiun ini
                        }
                    }
                }

                // Logika pencarian sisanya tetap sama
                int startIdx = route.indexOf(currentStation);
                if (startIdx == -1) continue; // Pastikan stasiun awal ada di rute kereta ini
                for (int i = startIdx + 1; i < route.size(); i++) {
                    String nextStation = route.get(i);
                    String depTimeStr = departureTimes.get(currentStation);
                    String arrTimeStr = departureTimes.get(nextStation);
                    if (depTimeStr == null || arrTimeStr == null)
                        continue;

                    LocalDateTime depTime = time.toLocalDate().atTime(LocalTime.parse(depTimeStr));
                    LocalDateTime arrTime = time.toLocalDate().atTime(LocalTime.parse(arrTimeStr));
                    if (depTime.isBefore(time))
                        continue;

                    long newDuration = routeSoFar.isEmpty()
                            ? Duration.between(time, arrTime).toMinutes()
                            : Duration.between((LocalDateTime) routeSoFar.get(0).get("_departure_dt"), arrTime)
                                    .toMinutes();

                    if (newDuration > bestDuration)
                        continue;

                    Map<String, Integer> occupancyData = OccupancyPredictor.predict(train, time);
                    Integer occupancyAtStart = occupancyData.get(currentStation);

                    Map<String, Object> leg = new HashMap<>();
                    leg.put("train_id", train.getId());
                    leg.put("train_name", train.getName());
                    leg.put("start_station", currentStation);
                    leg.put("destination_station", nextStation);
                    leg.put("departure_time", depTime.format(DateTimeFormatter.ofPattern("HH:mm")));
                    leg.put("estimated_arrival", arrTime.format(DateTimeFormatter.ofPattern("HH:mm")));
                    leg.put("_departure_dt", depTime);
                    leg.put("_arrival_dt", arrTime);
                    leg.put("occupancy_percentage", occupancyAtStart);

                    List<Map<String, Object>> newRoute = new ArrayList<>(routeSoFar);
                    newRoute.add(leg);

                    if (nextStation.equals(destStation)) {
                        results.add(newRoute);
                        if (newDuration < bestDuration)
                            bestDuration = newDuration;
                    } else {
                        queue.add(new RouteNode(nextStation, arrTime.plusMinutes(1), newRoute, transitCount + 1));
                    }
                }
            }
        }
        return results;
    }

    public List<String> getAvailableStations() {
        Set<String> stations = schedule.getAllStations();
        List<String> stationList = new ArrayList<>(stations);
        Collections.sort(stationList);
        return stationList;
    }
}

/**
 * KELAS BARU: TrainScheduleGUI
 * Kelas ini mengelola semua komponen UI Swing
 */
class TrainScheduleGUI extends JFrame {
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
        JButton searchButton = new JButton("Cari Rute");
        JButton mapButton = new JButton("Lihat Peta");

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

        LocalDateTime currentTime = LocalDateTime.now(); // Gunakan waktu sekarang
        List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit(startStation, destStation, currentTime,
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

/**
 * KELAS BARU: TrainRouteRenderer
 * Renderer tabel kustom untuk mewarnai baris berdasarkan nama kereta.
 */
class TrainRouteRenderer extends DefaultTableCellRenderer {
    // Definisikan warna di sini
    private static final Color BOGOR_COLOR = Color.decode("#E30A16");
    private static final Color CIKARANG_COLOR = Color.decode("#0084D8");
    private static final Color TANJUNG_PRIOK_COLOR = Color.decode("#DD0067");
    private static final Color RANGKASBITUNG_COLOR = Color.decode("#16812B");
    private static final Color TANGERANG_COLOR = Color.decode("#623814");
    private static final Color TRANSIT_COLOR = new Color(220, 220, 220); // Abu-abu muda untuk transit

    @Override
    public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus,
            int row, int column) {
        Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);

        // Ambil nama kereta dari kolom pertama (indeks 0)
        String trainName = (String) table.getValueAt(row, 0);

        if (trainName == null) {
            c.setBackground(table.getBackground());
            c.setForeground(table.getForeground());
            return c;
        }

        // Tentukan warna berdasarkan nama kereta
        Color rowColor = table.getBackground(); // Warna default
        if (trainName.toLowerCase().contains("bogor")) {
            rowColor = BOGOR_COLOR;
        } else if (trainName.toLowerCase().contains("cikarang")) {
            rowColor = CIKARANG_COLOR;
        } else if (trainName.toLowerCase().contains("tanjung priok")) {
            rowColor = TANJUNG_PRIOK_COLOR;
        } else if (trainName.toLowerCase().contains("rangkasbitung")) {
            rowColor = RANGKASBITUNG_COLOR;
        } else if (trainName.toLowerCase().contains("tangerang")) {
            rowColor = TANGERANG_COLOR;
        } else if (trainName.contains("TRANSIT") || trainName.contains("ALTERNATIF")) {
            rowColor = TRANSIT_COLOR;
        }

        c.setBackground(rowColor);

        // Atur warna teks agar kontras dengan latar belakang
        // Jika warna latar terlalu gelap, buat teks menjadi putih
        if (rowColor.equals(BOGOR_COLOR) || rowColor.equals(RANGKASBITUNG_COLOR) || rowColor.equals(TANGERANG_COLOR)) {
            c.setForeground(Color.WHITE);
        } else {
            c.setForeground(Color.BLACK);
        }

        // Khusus untuk baris transit/alternatif
        if (trainName.contains("TRANSIT") || trainName.contains("ALTERNATIF")) {
            c.setFont(new Font("SansSerif", Font.BOLD | Font.ITALIC, 12));
            setHorizontalAlignment(SwingConstants.CENTER);
        } else {
            c.setFont(table.getFont());
            setHorizontalAlignment(SwingConstants.LEFT);
        }

        if (isSelected) {
            c.setBackground(table.getSelectionBackground());
            c.setForeground(table.getSelectionForeground());
        }

        return c;
    }
}

public class Kode_JagoanIT {
    public static void main(String[] args) {
        // Jalankan aplikasi di Event Dispatch Thread (EDT) Swing
        SwingUtilities.invokeLater(() -> {
            try {
                TrainSchedule schedule = new TrainSchedule("train_schedule_Jabodetabek.csv");
                TrainSchedulePredictorApp app = new TrainSchedulePredictorApp(schedule);
                TrainScheduleGUI gui = new TrainScheduleGUI(app);
                gui.setVisible(true);
            } catch (IOException e) {
                JOptionPane.showMessageDialog(null,
                        "Gagal memuat jadwal kereta (train_schedule_Jabodetabek.csv): " + e.getMessage(), "Fatal Error",
                        JOptionPane.ERROR_MESSAGE);
                e.printStackTrace();
            } catch (Exception e) {
                JOptionPane.showMessageDialog(null, "Terjadi kesalahan yang tidak terduga: " + e.getMessage(),
                        "Fatal Error", JOptionPane.ERROR_MESSAGE);
                e.printStackTrace();
            }
        });
    }
}