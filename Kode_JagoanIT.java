import java.awt.BorderLayout;
import java.io.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import javax.swing.*;

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

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public List<String> getRoute() {
        return route;
    }

    public Map<String, String> getDepartureTimes() {
        return departureTimes;
    }
}

class TrainSchedule {
    private final List<Train> trains;

    public TrainSchedule(String csvFile) throws IOException {
        this.trains = loadFromCSV(csvFile);
    }

    private List<Train> loadFromCSV(String filename) throws IOException {
        List<Train> schedule = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
            String line;
            br.readLine(); // Skip header
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

    public List<Train> getTrains() {
        return trains;
    }

    public Set<String> getAllStations() {
        Set<String> stations = new HashSet<>();
        for (Train train : trains)
            stations.addAll(train.getRoute());
        return stations;
    }
}

class OccupancyPredictor {

    // --- DATA PROFIL BERDASARKAN GAMBAR ---
    // Profil Pagi Hari (Arah Jakarta Kota)
    private static final Map<String, Integer> MORNING_PEAK_JAKARTA_BOUND = new HashMap<>();
    static {
        MORNING_PEAK_JAKARTA_BOUND.put("Bogor", 5);
        MORNING_PEAK_JAKARTA_BOUND.put("Depok", 55);
        MORNING_PEAK_JAKARTA_BOUND.put("Pasar Minggu", 75);
        MORNING_PEAK_JAKARTA_BOUND.put("Manggarai", 83);
        MORNING_PEAK_JAKARTA_BOUND.put("Gondangdia", 70);
        MORNING_PEAK_JAKARTA_BOUND.put("Juanda", 45);
        MORNING_PEAK_JAKARTA_BOUND.put("Sawah Besar", 20);
        MORNING_PEAK_JAKARTA_BOUND.put("Jakarta Kota", 5);
    }

    // Profil Sore Hari (Arah Bogor)
    private static final Map<String, Integer> EVENING_PEAK_BOGOR_BOUND = new HashMap<>();
    static {
        EVENING_PEAK_BOGOR_BOUND.put("Jakarta Kota", 5);
        EVENING_PEAK_BOGOR_BOUND.put("Juanda", 50);
        EVENING_PEAK_BOGOR_BOUND.put("Gondangdia", 70);
        EVENING_PEAK_BOGOR_BOUND.put("Manggarai", 83);
        EVENING_PEAK_BOGOR_BOUND.put("Pasar Minggu", 70);
        EVENING_PEAK_BOGOR_BOUND.put("Depok", 40);
        EVENING_PEAK_BOGOR_BOUND.put("Citayam", 20);
        EVENING_PEAK_BOGOR_BOUND.put("Bogor", 5);
    }

    // --- KONFIGURASI WAKTU & OKUPANSI ---
    private static final LocalTime MORNING_PEAK_START = LocalTime.of(5, 30);
    private static final LocalTime MORNING_PEAK_END = LocalTime.of(8, 30);
    private static final LocalTime EVENING_PEAK_START = LocalTime.of(15, 30);
    private static final LocalTime EVENING_PEAK_END = LocalTime.of(19, 0);

    // Improved: Off-peak occupancy now varies by time of day
    private static int getOffPeakOccupancy(LocalTime time) {
        // Paling sepi (11:00 - 14:00): 5% - 35%
        if (!time.isBefore(LocalTime.of(11, 0)) && time.isBefore(LocalTime.of(14, 0))) {
            return 15; // Sangat lengang, banyak kursi kosong
        }
        // Cukup ramai (09:00 - 10:30 & 14:00 - 15:00): 45% - 55%
        if ((!time.isBefore(LocalTime.of(9, 0)) && time.isBefore(LocalTime.of(10, 30)))
                || (!time.isBefore(LocalTime.of(14, 0)) && time.isBefore(LocalTime.of(15, 0)))) {
            return 50; // Lengang, mudah dapat tempat duduk
        }
        // Default off-peak (malam, sore, subuh, dll)
        return 25;
    }

