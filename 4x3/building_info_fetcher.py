import requests
import json


# ---- this section of code was taken from the https://github.com/innarliiv/bigdata4digitalconstruction ----

def fetch_building_data(building_id):
    # If building_id json file exists, return it
    try:
        with open(f"4x3/jsondata/{building_id}.ehr.json") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Fetching new data for building {building_id}")

    # URL of the API endpoint
    url = 'https://devkluster.ehr.ee/api/building/v2/buildingsData'

    # Headers to specify that we accept JSON and will send JSON
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

    # Data payload with the building ID
    payload = {'ehrCodes': [building_id]  # This assumes the API expects a list, even for a single ID
    }

    # Making the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        save_data_to_file(building_id, response.json())
        return response.json()
    else:
        # Handle errors or unsuccessful responses
        print(f"Error fetching data: {response.status_code}")
        return None


def save_data_to_file(building_id, data, path="4x3/jsondata"):
    filename = f"{path}/{building_id}.ehr.json"
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {filename}")


# ---- end of the section of code taken from the https://github.com/innarliiv/bigdata4digitalconstruction ----


def find_values(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return convert_type(obj[key])
        for v in obj.values():
            result = find_values(v, key)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_values(item, key)
            if result is not None:
                return result
    return None


def convert_type(value):
    if isinstance(value, str):
        if value.isdigit():
            return int(value)
        try:
            return float(value) if '.' in value else int(value)
        except ValueError:
            return value
    return value


def json_handler(json_data, headers):
    data = []
    for item in json_data:
        item_data = {header: find_values(item, header) for header in headers}
        data.append(item_data)
    return data
