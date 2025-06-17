import java.time.DayOfWeek;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class OccupancyPredictor {
    public enum Line {
        BOGOR, CIKARANG, RANGKASBITUNG, TANGERANG, TANJUNG_PRIOK, UNKNOWN
    }

    private enum Direction {
        MENUJU_JAKARTA, MENUJU_BOGOR, MENUJU_CIKARANG, MENUJU_RANGKASBITUNG, MENUJU_TANGERANG, DUA_ARAH, UNKNOWN
    }

    private enum TimePeriod {
        PUNCAK_PAGI, SIANG, PUNCAK_SORE, MALAM, AKHIR_PEKAN
    }

    private static final Map<Line, Map<Direction, Map<TimePeriod, Integer>>> occupancyMatrix = new HashMap<>();

    static {
        java.util.function.Function<String, Integer> avg = rangeStr -> {
            String[] parts = rangeStr.replaceAll("[^0-9\\-]", "").split("-");
            if (parts.length == 1)
                return Integer.parseInt(parts[0]);
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

    public static String normalizeStation(String name) {
        if (name == null)
            return "";
        return name.split("\\(")[0].trim(); // Menghapus bagian dalam kurung
    }

    public static Line getLine(List<String> route) {
        Set<String> routeSet = new HashSet<>();
        for (String station : route)
            routeSet.add(normalizeStation(station));
        if (routeSet.contains("bekasi") || routeSet.contains("cikarang") || routeSet.contains("tambun"))
            return Line.CIKARANG;
        if (routeSet.contains("parung panjang") || routeSet.contains("serpong") || routeSet.contains("rangkasbitung")
                || routeSet.contains("kebayoran"))
            return Line.RANGKASBITUNG;
        if (routeSet.contains("rawa buaya") || routeSet.contains("batu ceper") || routeSet.contains("tangerang"))
            return Line.TANGERANG;
        if (routeSet.contains("ancol") || routeSet.contains("tanjung priok"))
            return Line.TANJUNG_PRIOK;
        if (routeSet.contains("depok") || routeSet.contains("citayam") || routeSet.contains("bogor")
                || routeSet.contains("tebet"))
            return Line.BOGOR;
        return Line.UNKNOWN;
    }

    public static Direction getDirection(List<String> route) {
        if (route == null || route.size() < 2)
            return Direction.UNKNOWN;
        String first = normalizeStation(route.get(0));
        String last = normalizeStation(route.get(route.size() - 1));
        if (first.contains("tanjung priok") || last.contains("tanjung priok"))
            return Direction.DUA_ARAH;
        if (last.contains("jakarta") || last.contains("duri") || last.contains("angke") || last.contains("tanah abang"))
            return Direction.MENUJU_JAKARTA;
        if (last.contains("bogor") || last.contains("nambo"))
            return Direction.MENUJU_BOGOR;
        if (last.contains("cikarang"))
            return Direction.MENUJU_CIKARANG;
        if (last.contains("rangkasbitung") || last.contains("parung panjang") || last.contains("serpong"))
            return Direction.MENUJU_RANGKASBITUNG;
        if (last.contains("tangerang"))
            return Direction.MENUJU_TANGERANG;
        return Direction.UNKNOWN;
    }

    public static TimePeriod getTimePeriod(LocalDateTime dateTime) {
        DayOfWeek day = dateTime.getDayOfWeek();
        if (day == DayOfWeek.SATURDAY || day == DayOfWeek.SUNDAY)
            return TimePeriod.AKHIR_PEKAN;
        LocalTime time = dateTime.toLocalTime();
        if (!time.isBefore(MORNING_PEAK_START) && time.isBefore(MORNING_PEAK_END))
            return TimePeriod.PUNCAK_PAGI;
        if (!time.isBefore(DAYTIME_START) && time.isBefore(DAYTIME_END))
            return TimePeriod.SIANG;
        if (!time.isBefore(EVENING_PEAK_START) && time.isBefore(EVENING_PEAK_END))
            return TimePeriod.PUNCAK_SORE;
        return TimePeriod.MALAM;
    }

    public static Map<String, Integer> predict(Train train, LocalDateTime currentTime) {
        Map<String, Integer> occupancyMap = new HashMap<>();
        List<String> route = train.getRoute();
        if (route == null || route.isEmpty())
            return occupancyMap;
        Line line = getLine(route);
        Direction direction = getDirection(route);
        TimePeriod period = getTimePeriod(currentTime);
        int occupancy = occupancyMatrix
                .getOrDefault(line, Collections.emptyMap())
                .getOrDefault(direction, Collections.emptyMap())
                .getOrDefault(period, DEFAULT_OCCUPANCY);
        int finalOccupancy = Math.max(MIN_OCCUPANCY, Math.min(occupancy, MAX_OCCUPANCY));
        for (String station : route)
            occupancyMap.put(station, finalOccupancy);
        return occupancyMap;
    }
}