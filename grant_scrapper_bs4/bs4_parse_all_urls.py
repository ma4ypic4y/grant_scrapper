from bs4 import BeautifulSoup
import requests
import pandas as pd
from tqdm import tqdm
from threading import Thread


def get_num_pages(url):
    '''
    Получаем количество страниц
    '''
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    page_number_bar = soup.find_all('li', class_='pagination__item')
    num_pages = []
    for num in page_number_bar:
        try:
            num_pages.append(int(num.find('a').get_text()))
        except:
            pass

    return max(num_pages)


def get_links(n_page):
    '''
    Получаем ссылки на все гранты
    '''
    cur_url = url+'?page='+str(n_page)
    page = requests.get(cur_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    ref_block = soup.find('div', class_='table table--p-present table--projects')
    rows = ref_block.find_all('a')
    for row in rows:
        all_links.append(row.get('href'))


if  __name__ == '__main__':
    base_url = 'https://xn--80afcdbalict6afooklqi5o.xn--p1ai'
    url = 'https://xn--80afcdbalict6afooklqi5o.xn--p1ai/public/application/cards'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    page = requests.get(url, headers=headers)

    if page.status_code == 200:
        print('Connection established.')
    else:
        raise Exception('Connection failed.')

    num_pages = get_num_pages(url)

    number_of_threads = 10

    all_links = [] # список ссылок на все гранты (глобальная переменная)
    threads = []
    for i in tqdm(range(1,num_pages+1,number_of_threads)):
        print(i)
        for number in range(number_of_threads):
            # print(i+number)
            t = Thread(target=get_links, args=(i+number,)) # get number for place in list `buttons`
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if (i-1)%10 == 0:
            print('Собрано ссылок: ', len(all_links))
            pd.DataFrame(all_links).to_csv('links.csv', index=False)