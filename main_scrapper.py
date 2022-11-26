from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from time import sleep
import json
from selenium.webdriver.chrome.service import Service as ChromeService
import os
from tqdm import tqdm
import time
import uuid

import csv
from threading import Thread
import threading

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4,ensure_ascii=False)

INT_FIELDS = ['ИНН','ОГРН']

FLOAT_FIELDS = ['Рейтинг заявки']

INFO_DICT = {
    'Конкурс': 'competition',
    'Грантовое направление': 'grant_direction',
    'Номер заявки': 'application_number',
    'Дата подачи': 'date_of_submission',
    'Сроки реализации': 'implementation_period',
    'Организация': 'organization',
    'ИНН': 'inn',
    'ОГРН': 'ogrn',
    'Запрашиваемая сумма': 'requested_amount',
    'Софинансирование': 'co_financing',
    'Общая сумма расходов на реализацию проекта': 'amount_of_costs',
    'Рейтинг заявки': 'application_rating',
}

def get_num_pages(driver):
    '''
    получение количества страниц
    '''
    link_to_parse = driver.find_elements('xpath','//a[@class="pagination__link"]')
    num_of_pages = [int(link.text) for link in link_to_parse]
    return list(range(1, max(num_of_pages)+1))

def save_page_to_json(data):
    '''
    добавление данных в json файл
    '''

    with open(os.path.join(DATA_PATH,str(uuid.uuid4()))+'.json', mode='w', encoding='utf-8') as f:
        json.dump(data, f,indent=4,ensure_ascii=False)

def get_row_from_page(driver):
    '''
    получение ссылок на гранты с определенной страницы
    '''
    rows = driver.find_elements('xpath', '//div[@class="table table--p-present table--projects"]/a')
    return [row.get_attribute('href') for row in rows]

def get_data_from_row(driver, row):
    '''
    получение данных с определенного гранта
    '''
    driver.get(row)
    data = {}
    data['title'] = driver.find_element('xpath','//h2[@class="winner-info__title"]').text
    data['status'] = driver.find_element('xpath','//p[@class="winner-info__status"]/span').text
    money_block = driver.find_elements('xpath', '//span[@class="circle-bar__info-item-number"]')

    # надо переработать
    data['requested_amount'] = float(money_block[0].text[:-1].replace(' ', '').replace(',','.'))
    data['co_financing'] = float(money_block[1].text[:-1].replace(' ', '').replace(',','.'))
    data['amount_of_costs'] = float(money_block[2].text[:-1].replace(' ', '').replace(',','.'))

    info_block = driver.find_elements('xpath','//li[@class="winner-info__list-item"]')

    for el in info_block:
        field_name = el.text.split('\n')[0]
        field_value = el.text.split('\n')[1]
        try:
            if field_name in INT_FIELDS:
                 data[INFO_DICT[field_name]] = int(field_value)
            elif field_name in FLOAT_FIELDS:
                data[INFO_DICT[field_name]] = float(field_value.replace(',', "."))
            else:
                data[INFO_DICT[field_name]] = field_value.replace('\"', "'")
        except:
            print('[Error]: ', field_name, field_value)
            pass
    try:
        data['implementation_period_start'] = data['implementation_period'].split(' - ')[0]
        data['implementation_period_end'] = data['implementation_period'].split(' - ')[1]
        data.pop('implementation_period', None)
    except:
        data['implementation_period_start'] = None
        data['implementation_period_end'] = None

    data['aim'] = driver.find_element('xpath','//div[@id="winner-aims"]/ol/li').text
    data['tasks'] = [task.text for task in driver.find_elements('xpath','//div[@id="winner-tasks"]/ol/li')]
    data['target_groups'] = [task.text for task in driver.find_elements('xpath','//div[@id="winner-target"]/ol/li')]
    data['project_geography'] = driver.find_element('xpath','//div[@id="winner-geography"]').text.split('\n')[1]
    data['social_significance'] = ' '.join(driver.find_element('xpath','//div[@id="winner-social"]').text.split('\n')[1:])
    try:
        data['website_link'] = driver.find_element('xpath','//a[@class="winner__details-contacts-item winner__details-contacts-item--link"]').get_attribute('href')
    except:
        data['website_link'] = None

    data['addres'] = driver.find_element('xpath','//span[@class="winner__details-contacts-item"]').text
    data['summary'] = ' '.join(driver.find_element('xpath','//div[@id="winner-summary"]').text.split('\n')[1:])
    return data


def get_data_from_page(page):
    '''
    получение данных с определенной страницы
    '''
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(page)
    rows = get_row_from_page(driver)
    data = []
    for row in rows:
        data.append(get_data_from_row(driver, row))
    driver.close()
    save_page_to_json(data)


if __name__ == '__main__':
    export_data= []
    number_of_threads = 14

    url_parse = 'https://xn--80afcdbalict6afooklqi5o.xn--p1ai/public/application/cards?page=1'

    DATA_PATH = './scrap_data/'
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get(url_parse)

    num_pages = get_num_pages(driver)
    driver.close()

    threads = []
    for i in tqdm(range(500,1000,number_of_threads)):

        for number in range(number_of_threads):
            t = Thread(target=get_data_from_page, args=(url_parse.replace('page=1', f'page={i+number}'),)) # get number for place in list `buttons`
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    driver.quit()