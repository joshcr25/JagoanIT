import java.io.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;

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
    private static final double BASE_OCCUPANCY = 15.0;
    private static final double INCREASE_FACTOR_PER_MINUTE = 0.8;
    private static final double END_OF_ROUTE_DRAIN_FACTOR = 30.0;
    private static final int MIN_OCCUPANCY = 5;
    private static final int MAX_OCCUPANCY = 98;

    public static Map<String, Integer> predict(Train train) {
        List<String> route = train.getRoute();
        Map<String, Integer> occupancyMap = new HashMap<>();
        if (route == null || route.isEmpty())
            return occupancyMap;

        final String PEAK_STATION = "Manggarai";
        final double PEAK_OCCUPANCY = 83.0;
        final double INITIAL_OCCUPANCY = 15.0;
        int peakIndex = route.indexOf(PEAK_STATION);

        if (peakIndex == -1) {
            // Linear fallback
            Map<String, String> departureTimes = train.getDepartureTimes();
            if (route.size() < 2 || departureTimes == null) {
                if (!route.isEmpty())
                    occupancyMap.put(route.get(0), (int) INITIAL_OCCUPANCY);
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

        // Parabolic model
        double h = peakIndex;
        double k = PEAK_OCCUPANCY;
        double a = (h == 0) ? -0.5 : (INITIAL_OCCUPANCY - k) / (Math.pow(0 - h, 2));
        for (int i = 0; i < route.size(); i++) {
            String currentStation = route.get(i);
            double x = i;
            double calculatedOccupancy = a * Math.pow(x - h, 2) + k;
            int finalOccupancy = (int) Math.max(MIN_OCCUPANCY, Math.min(MAX_OCCUPANCY, calculatedOccupancy));
            occupancyMap.put(currentStation, finalOccupancy);
        }
        return occupancyMap;
    }
}

class TrainSchedulePredictorApp {
    private final TrainSchedule schedule;
    private long bestDuration = Long.MAX_VALUE;
    private int maxResultCount = 3;

    public TrainSchedulePredictorApp(TrainSchedule schedule) {
        this.schedule = schedule;
    }

    public List<List<Map<String, Object>>> predictRoutesWithTransit(
            String startStation, String destStation, LocalDateTime currentTime, int maxTransit) {
        List<List<Map<String, Object>>> results = new ArrayList<>();
        Set<String> visited = new HashSet<>();
        bestDuration = Long.MAX_VALUE;
        dfsFindRoutes(startStation, destStation, currentTime, maxTransit, new ArrayList<>(), results, visited, 0);
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

    private void dfsFindRoutes(
            String currentStation, String destStation, LocalDateTime currentTime, int remainingTransit,
            List<Map<String, Object>> currentRoute, List<List<Map<String, Object>>> results, Set<String> visited,
            long currentDuration) {
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

            for (int i = startIdx + 1; i < route.size(); i++) {
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

                // Prune jika sudah lebih lama dari bestDuration
                if (newDuration > bestDuration)
                    continue;

                Map<String, Integer> occupancyData = OccupancyPredictor.predict(train);
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
                            results, new HashSet<>(visited), newDuration);
                }
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
            LocalDateTime simulatedCurrentTime = LocalDateTime.of(2025, 6, 14, 4, 30);
            Scanner scanner = new Scanner(System.in);

            System.out.println("--- Train Schedule Predictor ---");
            System.out.println("Current Time (Simulated): "
                    + simulatedCurrentTime.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")) + "\n");

            List<String> availableStations = app.getAvailableStations();
            System.out.println("Available Stations:");
            for (int i = 0; i < availableStations.size(); i++) {
                System.out.println("  " + (i + 1) + ". " + availableStations.get(i));
            }
            System.out.println("-".repeat(30));

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

            // --- Ganti ke pencarian multi-transit ---
            List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit(startStation, destStation,
                    simulatedCurrentTime, 3);

            if (routes.isEmpty()) {
                System.out.println("\nSorry, no upcoming trains found for your selected route.");
            } else {
                System.out.println("\n--- Upcoming Train Route(s) ---");
                int routeNum = 1;
                for (List<Map<String, Object>> route : routes.subList(0, Math.min(3, routes.size()))) { // tampilkan max
                                                                                                        // 3 rute
                                                                                                        // efisien
                    System.out.println("Route #" + routeNum++);
                    System.out.printf("%-40s | %-12s | %-15s | %-12s%n", "Train Name", "Departs At", "Est. Arrival",
                            "Occupancy");
                    System.out.println("-".repeat(75));
                    for (Map<String, Object> leg : route) {
                        String occupancyInfo = leg.get("occupancy_percentage") != null
                                ? leg.get("occupancy_percentage") + "%"
                                : "N/A";
                        System.out.printf("%-40s | %-12s | %-15s | %-12s%n",
                                leg.get("train_name"),
                                leg.get("departure_time"),
                                leg.get("estimated_arrival"),
                                occupancyInfo);
                    }
                    System.out.println("-".repeat(75));
                }
            }
            scanner.close();
        } catch (IOException e) {
            System.out.println("Failed to load train schedule: " + e.getMessage());
        } catch (InputMismatchException | IndexOutOfBoundsException e) {
            System.out.println("\nInvalid input. Please enter a valid number from the list.");
        }
    }
}
