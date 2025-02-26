from Script2_Draw_Building_TopDown_View import gain_png
from building_by_uniid_fetcher import fetch_building_id
from topdown_analizer import simple_similarity, compose_matrix


if __name__ == "__main__":
    uniid = "datjul"
    save_to = "/PycharmProjects/dataMining/2D analize/TopDown"
    building_id = fetch_building_id(uniid)
    buildings = []
    for ehr in building_id:
        building = {"code": int(ehr), "polygon": gain_png(ehr, save_to)}
        buildings.append(building)

    compose_matrix(buildings)