    private static final int MIN_OCCUPANCY = 5;
    private static final int MAX_OCCUPANCY = 98;

    // Enum untuk merepresentasikan arah perjalanan
    private enum Direction {
        JAKARTA_BOUND, BOGOR_BOUND, UNKNOWN
    }

    /**
     * Prediksi okupansi dengan memperhitungkan waktu dan arah perjalanan.
     * 
     * @param train       Kereta yang akan diprediksi.
     * @param currentTime Waktu saat ini untuk menentukan konteks jam sibuk.
     * @return Map berisi prediksi okupansi per stasiun.
     */

    private static String normalizeStation(String s) {
        return s.trim().toLowerCase().replaceAll("\\s+", " ");
    }

    private static boolean stationEquals(String a, String b) {
        return normalizeStation(a).equals(normalizeStation(b));
    }

    // Menentukan arah perjalanan berdasarkan urutan stasiun
    private static Direction getDirection(List<String> route) {
        if (route == null || route.size() < 2)
            return Direction.UNKNOWN;
        String first = normalizeStation(route.get(0));
        String last = normalizeStation(route.get(route.size() - 1));
        if (first.contains("bogor") && last.contains("jakarta")) {
            return Direction.JAKARTA_BOUND;
        } else if (first.contains("jakarta") && last.contains("bogor")) {
            return Direction.BOGOR_BOUND;
        }
        return Direction.UNKNOWN;
    }

    // Mengambil profil okupansi sesuai waktu dan arah
    private static Map<String, Integer> getPeakProfile(LocalTime time, Direction direction) {
        if (direction == Direction.JAKARTA_BOUND &&
                !time.isBefore(MORNING_PEAK_START) && time.isBefore(MORNING_PEAK_END)) {
            return MORNING_PEAK_JAKARTA_BOUND;
        }
        if (direction == Direction.BOGOR_BOUND &&
                !time.isBefore(EVENING_PEAK_START) && time.isBefore(EVENING_PEAK_END)) {
            return EVENING_PEAK_BOGOR_BOUND;
        }
        return null;
    }

    public static Map<String, Integer> predict(Train train, LocalDateTime currentTime) {
        List<String> route = train.getRoute();
        Map<String, Integer> occupancyMap = new HashMap<>();
        if (route == null || route.isEmpty()) {
            return occupancyMap;
        }

        LocalTime time = currentTime.toLocalTime();
        Direction direction = getDirection(route);
        Map<String, Integer> profile = getPeakProfile(time, direction);

        if (profile != null) {
            // --- LOGIKA JAM SIBUK ---
            for (int i = 0; i < route.size(); i++) {
                String station = route.get(i);
                boolean found = false;
                for (String key : profile.keySet()) {
                    if (stationEquals(key, station)) {
                        found = true;
                        break;
                    }
                }
                if (found) {
                    occupancyMap.put(station, profile.get(station));
                } else {
                    occupancyMap.put(station, interpolateOccupancy(route, i, profile, time));
                }
            }
        } else {
            // --- LOGIKA DI LUAR JAM SIBUK (OFF-PEAK) DENGAN INTERPOLASI ---
            int offPeakStart = MIN_OCCUPANCY;
            int offPeakEnd = MIN_OCCUPANCY;
            int offPeakMid = getOffPeakOccupancy(time);

            int n = route.size();
            for (int i = 0; i < n; i++) {
                // Interpolasi linear: naik dari MIN ke MID, lalu turun ke MIN
                double pos = (double) i / (n - 1);
                int interpolated;
                if (pos <= 0.5) {
                    interpolated = (int) (offPeakStart + (offPeakMid - offPeakStart) * (pos / 0.5));
                } else {
                    interpolated = (int) (offPeakMid + (offPeakEnd - offPeakMid) * ((pos - 0.5) / 0.5));
                }
                occupancyMap.put(route.get(i), Math.max(MIN_OCCUPANCY, Math.min(MAX_OCCUPANCY, interpolated)));
            }
        }
        return occupancyMap;
    }

