import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

public class Kode_JagoanIT {

    private static List<Map<String, Object>> TRAIN_SCHEDULE_DATA;

    static {
        try {
            TRAIN_SCHEDULE_DATA = loadTrainScheduleFromCSV("train_schedule.csv");
        } catch (IOException e) {
            e.printStackTrace();
            TRAIN_SCHEDULE_DATA = new ArrayList<>(); // Initialize as empty if loading fails
        }
    }

    /**
     * Loads train schedule data from a specified CSV file.
     *
     * @param filename The path to the CSV file.
     * @return A list of maps, where each map represents a train's data.
     * @throws IOException If an I/O error occurs reading from the file.
     */
    public static List<Map<String, Object>> loadTrainScheduleFromCSV(String filename) throws IOException {
        List<Map<String, Object>> schedule = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
            String line;
            br.readLine(); // Skip header row
            while ((line = br.readLine()) != null) {
                String[] values = line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1); // Regex to handle commas within quotes

                Map<String, Object> trainData = new HashMap<>();
                trainData.put("train_id", values[0]);
                trainData.put("train_name", values[1]);
                trainData.put("route", Arrays.asList(values[2].replace("\"", "").split(",")));

                Map<String, String> departureTimes = new HashMap<>();
                String[] times = values[3].replace("\"", "").split(",");
                for (String time : times) {
                    String[] parts = time.split(":");
                    departureTimes.put(parts[0], parts[1] + ":" + parts[2]);
                }
                trainData.put("departure_times", departureTimes);

                schedule.add(trainData);
            }
        }
        return schedule;
    }

    // --- Konstanta untuk Logika Prediksi Keterisian (Linear Model Fallback) ---
    private static final double BASE_OCCUPANCY = 15.0;
    private static final double INCREASE_FACTOR_PER_MINUTE = 0.8;
    private static final double END_OF_ROUTE_DRAIN_FACTOR = 30.0;

    // --- Konstanta Umum Keterisian ---
    private static final int MIN_OCCUPANCY = 5;
    private static final int MAX_OCCUPANCY = 98;


    /**
     * Menghitung prediksi persentase keterisian di setiap stasiun pada rute.
     * Logika ini telah direfaktor untuk menggunakan model parabola yang lebih realistis,
     * dengan asumsi puncak keterisian terjadi di Stasiun Manggarai.
     *
     * @param train Data kereta termasuk rute dan jadwal.
     * @return Map berisi pasangan stasiun dan persentase keterisiannya.
     */
    private static Map<String, Integer> calculateOccupancy(Map<String, Object> train) {
        @SuppressWarnings("unchecked")
        List<String> route = (List<String>) train.get("route");
        Map<String, Integer> occupancyMap = new HashMap<>();

        if (route == null || route.isEmpty()) {
            return occupancyMap;
        }

        // --- REFACTORED LOGIC: Parabolic Occupancy Model ---
        // Model ini mengasumsikan keterisian puncak berada di Stasiun Manggarai (83%)
        // dan mengikuti kurva parabola (a < 0), sesuai dengan permintaan.

        final String PEAK_STATION = "Manggarai";
        final double PEAK_OCCUPANCY = 83.0; // Keterisian puncak di Manggarai 83%
        final double INITIAL_OCCUPANCY = 15.0; // Keterisian awal di stasiun pertama

        int peakIndex = route.indexOf(PEAK_STATION);

        // --- Fallback ke model linear jika stasiun puncak tidak ada di rute ---
        if (peakIndex == -1) {
            // (Menggunakan logika linear original sebagai fallback)
            @SuppressWarnings("unchecked")
            Map<String, String> departureTimes = (Map<String, String>) train.get("departure_times");
            if (route.size() < 2 || departureTimes == null) {
                if (!route.isEmpty()) occupancyMap.put(route.get(0), (int) INITIAL_OCCUPANCY);
                return occupancyMap;
            }

            double currentOccupancy = BASE_OCCUPANCY;
            occupancyMap.put(route.get(0), (int) currentOccupancy);

            for (int i = 1; i < route.size(); i++) {
                String prevStation = route.get(i - 1);
                String currentStation = route.get(i);

                if (!departureTimes.containsKey(prevStation) || !departureTimes.containsKey(currentStation)) {
                    occupancyMap.put(currentStation, (int) currentOccupancy);
                    continue;
                }

                LocalTime prevTime = LocalTime.parse(departureTimes.get(prevStation));
                LocalTime currentTime = LocalTime.parse(departureTimes.get(currentStation));

                long travelMinutes = Duration.between(prevTime, currentTime).toMinutes();
                double occupancyIncrease = travelMinutes * INCREASE_FACTOR_PER_MINUTE;
                double progressRatio = (double) i / (route.size() - 1);
                double occupancyDecrease = progressRatio * (END_OF_ROUTE_DRAIN_FACTOR / route.size());

                currentOccupancy += occupancyIncrease - occupancyDecrease;
                currentOccupancy = Math.max(MIN_OCCUPANCY, Math.min(MAX_OCCUPANCY, currentOccupancy));

                occupancyMap.put(currentStation, (int) currentOccupancy);
            }
            return occupancyMap;
        }

        // --- Kalkulasi Model Parabola ---
        // Persamaan parabola: y = a(x - h)^2 + k
        // y = keterisian, x = indeks stasiun
        // (h, k) = titik puncak (peakIndex, PEAK_OCCUPANCY)

        double h = peakIndex;
        double k = PEAK_OCCUPANCY;

        // Hitung koefisien 'a' (kelengkungan parabola)
        // Gunakan stasiun pertama (indeks 0) dengan keterisian awal untuk menemukan 'a'.
        // a = (y - k) / (x - h)^2
        double a;
        if (h == 0) {
            // Jika rute dimulai dari stasiun puncak, gunakan nilai default
            a = -0.5;
        } else {
            a = (INITIAL_OCCUPANCY - k) / (Math.pow(0 - h, 2));
        }

        // Hitung keterisian untuk setiap stasiun di rute
        for (int i = 0; i < route.size(); i++) {
            String currentStation = route.get(i);
            double x = i;

            // y = a(x - h)^2 + k
            double calculatedOccupancy = a * Math.pow(x - h, 2) + k;

            // Pastikan nilai berada dalam rentang MIN dan MAX
            int finalOccupancy = (int) Math.max(MIN_OCCUPANCY, Math.min(MAX_OCCUPANCY, calculatedOccupancy));

            occupancyMap.put(currentStation, finalOccupancy);
        }

        return occupancyMap;
    }


    // --- Core Prediction Logic ---
    public static List<Map<String, Object>> predictNextTrains(String startStation, String destStation,
            LocalDateTime currentTime) {
        List<Map<String, Object>> predictions = new ArrayList<>();

        for (Map<String, Object> train : TRAIN_SCHEDULE_DATA) {
            @SuppressWarnings("unchecked")
            List<String> route = (List<String>) train.get("route");

            if (route.contains(startStation) && route.contains(destStation)) {
                int startIndex = route.indexOf(startStation);
                int destIndex = route.indexOf(destStation);

                if (startIndex < destIndex) {
                    @SuppressWarnings("unchecked")
                    Map<String, String> departureTimes = (Map<String, String>) train.get("departure_times");
                    String departureTimeStr = departureTimes.get(startStation);

                    if (departureTimeStr == null) {
                        continue;
                    }

                    LocalDateTime departureDateTime = currentTime.toLocalDate().atTime(LocalTime.parse(departureTimeStr));

                    if (departureDateTime.isAfter(currentTime)) {
                        String destArrivalTimeStr = departureTimes.get(destStation);
                        if (destArrivalTimeStr == null) {
                            continue;
                        }

                        LocalDateTime arrivalDateTime = currentTime.toLocalDate().atTime(LocalTime.parse(destArrivalTimeStr));

                        // Hitung keterisian dan tambahkan ke data prediksi
                        Map<String, Integer> occupancyData = calculateOccupancy(train);
                        Integer occupancyAtStart = occupancyData.get(startStation);


                        Map<String, Object> prediction = new HashMap<>();
                        prediction.put("train_id", train.get("train_id"));
                        prediction.put("train_name", train.get("train_name"));
                        prediction.put("start_station", startStation);
                        prediction.put("destination_station", destStation);
                        prediction.put("departure_time",
                                departureDateTime.format(DateTimeFormatter.ofPattern("HH:mm")));
                        prediction.put("estimated_arrival",
                                arrivalDateTime.format(DateTimeFormatter.ofPattern("HH:mm")));
                        prediction.put("_departure_dt", departureDateTime);
                        prediction.put("occupancy_percentage", occupancyAtStart);

                        predictions.add(prediction);
                    }
                }
            }
        }

        // Sort predictions by departure time
        predictions.sort(Comparator.comparing(p -> (LocalDateTime) p.get("_departure_dt")));

        return predictions;
    }

    public static List<String> getAvailableStations() {
        Set<String> stations = new HashSet<>();
        for (Map<String, Object> train : TRAIN_SCHEDULE_DATA) {
            @SuppressWarnings("unchecked")
            List<String> route = (List<String>) train.get("route");
            stations.addAll(route);
        }
        List<String> sortedStations = new ArrayList<>(stations);
        Collections.sort(sortedStations);
        return sortedStations;
    }

    // --- Main Application ---
    public static void main(String[] args) {
        LocalDateTime simulatedCurrentTime = LocalDateTime.of(2025, 6, 14, 4, 30);
        Scanner scanner = new Scanner(System.in);

        System.out.println("--- Train Schedule Predictor ---");
        System.out.println("Current Time (Simulated): "
                + simulatedCurrentTime.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")) + "\n");

        List<String> availableStations = getAvailableStations();
        System.out.println("Available Stations:");
        for (int i = 0; i < availableStations.size(); i++) {
            System.out.println("  " + (i + 1) + ". " + availableStations.get(i));
        }
        System.out.println("-".repeat(30));

        try {
            System.out.print("Enter the number for your START station: ");
            int startStationNum = scanner.nextInt();
            System.out.print("Enter the number for your DESTINATION station: ");
            int destStationNum = scanner.nextInt();

            String startStation = availableStations.get(startStationNum - 1);
            String destStation = availableStations.get(destStationNum - 1);

            if (startStation.equals(destStation)) {
                System.out.println("\nError: Start and destination stations cannot be the same.");
                return;
            }

            System.out.println("\nSearching for trains from '" + startStation + "' to '" + destStation + "'...");

            List<Map<String, Object>> predictions = predictNextTrains(startStation, destStation, simulatedCurrentTime);

            if (predictions.isEmpty()) {
                System.out.println("\nSorry, no upcoming trains found for your selected route.");
            } else {
                System.out.println("\n--- Upcoming Train Schedule ---");
                System.out.printf("%-25s | %-12s | %-15s | %-12s%n", "Train Name", "Departs At", "Est. Arrival", "Occupancy");
                System.out.println("-".repeat(75));

                for (Map<String, Object> train : predictions) {
                    String occupancyInfo = train.get("occupancy_percentage") != null ? train.get("occupancy_percentage") + "%" : "N/A";
                    System.out.printf("%-25s | %-12s | %-15s | %-12s%n",
                            train.get("train_name"),
                            train.get("departure_time"),
                            train.get("estimated_arrival"),
                            occupancyInfo);
                }
                System.out.println("-".repeat(75));
            }

        } catch (InputMismatchException | IndexOutOfBoundsException e) {
            System.out.println("\nInvalid input. Please enter a valid number from the list.");
        } finally {
            scanner.close();
        }
    }
}