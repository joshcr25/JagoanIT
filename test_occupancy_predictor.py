import datetime
import mlflow
import mlflow.sklearn
from occupancy_predictor import predict, calculate_confidence, OccupancyPredictorModel
from data_models import Train, Region

def test_occupancy_and_log01():
    # Contoh data uji
    route = [
        "Depok",
"Citayam",
"Bojong Gede",
"Cilebut",
"Bogor"
    ]
    train = Train(train_id="123", route=route)
    current_time = datetime.datetime(year=2025, month=6, day=16, hour=12, minute=0)

    # Mulai MLflow run
    with mlflow.start_run(run_name=f"occupancy_predictor_test {str(current_time).replace(":", "")}", description="Okupansi KRL dari Depok - Bogor di hari kerja di luar jam sibuk yg berusaha utk mendekati okupansi sebenarnya"):
        # Prediksi okupansi
        occupancy_map = predict(train, current_time)
        confidence = calculate_confidence(occupancy_map)
        
        # Log metrik okupansi parameter
        mlflow.log_param("train_id", train.train_id)
        mlflow.log_param("route", train.route)
        mlflow.log_param("time", current_time)

        # Log metrik okupansi rata-rata dan confidence
        for occupancy in occupancy_map:
            mlflow.log_metric(occupancy, occupancy_map[occupancy])
        mlflow.log_metric("confidence", confidence)

        # Log model (skema MLflow pyfunc)
        model = OccupancyPredictorModel()
        mlflow.pyfunc.log_model(
            artifact_path=f"occupancy_predictor_model  {str(current_time).replace(":", "")}",
            python_model=model,
            registered_model_name="OccupancyPredictorModel")

        print("Occupancy map:", occupancy_map)
        print("Confidence:", confidence)
        print("MLflow run logged.")
        
def test_occupancy_and_log02():
    # Contoh data uji
    route = [
       "Depok",
"Citayam",
"Bojong Gede",
"Cilebut",
"Bogor"
    ]
    train = Train(train_id="123", route=route)
    current_time = datetime.datetime(year=2025, month=6, day=16, hour=18, minute=0)

    # Mulai MLflow run
    with mlflow.start_run(run_name=f"occupancy_predictor_test {str(current_time).replace(":", "")}", description="Okupansi KRL dari Depok - Bogor di hari kerja di jam sibuk sore yg berusaha utk mendekati okupansi sebenarnya"):
        # Prediksi okupansi
        occupancy_map = predict(train, current_time)
        confidence = calculate_confidence(occupancy_map)
        
        # Log metrik okupansi parameter
        mlflow.log_param("train_id", train.train_id)
        mlflow.log_param("route", train.route)
        mlflow.log_param("time", current_time)

        # Log metrik okupansi rata-rata dan confidence
        for occupancy in occupancy_map:
            mlflow.log_metric(occupancy, occupancy_map[occupancy])
        mlflow.log_metric("confidence", confidence)

        # Log model (skema MLflow pyfunc)
        model = OccupancyPredictorModel()
        mlflow.pyfunc.log_model(
            artifact_path=f"occupancy_predictor_model  {str(current_time).replace(":", "")}",
            python_model=model,
            registered_model_name="OccupancyPredictorModel")

        print("Occupancy map:", occupancy_map)
        print("Confidence:", confidence)
        print("MLflow run logged.")
        
def test_occupancy_and_log03():
    # Contoh data uji
    route = [
        "Depok",
"Citayam",
"Bojong Gede",
"Cilebut",
"Bogor"
    ]
    train = Train(train_id="123", route=route)
    current_time = datetime.datetime(year=2025, month=6, day=15, hour=10, minute=0)

    # Mulai MLflow run
    with mlflow.start_run(run_name=f"occupancy_predictor_test {str(current_time).replace(":", "")}", description="Okupansi KRL dari Depok - Bogor di akhir pekan yg berusaha utk mendekati okupansi sebenarnya"):
        # Prediksi okupansi
        occupancy_map = predict(train, current_time)
        confidence = calculate_confidence(occupancy_map)
        
        # Log metrik okupansi parameter
        mlflow.log_param("train_id", train.train_id)
        mlflow.log_param("route", train.route)
        mlflow.log_param("time", current_time)

        # Log metrik okupansi rata-rata dan confidence
        for occupancy in occupancy_map:
            mlflow.log_metric(occupancy, occupancy_map[occupancy])
        mlflow.log_metric("confidence", confidence)

        # Log model (skema MLflow pyfunc)
        model = OccupancyPredictorModel()
        mlflow.pyfunc.log_model(
            artifact_path=f"occupancy_predictor_model  {str(current_time).replace(":", "")}",
            python_model=model,
            registered_model_name="OccupancyPredictorModel")

        print("Occupancy map:", occupancy_map)
        print("Confidence:", confidence)
        print("MLflow run logged.")
        
