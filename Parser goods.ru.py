'''

Спарсить отзывы к товарам с сайта goods.ru
По списку артикулов из файла source.csv

Пример артикула: 100013276059

Парсить следующее:
Название товара: Держатель для бумажного полотенца Joseph Joseph Easy-Tear серый
Имя отзыва: Лилия
Общий рейтинг: 4
Дизайн (внешний вид): 5
Качество материалов: 5
Достоинства: Товары бренда Joseph Joseph очень качественные и приятные в использовании, и этот держатель не исключение.
Хорошо смотрится на кухне, крепкий, приятный пластик.
Недостатки: Цвет серый, на мой взгляд, на любителя.
Комментарий: Держатель для бумажных полотенец весит 876гр. Достаточно тяжёлый (пластик +чугун), что позволяет ему
устойчиво оставаться на своём месте при отрывании рулона. Также подставка имеет нескользящее основание . Сверху есть ручка, удобно переносить держатель при необходимости. Есть основной механизм, который регулируется под толщину рулона и всегда плотно его фиксирует. Но первое время придётся приноровиться, чтоб отрывать полотенце одной рукой, как заявляет производитель.
В целом покупкой довольна! Рекомендую!
Ссылки на фото: https://ugc-media.shoppilot.ru/media_files/5be7/5088/6dd2/5c00/3220/5441/original.jpg?1541886085,
https://ugc-media.shoppilot.ru/media_files/5be7/5088/6dd2/5c00/3220/5442/original.jpg?1541886087

'''

password = '123456'


import os
import subprocess
from bs4 import BeautifulSoup
import requests
import csv
from time import time, sleep
from multiprocessing import Pool


def refactor_text(list):
    result = ''
    sp = list.split()
    for el in sp:
        result += el + ' '
    return result[:-1]


def read_file():
    rows_csv = []
    with open('source.csv', 'r', encoding='cp1251') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            rows_csv.append(row)
    return rows_csv[1:]


def get_url(rows_csv):
    url = 'https://goods.ru/catalog/?q={}'
    url = url.format(rows_csv[2])
    r = requests.get(url)
    url = r.url + 'otzyvy/'
    get_data(url, rows_csv)


def get_data(url, rows_csv):
    # print(url)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    try:
        soups = soup.find('div', {'id': 'sp-product-reviews'}).find_all('div', class_='sp-review')
    except AttributeError:
        soups = []
        print(f'{url}\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', file=open('error.txt', 'a'))
    for soup in soups:
        try:
            name = soup.find('div', class_='sp-review-author-name').text
            # print(name)
        except AttributeError:
            name = ''

        try:
            date = soup.find('div', class_='sp-review-date').text.strip()
            # print(date)
        except AttributeError:
            date = ''

        try:
            rating_total = soup.find('span', class_='sp-review-rating-value').text
            # print(rating_total)
        except AttributeError:
            rating_total = ''

        rating_design = rating_material = ''
        rating_other = soup.find_all('div', class_='sp-review-rating-detail-label')
        for i, el in enumerate(rating_other):
            if i == 0:
                rating_design = el.find('span', class_='sp-review-rating-detail-value').text
            if i == 1:
                rating_material = el.find('span', class_='sp-review-rating-detail-value').text
        # print(rating_total, rating_design, rating_material)

        # rating_material = soup.find('span', class_='sp-review-rating-detail-value')
        # print(rating_material)

        try:
            photos = soup.find_all('div', class_='sp-review-photo')
            photo_links = []
            for photo in photos:
                photo_links.append(photo.find('a').get('href'))
            photo_links = list_to_str(photo_links)
            # print(photo_links)
        except AttributeError:
            pass

        try:
            dost = soup.find('div', class_='sp-review-pros-content sp-review-text-content').text
            dost = refactor_text(dost)
            # print(dost)
        except AttributeError:
            dost = ''

        try:
            nedost = soup.find('div', class_='sp-review-cons-content sp-review-text-content').text
            nedost = refactor_text(nedost)
            # print(nedost)
        except AttributeError:
            nedost = ''

        try:
            comment = soup.find('div', class_='sp-review-body-content sp-review-text-content').text
            comment = refactor_text(comment)
            # print(comment)
        except AttributeError:
            comment = ''

        finally:
            count = soup.find('div', class_='components_PdpContentNav__root_0')
            # print('======================================')
            data = {'merchant_name': rows_csv[0],
                    'vendor_name': rows_csv[1],
                    'goods_id': rows_csv[2],
                    'url': url,
                    'date': date,
                    'name': name,
                    'rating_total': rating_total,
                    'rating_design': rating_design,
                    'rating_material': rating_material,
                    'photo_links': photo_links,
                    'dost': dost,
                    'nedost': nedost,
                    'comment': comment}
            write_csv(data)
    if not soups:
        name = rating_total = photo_links = dost = nedost = comment = rating_design = rating_material = date = ''
        data = {'merchant_name': rows_csv[0],
                'vendor_name': rows_csv[1],
                'goods_id': rows_csv[2],
                'url': url,
                'date': date,
                'name': name,
                'rating_total': rating_total,
                'rating_design': rating_design,
                'rating_material': rating_material,
                'photo_links': photo_links,
                'dost': dost,
                'nedost': nedost,
                'comment': comment}
        write_csv(data)


def write_csv(data):
    with open('result.csv', 'a', newline='', encoding='cp1251') as f:
        order = ['merchant_name', 'vendor_name', 'goods_id', 'url', 'date', 'name', 'rating_total', 'rating_design',
                 'rating_material', 'photo_links', 'dost', 'nedost', 'comment']
        writer = csv.DictWriter(f, fieldnames=order, delimiter=';')
        try:
            writer.writerow(data)
        except UnicodeEncodeError:
            pass


def list_to_str(my_list):
    return ' '.join(my_list)


def archiv(file, passwd):
    subprocess.call(['7z', 'a', file + '.zip', '-mx9', f'-p{passwd}'] + [file])


if __name__ == '__main__':
    start = time()
    with open('result.csv', 'w', encoding='cp1251') as f:
        f.write('Merchant offer name;Вендор код (артикул производителя);Goods id;УРЛ;Дата;Имя пользовател;Общий рейтинг;'
                'Дизайн (внешний вид);Качество материалов;Ссылки на фото;Достоинства;Недостатки;Комментарий\n')
    rows_csv = read_file()
    els = []
    for el in rows_csv:
        els.append(el)
    with Pool(10) as p:
        p.map(get_url, els)
    # sleep(30)
    archiv('result.csv', password)
    os.remove('result.csv')
    print(f'Время выполнения {round(time() - start)} сек')
