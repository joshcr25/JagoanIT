# Prediksi Kereta Api

import datetime
import csv
import json

# --- Simulated Train Data ---
# (TRAIN_SCHEDULE_DATA remains the same as in your original code)
TRAIN_SCHEDULE_DATA = [
    {
        # --- Commuter Line Bogor, Bogor to Jakarta Kota & Bogor to Manggarai
        "train_id": "1157",
        "train_name": "Commuter Line Bogor",
        "route": ["Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru", "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung", "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang", "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar", "Mangga Besar", "Jayakarta", "Jakarta Kota"],
        "departure_times": {
            "Bogor": "04:03",
            "Cilebut": "04:12",
            "Bojonggede": "04:18",
            "Citayam": "04:24",
            "Depok": "04:30",
            "Depok Baru": "04:34",
            "Pondok Cina": "04:36",
            "Univ. Indonesia": "04:40",
            "Univ. Pancasila": "04:42",
            "Lenteng Agung": "04:43",
            "Tanjung Barat": "04:45",
            "Pasar Minggu": "04:53",
            "Pasar Minggu Baru": "04:55",
            "Duren Kalibata": "04:56",
            "Cawang": "04:57",
            "Tebet": "04:58",
            "Manggarai": "05:06",
            "Cikini": "05:08",
            "Gondangdia": "05:10",
            "Juanda": "05:18",
            "Sawah Besar": "05:19",
            "Mangga Besar": "05:20",
            "Jayakarta": "05:25",
            "Jakarta Kota": "05:28"
        }
    },
    {
        "train_id": "1001",
        "train_name": "Commuter Line Bogor",
        "route": ["Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru", "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung", "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang", "Tebet", "Manggarai"],
        "departure_times": {
            "Bogor": "04:13",
            "Cilebut": "04:22",
            "Bojonggede": "04:28",
            "Citayam": "04:34",
            "Depok": "04:40",
            "Depok Baru": "04:44",
            "Pondok Cina": "04:46",
            "Univ. Indonesia": "04:50",
            "Univ. Pancasila": "04:52",
            "Lenteng Agung": "04:53",
            "Tanjung Barat": "04:55",
            "Pasar Minggu": "05:03",
            "Pasar Minggu Baru": "05:05",
            "Duren Kalibata": "05:06",
            "Cawang": "05:07",
            "Tebet": "05:08",
            "Manggarai": "05:16"
        }
    },{
        "train_id": "1161",
        "train_name": "Commuter Line Bogor",
        "route": ["Bogor", "Cilebut", "Bojonggede", "Citayam", "Depok", "Depok Baru", "Pondok Cina", "Univ. Indonesia", "Univ. Pancasila", "Lenteng Agung", "Tanjung Barat", "Pasar Minggu", "Pasar Minggu Baru", "Duren Kalibata", "Cawang", "Tebet", "Manggarai", "Cikini", "Gondangdia", "Juanda", "Sawah Besar", "Mangga Besar", "Jayakarta", "Jakarta Kota"],
        "departure_times": {
            "Bogor": "04:18",
            "Cilebut": "04:27",
            "Bojonggede": "04:33",
            "Citayam": "04:39",
            "Depok": "04:45",
            "Depok Baru": "04:49",
            "Pondok Cina": "04:51",
            "Univ. Indonesia": "04:55",
            "Univ. Pancasila": "04:57",
            "Lenteng Agung": "04:58",
            "Tanjung Barat": "05:00",
            "Pasar Minggu": "04:53",
            "Pasar Minggu Baru": "04:55",
            "Duren Kalibata": "04:56",
            "Cawang": "04:57",
            "Tebet": "04:58",
            "Manggarai": "05:06",
            "Cikini": "05:08",
            "Gondangdia": "05:10",
            "Juanda": "05:18",
            "Sawah Besar": "05:19",
            "Mangga Besar": "05:20",
            "Jayakarta": "05:25",
            "Jakarta Kota": "05:28"
        }
    },
    {
        "train_id": "KRL-B03",
        "train_name": "Bogor Line Express",
        "route": ["Jakarta Kota", "Manggarai", "Depok", "Bogor"],
        "departure_times": {
            "Jakarta Kota": "09:00",
            "Manggarai": "09:25",
            "Depok": "09:50",
            "Bogor": "10:15"
        }
    },
    {
        "train_id": "KRL-J01",
        "train_name": "Jatinegara Loop",
        "route": ["Jatinegara", "Manggarai", "Tanah Abang", "Duri", "Kampung Bandan"],
        "departure_times": {
            "Jatinegara": "08:15",
            "Manggarai": "08:30",
            "Tanah Abang": "08:50",
            "Duri": "09:00",
            "Kampung Bandan": "09:15"
        }
    },
    # --- Trains going in the opposite direction ---
    {
        "train_id": "KRL-B04-REV",
        "train_name": "Jakarta Express",
        "route": ["Bogor", "Depok", "Manggarai", "Jakarta Kota"],
        "departure_times": {
            "Bogor": "08:00",
            "Depok": "08:25",
            "Manggarai": "08:50",
            "Jakarta Kota": "09:15"
        }
    },
    {
        "train_id": "KRL-B05-REV",
        "train_name": "Jakarta Commuter",
        "route": ["Bogor", "Depok", "Pasar Minggu", "Manggarai", "Jakarta Kota"],
        "departure_times": {
            "Bogor": "08:30",
            "Depok": "08:55",
            "Pasar Minggu": "09:10",
            "Manggarai": "09:25",
            "Jakarta Kota": "09:50"
        }
    },
]


