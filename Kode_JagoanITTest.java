import org.junit.jupiter.api.*;
import java.io.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

// Kode_JagoanITTest.java
// Unit tests for Kode_JagoanIT.java



class Kode_JagoanITTest {

    private static final String TEST_CSV = "test_schedule.csv";

    @BeforeAll
    static void setupCSV() throws IOException {
        // Copy train_schedule.csv to test_schedule.csv
        String trainSchedulePath = "c:\\Users\\acer\\Downloads\\JagoanIT\\train_schedule.csv";
        try (
            BufferedReader br = new BufferedReader(new FileReader(trainSchedulePath));
            PrintWriter pw = new PrintWriter(TEST_CSV)
        ) {
            String line;
            while ((line = br.readLine()) != null) {
                pw.println(line);
            }
        }
    }

    static void cleanupCSV() {
        new File(TEST_CSV).delete();
    }

    @Test
    void testTrainConstructorAndGetters() {
        List<String> route = Arrays.asList("StationA", "StationB");
        Map<String, String> departureTimes = new HashMap<>();
        departureTimes.put("StationA", "10:00");
        departureTimes.put("StationB", "10:30");
        Train train = new Train("T001", "Test Train", route, departureTimes);

        assertEquals("T001", train.getId());
        assertEquals("Test Train", train.getName());
        assertEquals(route, train.getRoute());
        assertEquals(departureTimes, train.getDepartureTimes());
    }

    @Test
    void testTrainScheduleLoad() throws IOException {
        TrainSchedule schedule = new TrainSchedule(TEST_CSV);
        List<Train> trains = schedule.getTrains();
        assertEquals(2, trains.size());
        assertEquals("Depok - Jakarta Kota", trains.get(0).getName());
        assertTrue(trains.get(1).getRoute().contains("Bogor"));
    }

    @Test
    void testGetAllStations() throws IOException {
        TrainSchedule schedule = new TrainSchedule(TEST_CSV);
        Set<String> stations = schedule.getAllStations();
        assertTrue(stations.contains("Bogor"));
        assertTrue(stations.contains("Jakarta Kota"));
        assertTrue(stations.contains("Karet"));
        assertTrue(stations.contains("Bekasi"));
        assertEquals(43, stations.size()); // 43 unique stations in test CSV
    }

    @Test
    void testOccupancyPredictorMorningPeak() throws IOException {
        TrainSchedule schedule = new TrainSchedule(TEST_CSV);
        Train train = schedule.getTrains().get(1); // Use Bogor - Jakarta Kota
        LocalDateTime morning = LocalDateTime.of(2025, 6, 14, 6, 0);
        Map<String, Integer> occ = OccupancyPredictor.predict(train, morning);
        assertEquals(5, occ.get("Bogor"));
        assertEquals(75, occ.get("Pasar Minggu"));
        assertEquals(5, occ.get("Jakarta Kota"));
    }

    @Test
    void testOccupancyPredictorOffPeak() throws IOException {
        TrainSchedule schedule = new TrainSchedule(TEST_CSV);
        Train train = schedule.getTrains().get(1); // Use Bogor - Jakarta Kota
        LocalDateTime noon = LocalDateTime.of(2025, 6, 14, 12, 0);
        Map<String, Integer> occ = OccupancyPredictor.predict(train, noon);
        for (Integer v : occ.values()) {
            assertTrue(v >= 5 && v <= 98);
        }
    }

    @Test
    void testPredictRoutesDirect01() throws IOException {
        TrainSchedule schedule = new TrainSchedule(TEST_CSV);
        TrainSchedulePredictorApp app = new TrainSchedulePredictorApp(schedule);
        LocalDateTime time = LocalDateTime.of(2025, 6, 14, 5, 30);
        List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit("Bogor", "Jakarta Kota", time, 0);
        assertTrue(routes.isEmpty());
    }

    @Test
    void testPredictRoutesDirect02() throws IOException {
        TrainSchedule schedule = new TrainSchedule(TEST_CSV);
        TrainSchedulePredictorApp app = new TrainSchedulePredictorApp(schedule);
        LocalDateTime time = LocalDateTime.of(2025, 6, 14, 7, 0);
        List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit("Jakarta Kota", "Bogor", time, 1);
        assertTrue(routes.isEmpty());
    }

    @Test
    void testPredictRoutesDirect03() throws IOException {
        TrainSchedule schedule = new TrainSchedule(TEST_CSV);
        TrainSchedulePredictorApp app = new TrainSchedulePredictorApp(schedule);
        LocalDateTime time = LocalDateTime.of(2025, 6, 14, 7, 0);
        List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit("Tangerang", "Duri", time, 1);
        assertTrue(routes.isEmpty());
    }

    @Test
    void testPredictRoutesDirect04() throws IOException {
        TrainSchedule schedule = new TrainSchedule(TEST_CSV);
        TrainSchedulePredictorApp app = new TrainSchedulePredictorApp(schedule);
        LocalDateTime time = LocalDateTime.of(2025, 6, 14, 7, 0);
        List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit("Kampung Bandan", "Bekasi", time, 1);
        assertTrue(routes.isEmpty());
    }

    @Test
    void testPredictRoutesWithOneTransit() throws IOException {
        TrainSchedule schedule = new TrainSchedule(TEST_CSV);
        TrainSchedulePredictorApp app = new TrainSchedulePredictorApp(schedule);
        LocalDateTime time = LocalDateTime.of(2025, 6, 14, 7, 0);
        List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit("Pondok Cina", "Bekasi", time, 2);
        assertFalse(routes.isEmpty());
    }

    @Test
    void testNoRouteFound() throws IOException {
        TrainSchedule schedule = new TrainSchedule(TEST_CSV);
        TrainSchedulePredictorApp app = new TrainSchedulePredictorApp(schedule);
        LocalDateTime time = LocalDateTime.of(2025, 6, 14, 5, 30);
        List<List<Map<String, Object>>> routes = app.predictRoutesWithTransit("Bogor", "Nonexistent", time, 1);
        assertTrue(routes.isEmpty());
    }

    @Test
    void testReadTrainScheduleCSV() throws IOException {
        String csvPath = "c:\\Users\\acer\\Downloads\\JagoanIT\\train_schedule.csv";
        TrainSchedule schedule = new TrainSchedule(csvPath);
        List<Train> trains = schedule.getTrains();
        assertFalse(trains.isEmpty());
        // Optionally, check for a known train
        assertTrue(trains.stream().anyMatch(t -> t.getName().contains("Depok")));
        // Optionally, check for a known station
        Set<String> stations = schedule.getAllStations();
        assertTrue(stations.contains("Bogor"));
    }
}