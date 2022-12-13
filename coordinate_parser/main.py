# парсер координат snip https://snipp.ru/tools/address-coord

from selenium import webdriver
import json
from selenium.webdriver.common.by import By
import time
import os

import json


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":

    url_parse = "https://snipp.ru/tools/address-coord"

    driver = webdriver.Remote(
        f"http://localhost:4444/wd/hub", options=webdriver.ChromeOptions()
    )

    try:
        with open("./data/test.json") as json_file:
            data = json.load(json_file)

        driver.get(url_parse)
        time.sleep(2)
        input_field = driver.find_element(
            By.XPATH, "//input[@class='ymaps-b-form-input__input']"
        )
        sub_button = driver.find_element(
            By.XPATH,
            "//body/div[2]/main[1]/div[2]/div[1]/ymaps[1]/ymaps[5]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[2]/ymaps[1]/ymaps[2]",
        )
        location_field = driver.find_element(By.XPATH, "//input[@id='ypoint']")
        # data = ['1']
        time.sleep(10)
        counter = 0
        for i, d in enumerate(data):
            counter += 1
            if d["location"]["lat"] is None:
                print(d["location"])
                try:
                    input_field.send_keys(d["addres"])
                    sub_button.click()

                    time.sleep(0.5)

                    input_field.clear()
                    lat, lon = location_field.get_attribute("value").split(",")
                    d["location"] = {"lat": float(lat), "lon": float(lon)}
                    print(f'ITERATEON[{i}] - {d["location"]}')
                except:
                    print(f"[ERROR] {i}")
                    d["location"] = {"lat": None, "lon": None}
                    input_field.clear()
                    continue
            if counter % 100 == 0:
                # couter +=1
                save_json("data/active_data_govno.json", data)
                time.sleep(1)

        save_json("data/active_data_govno.json", data)
    except:
        driver.close()
        driver.quit()
    driver.close()
    driver.quit()