    /**
     * Mengestimasi okupansi stasiun yang tidak ada di profil
     * dengan mencari stasiun terdekat sebelum dan sesudahnya yang ada di profil.
     */
    private static int interpolateOccupancy(List<String> route, int currentIndex, Map<String, Integer> profile,
            LocalTime time) {
        String currentStation = route.get(currentIndex);

        // Cari stasiun terdekat sebelumnya yang ada di profil
        Integer prevStationIndex = null;
        Integer prevOccupancy = null;
        for (int i = currentIndex - 1; i >= 0; i--) {
            for (String key : profile.keySet()) {
                if (stationEquals(key, route.get(i))) {
                    prevStationIndex = i;
                    prevOccupancy = profile.get(key);
                    break;
                }
            }
            if (prevStationIndex != null)
                break;
        }

        // Cari stasiun terdekat sesudahnya yang ada di profil
        Integer nextStationIndex = null;
        Integer nextOccupancy = null;
        for (int i = currentIndex + 1; i < route.size(); i++) {
            for (String key : profile.keySet()) {
                if (stationEquals(key, route.get(i))) {
                    nextStationIndex = i;
                    nextOccupancy = profile.get(key);
                    break;
                }
            }
            if (nextStationIndex != null)
                break;
        }

        if (prevStationIndex != null && nextStationIndex != null) {
            double totalStops = nextStationIndex - prevStationIndex;
            double currentPosition = currentIndex - prevStationIndex;
            double occupancySlope = (nextOccupancy - prevOccupancy) / totalStops;
            double estimatedOccupancy = prevOccupancy + (occupancySlope * currentPosition);
            return (int) Math.max(MIN_OCCUPANCY, Math.min(MAX_OCCUPANCY, estimatedOccupancy));
        } else if (prevOccupancy != null) {
            return prevOccupancy;
        } else if (nextOccupancy != null) {
            return nextOccupancy;
        }
        return getOffPeakOccupancy(time);
    }
}

class TrainSchedulePredictorApp {
    private final TrainSchedule schedule;
    private long bestDuration = Long.MAX_VALUE;
    private int maxResultCount = 1; // Tampilkan hanya 1 rute

    public TrainSchedulePredictorApp(TrainSchedule schedule) {
        this.schedule = schedule;
    }

    public static void showMapImage(String imagePath) {
        JFrame frame = new JFrame("Peta Rute KRL");
        frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        ImageIcon icon = new ImageIcon(imagePath);
        JLabel label = new JLabel(icon);
        frame.getContentPane().add(label, BorderLayout.CENTER);
        frame.pack();
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }

    public List<List<Map<String, Object>>> predictRoutesWithTransit(
            String startStation, String destStation, LocalDateTime currentTime, int maxTransit) {
        List<List<Map<String, Object>>> results = new ArrayList<>();
        Set<String> visited = new HashSet<>();
        bestDuration = Long.MAX_VALUE;
        dfsFindRoutes(startStation, destStation, currentTime, maxTransit, new ArrayList<>(), results, visited, 0, true);
        // Sort hasil
        results.sort(Comparator.comparingInt((List<Map<String, Object>> route) -> route.size())
                .thenComparing(route -> {
                    LocalDateTime dep = (LocalDateTime) route.get(0).get("_departure_dt");
                    LocalDateTime arr = (LocalDateTime) route.get(route.size() - 1).get("_arrival_dt");
                    return Duration.between(dep, arr).toMinutes();
                }));
        // Batasi hasil
        if (results.size() > maxResultCount) {
            return results.subList(0, maxResultCount);
        }
        return results;
    }

