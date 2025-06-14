import java.time.Duration;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

public class Kode_JagoanIT {

    // --- Simulated Train Data ---
    // (TRAIN_SCHEDULE_DATA remains the same as in your original code)
    private static final List<Map<String, Object>> TRAIN_SCHEDULE_DATA = Arrays.asList(
            new HashMap<String, Object>() {
                {
                    // --- Commuter Line Bogor, Bogor to Jakarta Kota & Bogor to Manggarai (Red
                    // line)
                    put("train_id", "1157");
                    put("train_name", "Commuter Line Bogor");
                    put("route",
                            Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar",
                                    "Mangga Besar", "Jayakarta", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "04:03");
                            put("Cilebut", "04:12");
                            put("Bojonggede", "04:18");
                            put("Citayam", "04:24");
                            put("Depok", "04:30");
                            put("Depok Baru", "04:34");
                            put("Pondok Cina", "04:36");
                            put("Univ. Indonesia", "04:40");
                            put("Univ. Pancasila", "04:42");
                            put("Lenteng Agung", "04:43");
                            put("Tanjung Barat", "04:45");
                            put("Pasar Minggu", "04:53");
                            put("Pasar Minggu Baru", "04:55");
                            put("Duren Kalibata", "04:56");
                            put("Cawang", "04:57");
                            put("Tebet", "04:58");
                            put("Manggarai", "05:06");
                            put("Cikini", "05:08");
                            put("Gondangdia", "05:10");
                            put("Juanda", "05:18");
                            put("Sawah Besar", "05:19");
                            put("Mangga Besar", "05:20");
                            put("Jayakarta", "05:25");
                            put("Jakarta Kota", "05:28");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1001");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                            "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung", "Tanjung Barat",
                            "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang", "Tebet", "Manggarai"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "04:13");
                            put("Cilebut", "04:22");
                            put("Bojonggede", "04:28");
                            put("Citayam", "04:34");
                            put("Depok", "04:40");
                            put("Depok Baru", "04:44");
                            put("Pondok Cina", "04:46");
                            put("Univ. Indonesia", "04:50");
                            put("Univ. Pancasila", "04:52");
                            put("Lenteng Agung", "04:53");
                            put("Tanjung Barat", "04:55");
                            put("Pasar Minggu", "05:03");
                            put("Pasar Minggu Baru", "05:05");
                            put("Duren Kalibata", "05:06");
                            put("Cawang", "05:07");
                            put("Tebet", "05:08");
                            put("Manggarai", "05:16");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1161");
                    put("train_name", "Commuter Line Bogor");
                    put("route",
                            Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar",
                                    "Mangga Besar", "Jayakarta", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "04:28");
                            put("Cilebut", "04:37");
                            put("Bojonggede", "04:43");
                            put("Citayam", "04:49");
                            put("Depok", "04:55");
                            put("Depok Baru", "04:59");
                            put("Pondok Cina", "05:01");
                            put("Univ. Indonesia", "05:05");
                            put("Univ. Pancasila", "05:07");
                            put("Lenteng Agung", "05:08");
                            put("Tanjung Barat", "05:10");
                            put("Pasar Minggu", "05:18");
                            put("Pasar Minggu Baru", "05:20");
                            put("Duren Kalibata", "05:21");
                            put("Cawang", "05:22");
                            put("Tebet", "05:23");
                            put("Manggarai", "05:31");
                            put("Cikini", "05:33");
                            put("Gondangdia", "05:35");
                            put("Juanda", "05:43");
                            put("Sawah Besar", "05:44");
                            put("Mangga Besar", "05:45");
                            put("Jayakarta", "05:51");
                            put("Jakarta Kota", "05:54");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1169");
                    put("train_name", "Commuter Line Bogor");
                    put("route",
                            Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar",
                                    "Mangga Besar", "Jayakarta", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "04:38");
                            put("Cilebut", "04:47");
                            put("Bojonggede", "04:53");
                            put("Citayam", "04:59");
                            put("Depok", "05:05");
                            put("Depok Baru", "05:09");
                            put("Pondok Cina", "05:11");
                            put("Univ. Indonesia", "05:15");
                            put("Univ. Pancasila", "05:17");
                            put("Lenteng Agung", "05:18");
                            put("Tanjung Barat", "05:20");
                            put("Pasar Minggu", "05:28");
                            put("Pasar Minggu Baru", "05:30");
                            put("Duren Kalibata", "05:31");
                            put("Cawang", "05:32");
                            put("Tebet", "05:33");
                            put("Manggarai", "05:42");
                            put("Cikini", "05:44");
                            put("Gondangdia", "05:46");
                            put("Juanda", "05:54");
                            put("Sawah Besar", "05:55");
                            put("Mangga Besar", "05:56");
                            put("Jayakarta", "06:02");
                            put("Jakarta Kota", "06:05");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1003");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                            "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung", "Tanjung Barat",
                            "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang", "Tebet", "Manggarai"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "04:42");
                            put("Cilebut", "04:51");
                            put("Bojonggede", "04:57");
                            put("Citayam", "05:03");
                            put("Depok", "05:09");
                            put("Depok Baru", "05:13");
                            put("Pondok Cina", "05:15");
                            put("Univ. Indonesia", "05:20");
                            put("Univ. Pancasila", "05:22");
                            put("Lenteng Agung", "05:23");
                            put("Tanjung Barat", "05:25");
                            put("Pasar Minggu", "05:33");
                            put("Pasar Minggu Baru", "05:35");
                            put("Duren Kalibata", "05:36");
                            put("Cawang", "05:37");
                            put("Tebet", "05:38");
                            put("Manggarai", "05:46");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1171");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar",
                                    "Mangga Besar", "Jayakarta", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "04:48");
                            put("Cilebut", "04:57");
                            put("Bojonggede", "05:03");
                            put("Citayam", "05:09");
                            put("Depok", "05:15");
                            put("Depok Baru", "05:19");
                            put("Pondok Cina", "05:21");
                            put("Univ. Indonesia", "05:25");
                            put("Univ. Pancasila", "05:27");
                            put("Lenteng Agung", "05:28");
                            put("Tanjung Barat", "05:30");
                            put("Pasar Minggu", "05:38");
                            put("Pasar Minggu Baru", "05:40");
                            put("Duren Kalibata", "05:41");
                            put("Cawang", "05:42");
                            put("Tebet", "05:43");
                            put("Manggarai", "05:51");
                            put("Cikini", "05:53");
                            put("Gondangdia", "05:56");
                            put("Juanda", "06:03");
                            put("Sawah Besar", "06:04");
                            put("Mangga Besar", "06:05");
                            put("Jayakarta", "06:12");
                            put("Jakarta Kota", "06:15");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1173");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar",
                                    "Mangga Besar", "Jayakarta", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "04:53");
                            put("Cilebut", "05:02");
                            put("Bojonggede", "05:08");
                            put("Citayam", "05:14");
                            put("Depok", "05:20");
                            put("Depok Baru", "05:24");
                            put("Pondok Cina", "05:26");
                            put("Univ. Indonesia", "05:30");
                            put("Univ. Pancasila", "05:32");
                            put("Lenteng Agung", "05:33");
                            put("Tanjung Barat", "05:35");
                            put("Pasar Minggu", "05:43");
                            put("Pasar Minggu Baru", "05:45");
                            put("Duren Kalibata", "05:46");
                            put("Cawang", "05:47");
                            put("Tebet", "05:48");
                            put("Manggarai", "05:57");
                            put("Cikini", "05:59");
                            put("Gondangdia", "06:01");
                            put("Juanda", "06:09");
                            put("Sawah Besar", "06:10");
                            put("Mangga Besar", "06:11");
                            put("Jayakarta", "06:17");
                            put("Jakarta Kota", "06:20");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1175");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar",
                                    "Mangga Besar", "Jayakarta", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "05:03");
                            put("Cilebut", "05:12");
                            put("Bojonggede", "05:18");
                            put("Citayam", "05:24");
                            put("Depok", "05:30");
                            put("Depok Baru", "05:34");
                            put("Pondok Cina", "05:36");
                            put("Univ. Indonesia", "05:40");
                            put("Univ. Pancasila", "05:42");
                            put("Lenteng Agung", "05:43");
                            put("Tanjung Barat", "05:45");
                            put("Pasar Minggu", "05:53");
                            put("Pasar Minggu Baru", "05:55");
                            put("Duren Kalibata", "05:56");
                            put("Cawang", "05:57");
                            put("Tebet", "05:58");
                            put("Manggarai", "06:06");
                            put("Cikini", "06:08");
                            put("Gondangdia", "06:10");
                            put("Juanda", "06:18");
                            put("Sawah Besar", "06:19");
                            put("Mangga Besar", "06:20");
                            put("Jayakarta", "06:27");
                            put("Jakarta Kota", "06:30");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1177");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar",
                                    "Mangga Besar", "Jayakarta", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "05:09");
                            put("Cilebut", "05:18");
                            put("Bojonggede", "05:24");
                            put("Citayam", "05:30");
                            put("Depok", "05:36");
                            put("Depok Baru", "05:40");
                            put("Pondok Cina", "05:42");
                            put("Univ. Indonesia", "05:46");
                            put("Univ. Pancasila", "05:48");
                            put("Lenteng Agung", "05:49");
                            put("Tanjung Barat", "05:51");
                            put("Pasar Minggu", "05:59");
                            put("Pasar Minggu Baru", "06:01");
                            put("Duren Kalibata", "06:02");
                            put("Cawang", "06:03");
                            put("Tebet", "06:04");
                            put("Manggarai", "06:13");
                            put("Cikini", "06:15");
                            put("Gondangdia", "06:17");
                            put("Juanda", "06:25");
                            put("Sawah Besar", "06:26");
                            put("Mangga Besar", "06:27");
                            put("Jayakarta", "06:33");
                            put("Jakarta Kota", "06:36");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1005");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                            "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung", "Tanjung Barat",
                            "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang", "Tebet", "Manggarai"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "05:13");
                            put("Cilebut", "05:22");
                            put("Bojonggede", "05:28");
                            put("Citayam", "05:34");
                            put("Depok", "05:40");
                            put("Depok Baru", "05:44");
                            put("Pondok Cina", "05:46");
                            put("Univ. Indonesia", "05:50");
                            put("Univ. Pancasila", "05:52");
                            put("Lenteng Agung", "05:53");
                            put("Tanjung Barat", "05:55");
                            put("Pasar Minggu", "06:03");
                            put("Pasar Minggu Baru", "06:05");
                            put("Duren Kalibata", "06:06");
                            put("Cawang", "06:07");
                            put("Tebet", "06:08");
                            put("Manggarai", "06:16");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1179");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar",
                                    "Mangga Besar", "Jayakarta", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "05:18");
                            put("Cilebut", "05:27");
                            put("Bojonggede", "05:33");
                            put("Citayam", "05:39");
                            put("Depok", "05:45");
                            put("Depok Baru", "05:49");
                            put("Pondok Cina", "05:51");
                            put("Univ. Indonesia", "05:55");
                            put("Univ. Pancasila", "05:57");
                            put("Lenteng Agung", "05:58");
                            put("Tanjung Barat", "06:00");
                            put("Pasar Minggu", "06:08");
                            put("Pasar Minggu Baru", "06:10");
                            put("Duren Kalibata", "06:11");
                            put("Cawang", "06:12");
                            put("Tebet", "06:13");
                            put("Manggarai", "06:21");
                            put("Cikini", "06:23");
                            put("Gondangdia", "06:25");
                            put("Juanda", "06:33");
                            put("Sawah Besar", "06:34");
                            put("Mangga Besar", "06:35");
                            put("Jayakarta", "06:41");
                            put("Jakarta Kota", "06:44");
                        }
                    });
                }
            },new HashMap<String, Object>() {
                {
                    put("train_id", "1183");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar",
                                    "Mangga Besar", "Jayakarta", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "05:28");
                            put("Cilebut", "05:37");
                            put("Bojonggede", "05:43");
                            put("Citayam", "05:49");
                            put("Depok", "05:55");
                            put("Depok Baru", "06:00");
                            put("Pondok Cina", "06:02");
                            put("Univ. Indonesia", "06:06");
                            put("Univ. Pancasila", "06:08");
                            put("Lenteng Agung", "06:09");
                            put("Tanjung Barat", "06:11");
                            put("Pasar Minggu", "06:20");
                            put("Pasar Minggu Baru", "06:22");
                            put("Duren Kalibata", "06:23");
                            put("Cawang", "06:24");
                            put("Tebet", "06:25");
                            put("Manggarai", "06:33");
                            put("Cikini", "06:35");
                            put("Gondangdia", "06:37");
                            put("Juanda", "06:45");
                            put("Sawah Besar", "06:46");
                            put("Mangga Besar", "06:47");
                            put("Jayakarta", "06:53");
                            put("Jakarta Kota", "06:56");
                        }
                    });
                }
            },new HashMap<String, Object>() {
                {
                    put("train_id", "1007");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar",
                                    "Mangga Besar", "Jayakarta", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "05:48");
                            put("Cilebut", "05:57");
                            put("Bojonggede", "06:03");
                            put("Citayam", "06:09");
                            put("Depok", "06:15");
                            put("Depok Baru", "06:20");
                            put("Pondok Cina", "06:22");
                            put("Univ. Indonesia", "06:26");
                            put("Univ. Pancasila", "06:28");
                            put("Lenteng Agung", "06:29");
                            put("Tanjung Barat", "06:31");
                            put("Pasar Minggu", "06:40");
                            put("Pasar Minggu Baru", "06:42");
                            put("Duren Kalibata", "06:43");
                            put("Cawang", "06:44");
                            put("Tebet", "06:45");
                            put("Manggarai", "06:53");
                            put("Cikini", "06:55");
                            put("Gondangdia", "06:57");
                            put("Juanda", "07:05");
                            put("Sawah Besar", "07:06");
                            put("Mangga Besar", "07:07");
                            put("Jayakarta", "07:14");
                            put("Jakarta Kota", "07:17");
                        }
                    });
                }
            },new HashMap<String, Object>() {
                {
                    put("train_id", "1189");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru",
                                    "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung",
                                    "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang",
                                    "Tebet", "Manggarai"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "05:36");
                            put("Cilebut", "05:45");
                            put("Bojonggede", "05:51");
                            put("Citayam", "05:58");
                            put("Depok", "06:05");
                            put("Depok Baru", "06:10");
                            put("Pondok Cina", "06:12");
                            put("Univ. Indonesia", "06:16");
                            put("Univ. Pancasila", "06:18");
                            put("Lenteng Agung", "06:19");
                            put("Tanjung Barat", "06:21");
                            put("Pasar Minggu", "06:29");
                            put("Pasar Minggu Baru", "06:31");
                            put("Duren Kalibata", "06:32");
                            put("Cawang", "06:33");
                            put("Tebet", "06:34");
                            put("Manggarai", "06:42");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "1183");
                    put("train_name", "Commuter Line Bogor");
                    put("route", Arrays.asList("Jatinegara", "Manggarai", "Tanah Abang", "Duri", "Kampung Bandan"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Jatinegara", "08:15");
                            put("Manggarai", "08:30");
                            put("Tanah Abang", "08:50");
                            put("Duri", "09:00");
                            put("Kampung Bandan", "09:15");
                        }
                    });
                }
            },
            // --- Trains going in the opposite direction ---
            new HashMap<String, Object>() {
                {
                    put("train_id", "KRL-B04-REV");
                    put("train_name", "Jakarta Express");
                    put("route", Arrays.asList("Bogor", "Depok", "Manggarai", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "08:00");
                            put("Depok", "08:25");
                            put("Manggarai", "08:50");
                            put("Jakarta Kota", "09:15");
                        }
                    });
                }
            },
            new HashMap<String, Object>() {
                {
                    put("train_id", "KRL-B05-REV");
                    put("train_name", "Jakarta Commuter");
                    put("route", Arrays.asList("Bogor", "Depok", "Pasar Minggu", "Manggarai", "Jakarta Kota"));
                    put("departure_times", new HashMap<String, String>() {
                        {
                            put("Bogor", "08:30");
                            put("Depok", "08:55");
                            put("Pasar Minggu", "09:10");
                            put("Manggarai", "09:25");
                            put("Jakarta Kota", "09:50");
                        }
                    });
                }
            });

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
    } // [1] & [2]
}
// [1] Konten ini dihasilkan oleh Google Gemini (tanggal akses 14 Juni 2025).
// [2] Perbaiki variabel okupansi: asumsi keterisian puncak berada di Manggarai 83%, lebih kecil saat di awal dan di akhir