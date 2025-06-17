import java.awt.*;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.time.DayOfWeek;
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

class Train {
    private final String id;
    private final String name;
    private final List<String> route;
    private final Map<String, String> departureTimes;

    public Train(String id, String name, List<String> route, Map<String, String> departureTimes) {
        this.id = id;
        this.name = name;
        this.route = route;
        this.departureTimes = departureTimes;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public List<String> getRoute() { return route; }
    public Map<String, String> getDepartureTimes() { return departureTimes; }
}

class TrainSchedule {
    private final List<Train> trains;

    public TrainSchedule(String csvFile) throws IOException {
        this.trains = loadFromCSV(csvFile);
    }

    private List<Train> loadFromCSV(String filename) throws IOException {
        List<Train> schedule = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
            br.readLine(); // Skip header
            String line;
            while ((line = br.readLine()) != null) {
                String[] values = line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1);
                String id = values[0];
                String name = values[1];
                List<String> route = Arrays.asList(values[2].replace("\"", "").split(","));
                Map<String, String> departureTimes = new HashMap<>();
                String[] times = values[3].replace("\"", "").split(",");
                for (String time : times) {
                    String[] parts = time.split(":");
                    departureTimes.put(parts[0], parts[1] + ":" + parts[2]);
                }
                schedule.add(new Train(id, name, route, departureTimes));
            }
        }
        return schedule;
    }

    public List<Train> getTrains() { return trains; }

    public Set<String> getAllStations() {
        Set<String> stations = new HashSet<>();
        for (Train train : trains)
            stations.addAll(train.getRoute());
        return stations;
    }
}

class OccupancyPredictor {
    private enum Line { BOGOR, CIKARANG, RANGKASBITUNG, TANGERANG, TANJUNG_PRIOK, UNKNOWN }
    private enum Direction { MENUJU_JAKARTA, MENUJU_BOGOR, MENUJU_CIKARANG, MENUJU_RANGKASBITUNG, MENUJU_TANGERANG, DUA_ARAH, UNKNOWN }
    private enum TimePeriod { PUNCAK_PAGI, SIANG, PUNCAK_SORE, MALAM, AKHIR_PEKAN }
    private static final Map<Line, Map<Direction, Map<TimePeriod, Integer>>> occupancyMatrix = new HashMap<>();