def test_all_non_red_lines():
    # Daftar rute representative (selain lin Merah/Bogor/Nambo - Jakarta Kota)
    test_cases = [
        {
            "name": "Cikarang-Angke",
            "route": [
                "Cikarang", "Cibitung", "Tambun", "Bekasi Timur", "Bekasi", "Kranji", "Cakung", "Klender Baru", "Buaran", "Klender", "Jatinegara", "Pondok Jati", "Kramat", "Gang Sentiong", "Pasar Senen", "Kemayoran", "Rajawali", "Kampung Bandan", "Angke"
            ]
        },
        {
            "name": "Bekasi-Angke",
            "route": [
                "Bekasi", "Kranji", "Cakung", "Klender Baru", "Buaran", "Klender", "Jatinegara", "Pondok Jati", "Kramat", "Gang Sentiong", "Pasar Senen", "Kemayoran", "Rajawali", "Kampung Bandan", "Angke"
            ]
        },
        {
            "name": "Rangkasbitung-Tanah Abang",
            "route": [
                "Rangkasbitung", "Citeras", "Maja", "Cikoya", "Tigaraksa", "Tenjo", "Daru", "Cilejit", "Parung Panjang", "Cicayur", "Cisauk", "Serpong", "Rawa Buntu", "Sudimara", "Jurang Mangu", "Pondok Ranji", "Kebayoran", "Palmerah", "Tanah Abang"
            ]
        },
        {
            "name": "Parung Panjang-Tanah Abang",
            "route": [
                "Parung Panjang", "Cicayur", "Cisauk", "Serpong", "Rawa Buntu", "Sudimara", "Jurang Mangu", "Pondok Ranji", "Kebayoran", "Palmerah", "Tanah Abang"
            ]
        }
    ]

    # Tiga kondisi waktu: jam sibuk pagi, di luar jam sibuk (siang), akhir pekan
    test_times = [
        {"desc": "peak_morning", "dt": datetime.datetime(2025, 6, 17, 7, 0)},   # Selasa, jam sibuk pagi
        {"desc": "offpeak_noon", "dt": datetime.datetime(2025, 6, 17, 13, 0)},  # Selasa, siang
        {"desc": "weekend", "dt": datetime.datetime(2025, 6, 15, 10, 0)},       # Minggu, akhir pekan
    ]

    for case in test_cases:
        for time_case in test_times:
            train = Train(train_id=f"{case['name']}_{time_case['desc']}", route=case["route"])
            current_time = time_case["dt"]
            run_name = f"occupancy_predictor_test_{case['name']}_{time_case['desc']}_{str(current_time).replace(':', '')}"
            desc = f"Okupansi KRL {case['name']} pada {time_case['desc']}"
            with mlflow.start_run(run_name=run_name, description=desc):
                occupancy_map = predict(train, current_time)
                confidence = calculate_confidence(occupancy_map)
                mlflow.log_param("train_id", train.train_id)
                mlflow.log_param("route", train.route)
                mlflow.log_param("time", current_time)
                for occupancy in occupancy_map:
                    mlflow.log_metric(occupancy, occupancy_map[occupancy])
                mlflow.log_metric("confidence", confidence)
                model = OccupancyPredictorModel()
                mlflow.pyfunc.log_model(
                    artifact_path=f"occupancy_predictor_model_{case['name']}_{time_case['desc']}",
                    python_model=model,
                    registered_model_name="OccupancyPredictorModel")
                print(f"[{case['name']} - {time_case['desc']}] Occupancy map:", occupancy_map)
                print(f"[{case['name']} - {time_case['desc']}] Confidence:", confidence)
                print("MLflow run logged.")

def test_krl_yogya_solo():
    # Rute KRL Yogyakarta - Palur (Solo)
    route = [
        "Yogyakarta", "Lempuyangan", "Maguwo", "Brambanan", "Klaten", "Purwosari", "Solo Balapan", "Solo Jebres", "Palur"
    ]
    train = Train(train_id="KRL_YOGYA_SOLO", route=route)
    # Uji di tiga waktu berbeda
    test_times = [
        {"desc": "peak_morning", "dt": datetime.datetime(2025, 6, 17, 7, 0)},
        {"desc": "offpeak_noon", "dt": datetime.datetime(2025, 6, 17, 13, 0)},
        {"desc": "weekend", "dt": datetime.datetime(2025, 6, 15, 10, 0)},
    ]
    for time_case in test_times:
        current_time = time_case["dt"]
        run_name = f"occupancy_predictor_test_KRL_YOGYA_SOLO_{time_case['desc']}_{str(current_time).replace(':', '')}"
        desc = f"Okupansi KRL Yogyakarta-Palur pada {time_case['desc']}"
        with mlflow.start_run(run_name=run_name, description=desc):
            occupancy_map = predict(train, current_time)
            confidence = calculate_confidence(occupancy_map)
            mlflow.log_param("train_id", train.train_id)
            mlflow.log_param("route", train.route)
            mlflow.log_param("time", current_time)
            for occupancy in occupancy_map:
                mlflow.log_metric(occupancy, occupancy_map[occupancy])
            mlflow.log_metric("confidence", confidence)
            model = OccupancyPredictorModel()
            mlflow.pyfunc.log_model(
                artifact_path=f"occupancy_predictor_model_KRL_YOGYA_SOLO_{time_case['desc']}",
                python_model=model,
                registered_model_name="OccupancyPredictorModel")
            print(f"[KRL YOGYA-SOLO - {time_case['desc']}] Occupancy map:", occupancy_map)
            print(f"[KRL YOGYA-SOLO - {time_case['desc']}] Confidence:", confidence)
            print("MLflow run logged.")

