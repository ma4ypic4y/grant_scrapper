from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from read_write_script import read_json, read_yaml
import json
import yaml


def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4,ensure_ascii=False)


def read_yaml(path):
    with open(path, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data


def clear_json(data):
    '''
    удаление лишних полей
    удаление ключа index
    '''
    data = data['hits']['hits']
    data = [el["_source"] for el in data if el["_source"].get("title") is not None]
    for el in data:
        el.pop("index", None)
    return data


def create_index(client, index_name, settings):
    '''
    созадание индекса
    проверка на существование индекса
    '''
    try:
        client.indices.create(index_name, body=settings)
        print('-'*5+'Index {} created'.format(index_name))
        return True
    except Exception as e:
        if e.args[1] =="resource_already_exists_exception":
            return True
        return False


def upload(index_name, data):
    for i, item in enumerate(data,1):
        print(f'Processing {i} of {len(data)}')
        yield {
            "_index": index_name,
            "_source": item
        }


if __name__ =='__main__':

    data_path = './data_from_elastic.json'
    data = read_json(data_path)
    data = clear_json(data)

    config_path = 'config.yaml'
    ELK_CONFIG = read_yaml(config_path)
    LOGIN = ELK_CONFIG['elastic']['login']
    PASSWORD = ELK_CONFIG['elastic']['password']
    ES_HOST = ELK_CONFIG['elastic']['host']
    # ES_PORT = ELK_CONFIG['elastic']['port']

    print('Connecting to ElasticSearch...')

    index_name = 'grants2'
    url = f'https://{LOGIN}:{PASSWORD}@{ES_HOST}'
    print(url)
    client =  Elasticsearch(url, verify_certs=False, request_timeout=30)

    settings = read_json('mapping.json')

    if create_index(client, index_name, settings):
        print(len(data))
        bulk(client, upload(index_name,data), request_timeout=30)