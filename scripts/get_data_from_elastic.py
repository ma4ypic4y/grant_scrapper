import requests, json, os, sys
from elasticsearch import Elasticsearch, helpers


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


HOST = "localhost"


es = Elasticsearch([{"host": "localhost", "port": "9200"}])
directory = "."

res = es.search(
    index="grants",
    body={"size": 10000, "query": {"bool": {"must": [{"match_all": {}}]}}},
)
save_json("test.json", res)
print(res)
