import json


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def fill_na_coords(path):
    """
    заполняет пропуски в координатах
    """
    with open(path) as json_file:
        data = json.load(json_file)
        for i, d in enumerate(data):
            d["index"] = i
            if not d.get("location"):
                d["location"] = {"lat": None, "lon": None}
    save_json(path, data)


if __name__ == "__main__":
    fill_na_coords("./data/test.json")
