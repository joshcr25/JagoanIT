import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.ArrayList;
import java.util.Queue;
import java.util.LinkedList;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.awt.*;
import java.time.Duration;
import java.time.format.DateTimeFormatter;
import java.util.Collections;

import javax.swing.*;

public class TrainSchedulePredictorApp {
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

    private static class RouteNode {
        String station;
        LocalDateTime time;
        List<Map<String, Object>> route;
        int transit;

        RouteNode() {
            this.station = "";
            this.time = LocalDateTime.now();
            this.route = new ArrayList<>();
            this.transit = 0;
        }

        RouteNode(String station, LocalDateTime time, List<Map<String, Object>> route, int transit) {
            this.station = station;
            this.time = time;
            this.route = route;
            this.transit = transit;
        }
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