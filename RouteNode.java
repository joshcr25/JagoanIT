import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class RouteNode {
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