    // Tambahkan parameter onlyDirectFromStart
    private void dfsFindRoutes(
            String currentStation, String destStation, LocalDateTime currentTime, int remainingTransit,
            List<Map<String, Object>> currentRoute, List<List<Map<String, Object>>> results, Set<String> visited,
            long currentDuration, boolean onlyDirectFromStart) {
        if (remainingTransit < 0 || results.size() >= maxResultCount)
            return;
        String visitKey = currentStation + "|" + currentTime.toString() + "|" + remainingTransit;
        if (visited.contains(visitKey))
            return;
        visited.add(visitKey);

        for (Train train : schedule.getTrains()) {
            List<String> route = train.getRoute();
            Map<String, String> departureTimes = train.getDepartureTimes();
            if (!route.contains(currentStation))
                continue;
            int startIdx = route.indexOf(currentStation);

            // Cari stasiun terjauh yang bisa dicapai dengan kereta ini
            for (int i = route.size() - 1; i > startIdx; i--) {
                String nextStation = route.get(i);
                String depTimeStr = departureTimes.get(currentStation);
                String arrTimeStr = departureTimes.get(nextStation);
                if (depTimeStr == null || arrTimeStr == null)
                    continue;

                LocalDateTime depTime = currentTime.toLocalDate().atTime(LocalTime.parse(depTimeStr));
                LocalDateTime arrTime = currentTime.toLocalDate().atTime(LocalTime.parse(arrTimeStr));
                if (depTime.isBefore(currentTime))
                    continue;

                long newDuration = currentRoute.isEmpty()
                        ? Duration.between(currentTime, arrTime).toMinutes()
                        : Duration.between((LocalDateTime) currentRoute.get(0).get("_departure_dt"), arrTime)
                                .toMinutes();

                if (newDuration > bestDuration)
                    continue;

                Map<String, Integer> occupancyData = OccupancyPredictor.predict(train, currentTime);
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

                List<Map<String, Object>> newRoute = new ArrayList<>(currentRoute);
                newRoute.add(leg);

                if (nextStation.equals(destStation)) {
                    results.add(newRoute);
                    if (newDuration < bestDuration) {
                        bestDuration = newDuration;
                    }
                } else {
                    dfsFindRoutes(nextStation, destStation, arrTime.plusMinutes(1), remainingTransit - 1, newRoute,
                            results, new HashSet<>(visited), newDuration, false);
                }
                // Hanya ambil satu leg terjauh untuk satu kereta
                break;
            }
        }
        visited.remove(visitKey);
    }

    // Tambahkan metode ini:
    public List<String> getAvailableStations() {
        Set<String> stations = schedule.getAllStations();
        List<String> stationList = new ArrayList<>(stations);
        Collections.sort(stationList);
        return stationList;
    }

