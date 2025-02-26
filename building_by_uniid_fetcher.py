from bs4 import BeautifulSoup
import requests


def fetch_building_id(uniid,
        refresh=False,
        url="https://decision.cs.taltech.ee/DEX3/already_taken.php?group_name=2025K") -> list:
    try:
        with open("/PycharmProjects/dataMining/jsondata/building_by_uniid.txt") as file:
            rows = file.read().split("\n")
            for row in rows:
                if row.split(",")[0] == uniid:
                    return row.split(",")[1:]
                refresh = True
    except FileNotFoundError:
        refresh = True

    if refresh:
        print("Refreshing data")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table')
        rows = []
        for tr in table.find_all('tr')[1:]:
            cells = [td.text.strip() for td in tr.find_all('td')]
            if cells[1].split("@")[0] == uniid:
                rows.append(cells[3])
        with open("/PycharmProjects/dataMining/jsondata/building_by_uniid.txt", "w") as file:
            file.write(uniid+","+",".join(rows))
        return rows