def test_ka_prameks():
    # Rute KA Prameks Kutoarjo - Yogyakarta
    route = [
        "Kutoarjo", "Jenar", "Wojo", "Wates", "Yogyakarta"
    ]
    train = Train(train_id="PRAMEKS", route=route)
    test_times = [
        {"desc": "peak_morning", "dt": datetime.datetime(2025, 6, 17, 7, 0)},
        {"desc": "offpeak_noon", "dt": datetime.datetime(2025, 6, 17, 13, 0)},
        {"desc": "weekend", "dt": datetime.datetime(2025, 6, 15, 10, 0)},
    ]
    for time_case in test_times:
        current_time = time_case["dt"]
        run_name = f"occupancy_predictor_test_PRAMEKS_{time_case['desc']}_{str(current_time).replace(':', '')}"
        desc = f"Okupansi KA Prameks Kutoarjo-Yogyakarta pada {time_case['desc']}"
        with mlflow.start_run(run_name=run_name, description=desc):
            occupancy_map = predict(train, current_time)
            confidence = calculate_confidence(occupancy_map)
            mlflow.log_param("train_id", train.train_id)
            mlflow.log_param("route", train.route)
            mlflow.log_param("time", current_time)
            for occupancy in occupancy_map:
                mlflow.log_metric(occupancy, occupancy_map[occupancy])
            mlflow.log_metric("confidence", confidence)
            model = OccupancyPredictorModel()
            mlflow.pyfunc.log_model(
                artifact_path=f"occupancy_predictor_model_PRAMEKS_{time_case['desc']}",
                python_model=model,
                registered_model_name="OccupancyPredictorModel")
            print(f"[PRAMEKS - {time_case['desc']}] Occupancy map:", occupancy_map)
            print(f"[PRAMEKS - {time_case['desc']}] Confidence:", confidence)
            print("MLflow run logged.")

def test_ka_lokal_rangkas_merak():
    # Rute KA Lokal Rangkasbitung - Merak
    route = [
        "Rangkasbitung", "Jambu Baru", "Catang", "Cikeusal", "Walantaka", "Serang", "Karangantu", "Tonjong Baru", "Cilegon", "Krenceng", "Merak"
    ]
    train = Train(train_id="RANGKAS_MERAK", route=route)
    test_times = [
        {"desc": "peak_morning", "dt": datetime.datetime(2025, 6, 17, 7, 0)},
        {"desc": "offpeak_noon", "dt": datetime.datetime(2025, 6, 17, 13, 0)},
        {"desc": "weekend", "dt": datetime.datetime(2025, 6, 15, 10, 0)},
    ]
    for time_case in test_times:
        current_time = time_case["dt"]
        run_name = f"occupancy_predictor_test_RANGKAS_MERAK_{time_case['desc']}_{str(current_time).replace(':', '')}"
        desc = f"Okupansi KA Lokal Rangkasbitung-Merak pada {time_case['desc']}"
        with mlflow.start_run(run_name=run_name, description=desc):
            occupancy_map = predict(train, current_time)
            confidence = calculate_confidence(occupancy_map)
            mlflow.log_param("train_id", train.train_id)
            mlflow.log_param("route", train.route)
            mlflow.log_param("time", current_time)
            for occupancy in occupancy_map:
                mlflow.log_metric(occupancy, occupancy_map[occupancy])
            mlflow.log_metric("confidence", confidence)
            model = OccupancyPredictorModel()
            mlflow.pyfunc.log_model(
                artifact_path=f"occupancy_predictor_model_RANGKAS_MERAK_{time_case['desc']}",
                python_model=model,
                registered_model_name="OccupancyPredictorModel")
            print(f"[RANGKAS-MERAK - {time_case['desc']}] Occupancy map:", occupancy_map)
            print(f"[RANGKAS-MERAK - {time_case['desc']}] Confidence:", confidence)
            print("MLflow run logged.")

if __name__ == "__main__":
    test_krl_yogya_solo()
    test_ka_prameks()
    test_ka_lokal_rangkas_merak()