    static {
        java.util.function.Function<String, Integer> avg = rangeStr -> {
            String[] parts = rangeStr.replaceAll("[^0-9\\-]", "").split("-");
            if (parts.length == 1) return Integer.parseInt(parts[0]);
            return (Integer.parseInt(parts[0]) + Integer.parseInt(parts[1])) / 2;
        };
        Map<Direction, Map<TimePeriod, Integer>> bogorLine = new HashMap<>();
        Map<TimePeriod, Integer> bogorToJakarta = new HashMap<>();
        bogorToJakarta.put(TimePeriod.PUNCAK_PAGI, avg.apply("150-200%+"));
        bogorToJakarta.put(TimePeriod.SIANG, avg.apply("40-60%"));
        bogorToJakarta.put(TimePeriod.PUNCAK_SORE, avg.apply("70-100%"));
        bogorToJakarta.put(TimePeriod.MALAM, avg.apply("50-80%"));
        bogorToJakarta.put(TimePeriod.AKHIR_PEKAN, avg.apply("90-120%"));
        Map<TimePeriod, Integer> bogorToBogor = new HashMap<>();
        bogorToBogor.put(TimePeriod.PUNCAK_PAGI, avg.apply("60-90%"));
        bogorToBogor.put(TimePeriod.SIANG, avg.apply("50-70%"));
        bogorToBogor.put(TimePeriod.PUNCAK_SORE, avg.apply("140-180%"));
        bogorToBogor.put(TimePeriod.MALAM, avg.apply("80-110%"));
        bogorToBogor.put(TimePeriod.AKHIR_PEKAN, avg.apply("70-100%"));
        bogorLine.put(Direction.MENUJU_JAKARTA, bogorToJakarta);
        bogorLine.put(Direction.MENUJU_BOGOR, bogorToBogor);
        occupancyMatrix.put(Line.BOGOR, bogorLine);

        Map<Direction, Map<TimePeriod, Integer>> cikarangLine = new HashMap<>();
        Map<TimePeriod, Integer> toJakarta = new HashMap<>();
        toJakarta.put(TimePeriod.PUNCAK_PAGI, avg.apply("130-170%"));
        toJakarta.put(TimePeriod.SIANG, avg.apply("35-55%"));
        toJakarta.put(TimePeriod.PUNCAK_SORE, avg.apply("60-80%"));
        toJakarta.put(TimePeriod.MALAM, avg.apply("40-60%"));
        toJakarta.put(TimePeriod.AKHIR_PEKAN, avg.apply("60-90%"));
        Map<TimePeriod, Integer> toCikarang = new HashMap<>();
        toCikarang.put(TimePeriod.PUNCAK_PAGI, avg.apply("50-70%"));
        toCikarang.put(TimePeriod.SIANG, avg.apply("40-60%"));
        toCikarang.put(TimePeriod.PUNCAK_SORE, avg.apply("120-160%"));
        toCikarang.put(TimePeriod.MALAM, avg.apply("70-100%"));
        toCikarang.put(TimePeriod.AKHIR_PEKAN, avg.apply("60-90%"));
        cikarangLine.put(Direction.MENUJU_JAKARTA, toJakarta);
        cikarangLine.put(Direction.MENUJU_CIKARANG, toCikarang);
        occupancyMatrix.put(Line.CIKARANG, cikarangLine);

        Map<Direction, Map<TimePeriod, Integer>> rangkasLine = new HashMap<>();
        Map<TimePeriod, Integer> rangkasToJakarta = new HashMap<>();
        rangkasToJakarta.put(TimePeriod.PUNCAK_PAGI, avg.apply("160-220%+"));
        rangkasToJakarta.put(TimePeriod.SIANG, avg.apply("50-70%"));
        rangkasToJakarta.put(TimePeriod.PUNCAK_SORE, avg.apply("80-110%"));
        rangkasToJakarta.put(TimePeriod.MALAM, avg.apply("60-90%"));
        rangkasToJakarta.put(TimePeriod.AKHIR_PEKAN, avg.apply("80-110%"));
        Map<TimePeriod, Integer> rangkasToRangkas = new HashMap<>();
        rangkasToRangkas.put(TimePeriod.PUNCAK_PAGI, avg.apply("60-80%"));
        rangkasToRangkas.put(TimePeriod.SIANG, avg.apply("60-80%"));
        rangkasToRangkas.put(TimePeriod.PUNCAK_SORE, avg.apply("150-200%"));
        rangkasToRangkas.put(TimePeriod.MALAM, avg.apply("90-120%"));
        rangkasToRangkas.put(TimePeriod.AKHIR_PEKAN, avg.apply("80-110%"));
        rangkasLine.put(Direction.MENUJU_JAKARTA, rangkasToJakarta);
        rangkasLine.put(Direction.MENUJU_RANGKASBITUNG, rangkasToRangkas);
        occupancyMatrix.put(Line.RANGKASBITUNG, rangkasLine);

        Map<Direction, Map<TimePeriod, Integer>> tangerangLine = new HashMap<>();
        Map<TimePeriod, Integer> tangerangToJakarta = new HashMap<>();
        tangerangToJakarta.put(TimePeriod.PUNCAK_PAGI, avg.apply("120-160%"));
        tangerangToJakarta.put(TimePeriod.SIANG, avg.apply("40-60%"));
        tangerangToJakarta.put(TimePeriod.PUNCAK_SORE, avg.apply("60-80%"));
        tangerangToJakarta.put(TimePeriod.MALAM, avg.apply("45-65%"));
        tangerangToJakarta.put(TimePeriod.AKHIR_PEKAN, avg.apply("50-75%"));
        Map<TimePeriod, Integer> tangerangToTangerang = new HashMap<>();
        tangerangToTangerang.put(TimePeriod.PUNCAK_PAGI, avg.apply("50-70%"));
        tangerangToTangerang.put(TimePeriod.SIANG, avg.apply("45-65%"));
        tangerangToTangerang.put(TimePeriod.PUNCAK_SORE, avg.apply("110-150%"));
        tangerangToTangerang.put(TimePeriod.MALAM, avg.apply("70-90%"));
        tangerangToTangerang.put(TimePeriod.AKHIR_PEKAN, avg.apply("50-75%"));
        tangerangLine.put(Direction.MENUJU_JAKARTA, tangerangToJakarta);
        tangerangLine.put(Direction.MENUJU_TANGERANG, tangerangToTangerang);
        occupancyMatrix.put(Line.TANGERANG, tangerangLine);

        Map<Direction, Map<TimePeriod, Integer>> priokLine = new HashMap<>();
        Map<TimePeriod, Integer> priokTwoWay = new HashMap<>();
        priokTwoWay.put(TimePeriod.PUNCAK_PAGI, avg.apply("20-40%"));
        priokTwoWay.put(TimePeriod.SIANG, avg.apply("15-30%"));
        priokTwoWay.put(TimePeriod.PUNCAK_SORE, avg.apply("25-40%"));
        priokTwoWay.put(TimePeriod.MALAM, avg.apply("15-30%"));
        priokTwoWay.put(TimePeriod.AKHIR_PEKAN, avg.apply("20-35%"));
        priokLine.put(Direction.DUA_ARAH, priokTwoWay);
        occupancyMatrix.put(Line.TANJUNG_PRIOK, priokLine);
    }
    private static final LocalTime MORNING_PEAK_START = LocalTime.of(5, 30);
    private static final LocalTime MORNING_PEAK_END = LocalTime.of(8, 30);
    private static final LocalTime DAYTIME_START = LocalTime.of(9, 0);
    private static final LocalTime DAYTIME_END = LocalTime.of(15, 0);
    private static final LocalTime EVENING_PEAK_START = LocalTime.of(15, 30);
    private static final LocalTime EVENING_PEAK_END = LocalTime.of(19, 0);
    private static final int MIN_OCCUPANCY = 5;
    private static final int MAX_OCCUPANCY = 98;
    private static final int DEFAULT_OCCUPANCY = 30;
    private static String normalizeStation(String s) { return s.trim().toLowerCase().replaceAll("\\s+", " "); }
    private static Line getLine(List<String> route) {
        Set<String> routeSet = new HashSet<>();
        for (String station : route) routeSet.add(normalizeStation(station));
        if (routeSet.contains("bekasi") || routeSet.contains("cikarang") || routeSet.contains("tambun")) return Line.CIKARANG;
        if (routeSet.contains("parung panjang") || routeSet.contains("serpong") || routeSet.contains("rangkasbitung") || routeSet.contains("kebayoran")) return Line.RANGKASBITUNG;
        if (routeSet.contains("rawa buaya") || routeSet.contains("batu ceper") || routeSet.contains("tangerang")) return Line.TANGERANG;
        if (routeSet.contains("ancol") || routeSet.contains("tanjung priok")) return Line.TANJUNG_PRIOK;
        if (routeSet.contains("depok") || routeSet.contains("citayam") || routeSet.contains("bogor") || routeSet.contains("tebet")) return Line.BOGOR;
        return Line.UNKNOWN;
    }
    private static Direction getDirection(List<String> route) {
        if (route == null || route.size() < 2) return Direction.UNKNOWN;
        String first = normalizeStation(route.get(0));
        String last = normalizeStation(route.get(route.size() - 1));
        if (first.contains("tanjung priok") || last.contains("tanjung priok")) return Direction.DUA_ARAH;
        if (last.contains("jakarta") || last.contains("duri") || last.contains("angke") || last.contains("tanah abang")) return Direction.MENUJU_JAKARTA;
        if (last.contains("bogor") || last.contains("nambo")) return Direction.MENUJU_BOGOR;
        if (last.contains("cikarang")) return Direction.MENUJU_CIKARANG;
        if (last.contains("rangkasbitung") || last.contains("parung panjang") || last.contains("serpong")) return Direction.MENUJU_RANGKASBITUNG;
        if (last.contains("tangerang")) return Direction.MENUJU_TANGERANG;
        return Direction.UNKNOWN;
    }
    private static TimePeriod getTimePeriod(LocalDateTime dateTime) {
        DayOfWeek day = dateTime.getDayOfWeek();
        if (day == DayOfWeek.SATURDAY || day == DayOfWeek.SUNDAY) return TimePeriod.AKHIR_PEKAN;
        LocalTime time = dateTime.toLocalTime();
        if (!time.isBefore(MORNING_PEAK_START) && time.isBefore(MORNING_PEAK_END)) return TimePeriod.PUNCAK_PAGI;
        if (!time.isBefore(DAYTIME_START) && time.isBefore(DAYTIME_END)) return TimePeriod.SIANG;
        if (!time.isBefore(EVENING_PEAK_START) && time.isBefore(EVENING_PEAK_END)) return TimePeriod.PUNCAK_SORE;
        return TimePeriod.MALAM;
    }
    public static Map<String, Integer> predict(Train train, LocalDateTime currentTime) {
        Map<String, Integer> occupancyMap = new HashMap<>();
        List<String> route = train.getRoute();
        if (route == null || route.isEmpty()) return occupancyMap;
        Line line = getLine(route);
        Direction direction = getDirection(route);
        TimePeriod period = getTimePeriod(currentTime);
        int occupancy = occupancyMatrix
                .getOrDefault(line, Collections.emptyMap())
                .getOrDefault(direction, Collections.emptyMap())
                .getOrDefault(period, DEFAULT_OCCUPANCY);
        int finalOccupancy = Math.max(MIN_OCCUPANCY, Math.min(occupancy, MAX_OCCUPANCY));
        for (String station : route) occupancyMap.put(station, finalOccupancy);
        return occupancyMap;
    }
}

