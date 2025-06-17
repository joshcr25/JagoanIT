import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Train {
    private final String id;
    private final String name;
    private final List<String> route;
    private final Map<String, String> departureTimes;

    public Train() {
        this.id = "";
        this.name = "";
        this.route = new ArrayList<>();
        this.departureTimes = new HashMap<>();
    }

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