# --- Core Prediction Logic ---
# (predict_next_trains and get_available_stations functions remain the same)
def predict_next_trains(start_station: str, dest_station: str, current_time: datetime.datetime):
    predictions = []
    today = current_time.date()
    for train in TRAIN_SCHEDULE_DATA:
        route = train["route"]
        if start_station in route and dest_station in route:
            start_index = route.index(start_station)
            dest_index = route.index(dest_station)
            if start_index < dest_index:
                departure_time_str = train["departure_times"].get(start_station)
                if not departure_time_str:
                    continue
                hour, minute = map(int, departure_time_str.split(':'))
                departure_datetime = datetime.datetime(today.year, today.month, today.day, hour, minute)
                if departure_datetime > current_time:
                    dest_departure_time_str = train["departure_times"].get(dest_station)
                    if not dest_departure_time_str:
                        continue
                    dest_hour, dest_minute = map(int, dest_departure_time_str.split(':'))
                    dest_departure_datetime = datetime.datetime(today.year, today.month, today.day, dest_hour, dest_minute)
                    estimated_arrival_time = dest_departure_datetime - datetime.timedelta(minutes=3)
                    predictions.append({
                        "train_id": train["train_id"],
                        "train_name": train["train_name"],
                        "start_station": start_station,
                        "destination_station": dest_station,
                        "departure_time": departure_datetime.strftime("%H:%M"),
                        "estimated_arrival": estimated_arrival_time.strftime("%H:%M"),
                        "_departure_dt": departure_datetime
                    })
    sorted_predictions = sorted(predictions, key=lambda x: x["_departure_dt"])
    return sorted_predictions

def get_available_stations():
    stations = set()
    for train in TRAIN_SCHEDULE_DATA:
        for station in train["route"]:
            stations.add(station)
    return sorted(list(stations))



# --- Main Application ---

def main():
    """Main function to run the train schedule prediction CLI."""
    simulated_current_time = datetime.datetime(2025, 6, 14, 8, 45)
    print("--- Train Schedule Predictor ---")
    print(f"Current Time (Simulated): {simulated_current_time.strftime('%Y-%m-%d %H:%M')}\n")
    available_stations = get_available_stations()
    print("Available Stations:")
    for i, station in enumerate(available_stations):
        print(f"  {i+1}. {station}")
    print("-" * 30)
    try:
        start_station_num = int(input("Enter the number for your START station: "))
        dest_station_num = int(input("Enter the number for your DESTINATION station: "))
        start_station = available_stations[start_station_num - 1]
        dest_station = available_stations[dest_station_num - 1]
        if start_station == dest_station:
            print("\nError: Start and destination stations cannot be the same.")
            return
        print(f"\nSearching for trains from '{start_station}' to '{dest_station}'...")
        predictions = predict_next_trains(start_station, dest_station, simulated_current_time)
        if not predictions:
            print("\nSorry, no upcoming trains found for your selected route.")
        else:
            print("\n--- Upcoming Train Schedule ---")
            print(f"{'Train Name':<25} | {'Departs At':<12} | {'Est. Arrival':<15}")
            print("-" * 60)
            for train in predictions:
                print(f"{train['train_name']:<25} | {train['departure_time']:<12} | {train['estimated_arrival']:<15}")
            print("-" * 60)


    except (ValueError, IndexError):
        print("\nInvalid input. Please enter a valid number from the list.")

if __name__ == "__main__":
    main()

# [1] Konten ini dihasilkan oleh Google Gemini (tanggal akses 14 Juni 2025).