class TrainSchedulePredictorApp {
    private final TrainSchedule schedule;
    private final int maxResultCount = 3; // Tampilkan hingga 3 rute terbaik

    public TrainSchedulePredictorApp(TrainSchedule schedule) {
        this.schedule = schedule;
    }

    public static void showMapImage(String imagePath) {
        try {
            ImageIcon icon = new ImageIcon(new ImageIcon(imagePath).getImage().getScaledInstance(800, 600, Image.SCALE_SMOOTH));
            JLabel label = new JLabel(icon);
            JFrame frame = new JFrame("Peta Rute KRL");
            frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            frame.getContentPane().add(label, BorderLayout.CENTER);
            frame.pack();
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Gagal memuat gambar peta: " + imagePath + "\nError: " + e.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    public List<List<Map<String, Object>>> predictRoutesWithTransit(
            String startStation, String destStation, LocalDateTime currentTime, int maxTransit) {
        return bfsFindRoutes(startStation, destStation, currentTime, maxTransit);
    }

    private static class RouteNode {
        String station;
        LocalDateTime time;
        List<Map<String, Object>> route;
        int transit;

        RouteNode(String station, LocalDateTime time, List<Map<String, Object>> route, int transit) {
            this.station = station;
            this.time = time;
            this.route = route;
            this.transit = transit;
        }
    }

    public List<List<Map<String, Object>>> bfsFindRoutes(
            String startStation, String destStation, LocalDateTime currentTime, int maxTransit) {
        Queue<RouteNode> queue = new LinkedList<>();
        List<List<Map<String, Object>>> results = new ArrayList<>();
        Set<String> visited = new HashSet<>();

        queue.add(new RouteNode(startStation, currentTime, new ArrayList<>(), 0));
        long bestDuration = Long.MAX_VALUE;

        while (!queue.isEmpty()) {
            RouteNode node = queue.poll();
            String currentStation = node.station;
            LocalDateTime time = node.time;
            List<Map<String, Object>> routeSoFar = node.route;
            int transitCount = node.transit;

            if (transitCount > maxTransit) continue;

            String visitKey = currentStation + "|" + time.toLocalDate().toString() + "|" + transitCount;
            if (visited.contains(visitKey)) continue;
            visited.add(visitKey);

            for (Train train : schedule.getTrains()) {
                List<String> route = train.getRoute();
                Map<String, String> departureTimes = train.getDepartureTimes();
                if (!route.contains(currentStation)) continue;
                int startIdx = route.indexOf(currentStation);

                for (int i = startIdx + 1; i < route.size(); i++) {
                    String nextStation = route.get(i);
                    String depTimeStr = departureTimes.get(currentStation);
                    String arrTimeStr = departureTimes.get(nextStation);
                    if (depTimeStr == null || arrTimeStr == null) continue;

                    LocalDateTime depTime = time.toLocalDate().atTime(LocalTime.parse(depTimeStr));
                    LocalDateTime arrTime = time.toLocalDate().atTime(LocalTime.parse(arrTimeStr));
                    if (depTime.isBefore(time)) continue;

                    long newDuration = routeSoFar.isEmpty()
                            ? Duration.between(time, arrTime).toMinutes()
                            : Duration.between((LocalDateTime) routeSoFar.get(0).get("_departure_dt"), arrTime).toMinutes();

                    if (!results.isEmpty() && newDuration > bestDuration) continue;

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
                        if (newDuration < bestDuration) bestDuration = newDuration;
                    } else {
                        // Untuk transit, asumsikan waktu tunggu minimal
                        queue.add(new RouteNode(nextStation, arrTime.plusMinutes(2), newRoute, transitCount + (routeSoFar.isEmpty() || !routeSoFar.get(routeSoFar.size() - 1).get("train_id").equals(train.getId()) ? 1 : 0)));
                    }
                }
            }
        }
        results.sort(Comparator.comparingLong((List<Map<String, Object>> route) ->
                Duration.between((LocalDateTime) route.get(0).get("_departure_dt"), (LocalDateTime) route.get(route.size() - 1).get("_arrival_dt")).toMinutes()));
        
        if (results.size() > maxResultCount) {
            return results.subList(0, maxResultCount);
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
        String[] columnNames = {"Nama Kereta", "Berangkat", "Tiba", "Okupansi"};
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

    private void findAndDisplayRoutes() {
        String startStation = (String) startStationBox.getSelectedItem();
        String destStation = (String) destStationBox.getSelectedItem();

        if (startStation.equals(destStation)) {
            JOptionPane.showMessageDialog(this, "Stasiun awal dan tujuan tidak boleh sama.", "Input Error", JOptionPane.ERROR_MESSAGE);
            return;
        }

        // Hapus hasil sebelumnya
        tableModel.setRowCount(0);

        LocalDateTime currentTime = LocalDateTime.now(); // Gunakan waktu sekarang
        List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit(startStation, destStation, currentTime, 3);

        if (routes.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Maaf, tidak ditemukan rute untuk pilihan Anda.", "Tidak Ada Rute", JOptionPane.INFORMATION_MESSAGE);
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

                    tableModel.addRow(new Object[]{fullTrainName, departureTime, arrivalTime, occupancyInfo});
                    
                    // Jika ada transit, tambahkan baris penanda
                    if (j + 1 < route.size()){
                         tableModel.addRow(new Object[]{"--- TRANSIT ---", "", "", ""});
                    }

                    i = j + 1;
                }
                 // Tambahkan pemisah antar rute jika ada lebih dari satu rute ditemukan
                if(routes.size() > 1 && routes.indexOf(route) < routes.size() -1){
                    tableModel.addRow(new Object[]{"","","",""});
                    tableModel.addRow(new Object[]{"=== RUTE ALTERNATIF ===", "", "", ""});
                    tableModel.addRow(new Object[]{"","","",""});
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
    public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
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
        if (trainName.contains("TRANSIT") || trainName.contains("ALTERNATIF")){
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
                JOptionPane.showMessageDialog(null, "Gagal memuat jadwal kereta (train_schedule_Jabodetabek.csv): " + e.getMessage(), "Fatal Error", JOptionPane.ERROR_MESSAGE);
                e.printStackTrace();
            } catch (Exception e) {
                 JOptionPane.showMessageDialog(null, "Terjadi kesalahan yang tidak terduga: " + e.getMessage(), "Fatal Error", JOptionPane.ERROR_MESSAGE);
                e.printStackTrace();
            }
        });
    }
}