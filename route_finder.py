# route_finder.py
import collections
import datetime
import heapq
import tkinter as tk
from typing import List, Dict, Any, Set
from PIL import Image, ImageTk

from train_schedule import TrainSchedule
# --- UBAH IMPORT ---
from data_models import RouteNode, Region
import occupancy_predictor as predictor

class RouteFinder:
    """
    Menangani logika inti untuk menemukan rute kereta.
    """
    INTERCHANGE_STATIONS: Dict[str, Set[predictor.Line]] = {
        "manggarai": {predictor.Line.BOGOR, predictor.Line.CIKARANG},
        "tanah abang": {predictor.Line.CIKARANG, predictor.Line.RANGKASBITUNG},
        "duri": {predictor.Line.CIKARANG, predictor.Line.TANGERANG},
        "kampung bandan": {predictor.Line.CIKARANG, predictor.Line.TANJUNG_PRIOK},
        "jakarta kota": {predictor.Line.BOGOR, predictor.Line.TANJUNG_PRIOK},
    }

    def __init__(self, schedule: TrainSchedule):
        self.schedule = schedule
        self.max_result_count = 3 # Menaikkan agar bisa menampilkan beberapa alternatif

    @staticmethod
    def show_map_image(image_path: str):
        # ... (Tidak ada perubahan di sini)
        pass

    # --- UBAH SIGNATURE find_routes ---
    def find_routes(
        self,
        start_station: str,
        dest_station: str,
        start_time: datetime.datetime,
        region: Region  # Parameter baru
    ) -> List[List[Dict[str, Any]]]:
        """
        Menemukan rute antara dua stasiun pada waktu tertentu di wilayah spesifik.
        """
        if not all([start_station, dest_station, start_time, region]):
            return []

        # (waktu_tiba, node)
        queue = [(start_time, RouteNode(start_station, start_time, [], 0))]
        # (stasiun, jumlah_transit): waktu_terbaik
        visited = {(start_station, 0): start_time}
        results = []
        
        # Batas transit untuk mencegah rute yang terlalu kompleks
        max_transits = 2 if region == Region.JABODETABEK else 1

        while queue:
            current_arrival_time, node = heapq.heappop(queue)

            if len(results) >= self.max_result_count:
                break
            
            # --- GUNAKAN get_trains_for_station DENGAN REGION ---
            trains_at_station = self.schedule.get_trains_for_station(node.station, region)

            for train in trains_at_station:
                try:
                    current_idx = train.route.index(node.station)
                except ValueError:
                    continue

                predicted_occupancies = predictor.predict(train, node.time)

                for i in range(current_idx + 1, len(train.route)):
                    next_station = train.route[i]
                    
                    dep_time_str = train.departure_times.get(node.station)
                    if not dep_time_str: continue

                    dep_h, dep_m = map(int, dep_time_str.split(':'))
                    # Gunakan waktu node (yang sudah termasuk waktu tunggu/transit) sebagai basis
                    dep_time = node.time.replace(hour=dep_h, minute=dep_m, second=0, microsecond=0)

                    # Jika waktu keberangkatan berikutnya lebih awal dari waktu saat ini di stasiun,
                    # asumsikan itu untuk hari berikutnya.
                    if dep_time < node.time:
                        dep_time += datetime.timedelta(days=1)
                    
                    # Estimasi waktu perjalanan (bisa diperbaiki jika ada data waktu tiba)
                    # Mari asumsikan waktu perjalanan antar stasiun sekitar 3-5 menit
                    # Di sini kita pakai estimasi kasar, bisa diperbaiki jika data lebih lengkap
                    time_to_next = (i - current_idx) * 4 
                    arr_time = dep_time + datetime.timedelta(minutes=time_to_next)

                    is_different_train = not node.route or train.id != node.route[-1]['train_id']
                    
                    next_transit_count = node.transit
                    if is_different_train and node.route:
                         next_transit_count += 1
                    
                    if next_transit_count > max_transits:
                        continue

                    visit_key = (next_station, next_transit_count)
                    if visit_key in visited and visited[visit_key] <= arr_time:
                        continue

                    leg = {
                        "train_id": train.id, "train_name": train.name,
                        "start_station": node.station, "destination_station": next_station,
                        "departure_time": dep_time.strftime("%H:%M"),
                        "estimated_arrival": arr_time.strftime("%H:%M"),
                        "_departure_dt": dep_time, "_arrival_dt": arr_time,
                        "occupancy_percentage": predicted_occupancies.get(node.station, -1)
                    }
                    
                    new_route_so_far = node.route + [leg]
                    visited[visit_key] = arr_time

                    if next_station == dest_station:
                        results.append(new_route_so_far)
                        if len(results) >= self.max_result_count: break
                    else:
                        # Waktu tunggu untuk transit di stasiun berikutnya
                        transit_wait_minutes = 15 if is_different_train else 2
                        next_node_time = arr_time + datetime.timedelta(minutes=transit_wait_minutes)
                        new_node = RouteNode(next_station, next_node_time, new_route_so_far, next_transit_count)
                        heapq.heappush(queue, (arr_time, new_node))

                if len(results) >= self.max_result_count: break

        results.sort(key=lambda r: (r[-1]['_arrival_dt'], len(r))) # Urutkan berdasarkan waktu tiba dan jumlah leg
        return results[:self.max_result_count]