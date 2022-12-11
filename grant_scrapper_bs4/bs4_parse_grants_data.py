import pandas as pd
from tqdm import tqdm
import re
import requests
from bs4 import BeautifulSoup
from threading import Thread

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import os
import json
import yaml

import warnings

warnings.filterwarnings("ignore")

INT_FIELDS = ["ИНН", "ОГРН"]

FLOAT_FIELDS = ["Рейтинг заявки"]

INFO_DICT = {
    "Конкурс": "competition",
    "Грантовое направление": "grant_direction",
    "Номер заявки": "application_number",
    "Дата подачи": "date_of_submission",
    "Сроки реализации": "implementation_period",
    "Организация": "organization",
    "ИНН": "inn",
    "ОГРН": "ogrn",
    "Запрашиваемая сумма": "requested_amount",
    "Cофинансирование": "co_financing",
    "Общая сумма расходов на реализацию проекта": "amount_of_costs",
    "Рейтинг заявки": "application_rating",
    "Размер гранта": "requested_amount",
    "Перечислено Фондом на реализацию проекта": "transferred_costs",
}


def read_yaml(path):
    with open(path, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data


def read_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def get_info_from_block(block):
    """
    распарсить блок с информацией о гранте
    вертикальный круглый и вертикальный
    """

    d = {}
    for info in block:
        row = info.find_all("li")
        for item in row:
            item = item.find_all("span")
            key = item[0].text
            value = item[1].text.strip()
            if key in INFO_DICT.keys():
                d[INFO_DICT[key]] = value

            try:
                if key in INT_FIELDS:
                    d[INFO_DICT[key]] = int(value)
                elif key in FLOAT_FIELDS:
                    d[INFO_DICT[key]] = float(value.replace(",", "."))
                else:
                    d[INFO_DICT[key]] = value.replace('"', "'")
            except:
                print("[Error]: ", key, value)
                pass

    if "implementation_period" in d.keys():
        try:
            d["implementation_period_start"] = d["implementation_period"].split(" - ")[
                0
            ]
            d["implementation_period_end"] = d["implementation_period"].split(" - ")[1]
            d.pop("implementation_period", None)
        except:
            d["implementation_period_start"] = None
            d["implementation_period_end"] = None
    else:
        d["requested_amount"] = float(
            d["requested_amount"][:-1].replace(" ", "").replace(",", ".")
        )
        d["co_financing"] = float(
            d["co_financing"][:-1].replace(" ", "").replace(",", ".")
        )

        # для грантов победителей
        try:
            d["amount_of_costs"] = float(
                d["amount_of_costs"][:-1].replace(" ", "").replace(",", ".")
            )
        except:
            d["transferred_costs"] = float(
                d["transferred_costs"][:-1].replace(" ", "").replace(",", ".")
            )

    return d


def get_grant_data(link: str):
    """
    Получить данные о гранте по ссылке
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    page = requests.get(link, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    grant_data = {}

    grant_data["link"] = link

    try:
        title = soup.find("h2", class_="winner-info__title").text
        grant_data["title"] = title.replace('"', "'")
    except:
        grant_data["title"] = None

    status_block = soup.find("p", class_="winner-info__status")
    status = status_block.find("span").get_text()
    grant_data["status"] = status

    info_block = soup.find_all("ul", class_="winner-info__list winner-info__item")
    grant_data.update(get_info_from_block(info_block))

    circle_block = soup.find_all("ul", class_="circle-bar__info")
    grant_data.update(get_info_from_block(circle_block))

    description_block = soup.find("div", id="winner-summary")
    grant_data["summary"] = re.sub(
        " +",
        " ",
        description_block.text.replace("Краткое описание", "")
        .replace("\n", "")
        .replace('"', "'"),
    )

    aim_block = soup.find("div", id="winner-aims")
    grant_data["aim"] = re.sub(
        " +",
        " ",
        aim_block.text.replace("Цель", "").replace("\n", "").replace('"', "'"),
    )

    task_block = soup.find("div", id="winner-tasks")
    task_block = task_block.find_all("li")
    tasks = []
    for task in task_block:
        tasks.append(task.text)
    grant_data["tasks"] = tasks

    social_block = soup.find("div", id="winner-social")
    grant_data["social_significance"] = re.sub(
        " +",
        " ",
        social_block.text.replace("Обоснование социальной значимости", "")
        .replace("\n", "")
        .replace('"', "'"),
    )

    geography_block = soup.find("div", id="winner-geography")
    grant_data["project_geography"] = re.sub(
        " +",
        " ",
        geography_block.text.replace("Обоснование социальной значимости", "")
        .replace("\n", "")
        .replace('"', "'"),
    )

    target_block = soup.find("div", id="winner-target")
    target_block = target_block.find_all("li")
    targets = []
    for target in target_block:
        targets.append(target.text)
    grant_data["target"] = targets

    contact_block = soup.find("div", class_="winner__details-contacts")

    grant_data["address"] = contact_block.find(
        "span", class_="winner__details-contacts-item"
    ).text
    grant_data["website_link"] = (
        contact_block.find("a").text
        if contact_block.find("a").text != "Веб-сайт: нет"
        else None
    )
    grant_data["location"] = {"lat": None, "lon": None}

    return grant_data


def upload(index_name, data):
    print("uploading data to elastic")
    for i, item in enumerate(data, 1):
        # print(f'Processing {i} of {len(data)}')
        yield {"_index": index_name, "_source": item}


def insert_batch_to_elastic(client, index_name: str, links: list):
    """
    Парсинг батчем
    """
    data = [get_grant_data(link) for link in links]
    bulk(client, upload(index_name, data), request_timeout=30)


if __name__ == "__main__":
    df = pd.read_csv(os.path.join("./grant_scrapper_bs4/links.csv"))
    df["0"] = df["0"].apply(
        lambda x: "https://xn--80afcdbalict6afooklqi5o.xn--p1ai" + x
    )
    all_links = df["0"].tolist()

    config_path = "config.yaml"
    ELK_CONFIG = read_yaml(config_path)
    LOGIN = ELK_CONFIG["elastic"]["login"]
    PASSWORD = ELK_CONFIG["elastic"]["password"]
    ES_HOST = ELK_CONFIG["elastic"]["host"]

    print("Connecting to ElasticSearch...")
    index_name = "grants_upd"
    url = f"https://{LOGIN}:{PASSWORD}@{ES_HOST}"
    client = Elasticsearch(url, verify_certs=False, request_timeout=30)
    settings = read_json("mapping.json")

    if not client.indices.exists(index_name):
        client.indices.create(index_name, body=settings)
        print("-" * 5 + "Index {} created".format(index_name))

    number_of_threads = 3

    BATCH = 200
    threads = []
    for i in tqdm(range(0, len(all_links) - BATCH, BATCH)):

        for number in range(number_of_threads):
            t = Thread(
                target=insert_batch_to_elastic,
                args=(client, index_name, all_links[i : i + BATCH]),
            )  # get number for place in list `buttons`
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    # записываем остаток
    if len(all_links) % BATCH:
        insert_batch_to_elastic(
            client, index_name, all_links[-(len(all_links) % BATCH) :]
        )
