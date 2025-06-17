import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Collections;
import java.util.Arrays;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class TrainSchedule {
    private final List<Train> trains;
    // --- PERUBAHAN 1: Tambahkan Map untuk pencarian stasiun yang efisien ---
    private final Map<String, List<Train>> stationToTrainsMap;

    public TrainSchedule() {
        this.trains = new ArrayList<>();
        this.stationToTrainsMap = new HashMap<>();
    }

    public TrainSchedule(String csvFile) throws IOException {
        this.trains = loadFromCSV(csvFile);
        // --- PERUBAHAN 2: Panggil method untuk membangun Map setelah jadwal dimuat ---
        this.stationToTrainsMap = buildStationToTrainsMap();
    }

    // Method loadFromCSV tetap sama persis...
    public List<Train> loadFromCSV(String filename) throws IOException {
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

    // --- PERUBAHAN 3: Method baru untuk membangun Map ---
    public Map<String, List<Train>> buildStationToTrainsMap() {
        Map<String, List<Train>> map = new HashMap<>();
        for (Train train : trains) {
            for (String station : train.getRoute()) {
                // computeIfAbsent memastikan kita hanya membuat ArrayList baru jika belum ada
                map.computeIfAbsent(station, k -> new ArrayList<>()).add(train);
            }
        }
        return map;
    }

    public List<Train> getTrains() {
        return trains;
    }

    // --- PERUBAHAN 4: Method getter untuk Map agar bisa diakses oleh PredictorApp
    // ---
    public List<Train> getTrainsForStation(String station) {
        return stationToTrainsMap.getOrDefault(station, Collections.emptyList());
    }

    public Set<String> getAllStations() {
        // Diambil dari keyset map agar lebih cepat
        return stationToTrainsMap.keySet();
    }
}