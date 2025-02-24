from building_by_uniid_fetcher import fetch_building_id
from building_info_fetcher import fetch_building_data, save_data_to_file, json_handler
from building_analizer import analyze_building_data
import numpy as np


def analyze(uniid, headers, save_to):
    building_ids = fetch_building_id(uniid)
    data = []
    for building_id in building_ids:
        building_data_raw = fetch_building_data(building_id)
        building_data = json_handler(building_data_raw, headers)
        data.extend(building_data)
        print(f"{len(data)} entries fetched")
    analyze_building_data(data, save_to)


if __name__ == "__main__":
    uniid = "taltech uniid here"
    headers = ["ehrKood",
               "mahtBruto",
               "yldkasut_pind",
               "ehitisalunePind",
               "maxKorrusteArv",
               "pindala",
               "suletud_netopind"
               ]
    save_to = "4x3/SimilarityMeasurement"
    analyze(uniid, headers, save_to)