
# парсер координат snip https://snipp.ru/tools/address-coord

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
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4,ensure_ascii=False)

if __name__ == '__main__':

    url_parse = 'https://snipp.ru/tools/address-coord'

    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    with open('data/active_data.json') as json_file:
        data = json.load(json_file)

    driver.get(url_parse)
    time.sleep(1)
    input_field = driver.find_element(By.XPATH, "//input[@class='ymaps-b-form-input__input']")
    sub_button = driver.find_element(By.XPATH, "//body/div[2]/main[1]/div[2]/div[1]/ymaps[1]/ymaps[5]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[1]/ymaps[2]/ymaps[1]/ymaps[2]")
    location_field = driver.find_element(By.XPATH, "//input[@id='ypoint']")


    couter =0
    for i, d in enumerate(data):
        if d['location']['lat'] is None:
            print(d['location'])
            try:
                input_field.send_keys(d['addres'])
                sub_button.click()

                time.sleep(0.5)

                input_field.clear()
                lat, lon = location_field.get_attribute('value').split(',')
                d['location'] = {'lat': float(lat), 'lon': float(lon)}
                print(f'ITERATEON[{i}] - {d["location"]}')
            except:
                print(f'[ERROR] {i}')
                d['location'] = {'lat': None, 'lon': None}
                input_field.clear()
                continue
        if couter%100 == 0:
            couter +=1
            save_json('data/active_data.json', data)
            time.sleep(1)

    save_json('data/active_data.json', data)
