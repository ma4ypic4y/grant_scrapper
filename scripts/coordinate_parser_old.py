# парсер координат Google Maps

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import time
from parsel import Selector

import json


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":

    url_parse = "https://developers-dot-devsite-v2-prod.appspot.com/maps/documentation/utils/geocoder"

    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    with open("data/merged_file.json") as json_file:
        data = json.load(json_file)

    driver.get(url_parse)
    time.sleep(1)
    sub = driver.find_element(By.XPATH, "//input[@id='query-input']")
    for i, d in enumerate(data):
        if i > 3000:
            break
        try:
            time.sleep(1)
            sub.send_keys(d["addres"])
            sub_button = driver.find_element(By.XPATH, "//input[@id='geocode-button']")
            sub_button.click()
            time.sleep(2)
            print(d["addres"])
            loc = driver.find_element(
                By.XPATH,
                "//body[1]/div[2]/div[1]/div[1]/div[12]/div[1]/div[1]/div[2]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[2]/p[3]",
            )
            lat, lon = loc.text.split(",")
            d_loc = {
                "lat": float(lat.split(":")[1][1:]),
                "lon": float(lon.split("(")[0][:-1]),
            }
            time.sleep(1)
            sub.clear()
            d["location"] = d_loc
        except:
            print(f"[ERROR] {i}")
            d["location"] = {"lat": None, "lon": None}
            sub.clear()
            continue

    save_json("test.json", data)
