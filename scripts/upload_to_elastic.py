from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json

data_path = './data/test.json'

def read_json(filename):

    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_index(client, index_name, settings):

    try:
        client.indices.create(index_name, body=settings)
        print('-'*5+'Index {} created'.format(index_name))
        return True
    except Exception as e:
        if e.args[1] =="resource_already_exists_exception":
            return True
        return False


def get_data_from_text_file(self):
# the function will return a list of docs
    return [l.strip() for l in open(str(self), encoding="utf8", errors='ignore')]


def upload(index_name, data):
    for i, item in enumerate(data,1):
        print(f'Processing {i} of {len(data)}')
        yield {
            "_index": index_name,
            "_source": item
        }

if __name__ =='__main__':

    data = read_json(data_path)
    # LOGIN ='elastic'
    # PASSWORD = 'Qwerty789'
    ES_HOST = "localhost"
    url = f'http://{ES_HOST}'
    client =  Elasticsearch(url, port=9200)
    # print(client.info())
    index_name = 'grants'
    settings = read_json('mapping.json')
    if create_index(client, index_name, settings):
        # print('12'*100)
        data = read_json(data_path)
        print(len(data))
        bulk(client, upload(index_name,data))