    public static void main(String[] args) {
        try {
            TrainSchedule schedule = new TrainSchedule("train_schedule.csv");
            TrainSchedulePredictorApp app = new TrainSchedulePredictorApp(schedule);
            LocalDateTime simulatedCurrentTime = LocalDateTime.of(2025, 6, 14, 6, 30);
            Scanner scanner = new Scanner(System.in);

            List<String> availableStations = app.getAvailableStations();

            while (true) {
                System.out.println("\n=== MENU UTAMA ===");
                System.out.println("1. Cari rute KRL");
                System.out.println("2. Lihat Peta");
                System.out.println("3. Keluar Program");
                System.out.print("Pilih menu (1-3): ");
                String menuInput = scanner.nextLine().trim();

                if (menuInput.equals("1")) {
                    while (true) {
                        System.out.println("\nDaftar Stasiun:");
                        for (int i = 0; i < availableStations.size(); i++) {
                            System.out.printf("%3d. %s%n", i + 1, availableStations.get(i));
                        }
                        System.out.printf("%3d. Kembali ke Menu Utama%n", availableStations.size() + 1);
                        System.out.print("Pilih nomor stasiun AWAL (atau " + (availableStations.size() + 1)
                                + " untuk kembali): ");
                        int startStationNum;
                        try {
                            startStationNum = Integer.parseInt(scanner.nextLine().trim());
                        } catch (NumberFormatException e) {
                            System.out.println("Input tidak valid.");
                            continue;
                        }
                        if (startStationNum == availableStations.size() + 1)
                            break;
                        if (startStationNum < 1 || startStationNum > availableStations.size()) {
                            System.out.println("Nomor stasiun tidak valid.");
                            continue;
                        }
                        String startStation = availableStations.get(startStationNum - 1);

                        System.out.print("Pilih nomor stasiun TUJUAN (atau " + (availableStations.size() + 1)
                                + " untuk kembali): ");
                        int destStationNum;
                        try {
                            destStationNum = Integer.parseInt(scanner.nextLine().trim());
                        } catch (NumberFormatException e) {
                            System.out.println("Input tidak valid.");
                            continue;
                        }
                        if (destStationNum == availableStations.size() + 1)
                            break;
                        if (destStationNum < 1 || destStationNum > availableStations.size()) {
                            System.out.println("Nomor stasiun tidak valid.");
                            continue;
                        }
                        String destStation = availableStations.get(destStationNum - 1);

                        if (startStation.equals(destStation)) {
                            System.out.println("\nError: Stasiun awal dan tujuan tidak boleh sama.");
                            continue;
                        }

                        System.out.println("\nMencari rute dari '" + startStation + "' ke '" + destStation + "'...");
                        List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit(startStation, destStation,
                                simulatedCurrentTime, 3);

                        if (routes.isEmpty()) {
                            System.out.println("\nMaaf, tidak ditemukan rute kereta untuk pilihan Anda.");
                        } else {
                            System.out.println("\n--- Rute Kereta Tersedia ---");
                            int routeNum = 1;
                            for (List<Map<String, Object>> route : routes.subList(0, Math.min(3, routes.size()))) {
                                System.out.println("Rute #" + routeNum++);
                                System.out.printf("%-54s | %-12s | %-15s | %-12s%n", "Nama Kereta", "Berangkat", "Tiba",
                                        "Okupansi");
                                System.out.println("-".repeat(75));
                                int i = 0;
                                while (i < route.size()) {
                                    Map<String, Object> leg = route.get(i);
                                    String trainName = (String) leg.get("train_name");
                                    String startStationfromTransit = (String) leg.get("start_station");
                                    String departureTime = (String) leg.get("departure_time");
                                    String occupancyInfo = leg.get("occupancy_percentage") != null
                                            ? leg.get("occupancy_percentage") + "%"
                                            : "N/A";
                                    int j = i;
                                    while (j + 1 < route.size()
                                            && route.get(j + 1).get("train_name").equals(trainName)) {
                                        j++;
                                    }
                                    String endStation = (String) route.get(j).get("destination_station");
                                    String arrivalTime = (String) route.get(j).get("estimated_arrival");

                                    System.out.printf("%-54s | %-12s | %-15s | %-12s%n",
                                            trainName + " (" + startStationfromTransit + " - " + endStation + ")",
                                            departureTime,
                                            arrivalTime,
                                            occupancyInfo);

                                    i = j + 1;
                                }
                                System.out.println("-".repeat(75));
                            }
                        }
                        // Setelah selesai, kembali ke menu stasiun
                    }
                } else if (menuInput.equals("2")) {
                    showMapImage("Rute-KRL-1.png");
                    // Setelah lihat peta, kembali ke menu utama
                } else if (menuInput.equals("3")) {
                    System.out.println("Terima kasih telah menggunakan program ini.");
                    break;
                } else {
                    System.out.println("Pilihan tidak valid.");
                }
            }
            scanner.close();
        } catch (IOException e) {
            System.out.println("Failed to load train schedule: " + e.getMessage());
        } catch (Exception e) {
            System.out.println("\nTerjadi kesalahan: " + e.getMessage());
        }
    }
}
