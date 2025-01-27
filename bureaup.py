import datetime
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

import requests
from bs4 import BeautifulSoup

SEARCH_WORDS = [re.compile(x, flags=re.I) for x in [
    "coproriété", "monopropriété", "divisible", "immeuble", "indépendant", "independant"]]

MAIN_LINK = 'https://www.bureauxapartager.com/location-bureau-paris'


def get_offer_links():
    link_count = 0
    global MAIN_LINK
    visited_links = set()

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1420,1080')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.binary_location = '/usr/bin/google-chrome'
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=chrome_options)
    driver.get(MAIN_LINK)
    html = driver.page_source
    while True:
        soup = BeautifulSoup(html, features='lxml')
        new_found = False
        for x in soup.find_all('a', {'class': 'offer-container__link'}):
            if x['href'] in visited_links:
                continue
            else:
                yield x['href']
                visited_links.add(x['href'])
                new_found = True
                link_count += 1
        if not new_found:
            break
        try:
            element = driver.find_element_by_css_selector('.btn--more-results')
        except:
            break
        if not element:
            break
        driver.execute_script("arguments[0].click();", element)
        sleep(2)
        html = driver.page_source

    print(link_count)


def clean(txt):
    return re.sub('\s+', ' ', txt.replace('\n', '')).strip()


def get_offer_data(page_link):
    data = {'page_link': page_link}

    txt = requests.get(page_link).content
    soup = BeautifulSoup(txt, features='lxml')
    data['offer_id'] = soup.find('div', {'is': 'offer-favorite-slot', 'hash-id': True})['hash-id']
    offer_details = soup.find('div', {'class': 'offer-details__top'})
    data['offer_title'] = clean(
        offer_details.find('div', {'class': 'offer-info__title'}).find('span', {'itemprop': 'name'}).text)
    characteristics = offer_details.find('div', {'class': 'offer-info__characteristics'})
    try:
        data['offer_surface'] = clean(
            characteristics.find('span', {'class': 'offer-info__surface'}).find('span', {'itemprop': 'value'}).text)
    except:
        data['offer_surface'] = ''
    capacity = characteristics.find('span', {'class': 'offer-info__capacity'})
    try:
        offer_capacity_1 = clean(capacity.find('span', {'itemprop': 'value'}).text)
    except:
        offer_capacity_1 = ''
    try:
        offer_capacity_2 = clean(capacity.find('span', {'itemprop': 'name'}).text)
    except:
        offer_capacity_2 = ''

    data['offer_capacity'] = (offer_capacity_1 + ' ' + offer_capacity_2).strip()

    data['offer_address'] = clean(offer_details.find('div', {'class': 'offer-info__address'}).find('p').text)
    data['offer_price'] = clean(offer_details.find('div', {'class': 'offer-info__price'}).text)
    try:
        data['offer_price_per_seat'] = clean(offer_details.find('div', {'class': 'offer-info__price-per-seat'}).text)
    except:
        data['offer_price_per_seat'] = ''

    global SEARCH_WORDS
    description = data['offer_title']
    description += ' ' + clean(soup.find('div', {'class': 'content__info'}).text)
    data.update({x.pattern: bool(x.search(description)) for x in SEARCH_WORDS})
    return data


def write_offer_data():
    keys = ['page_link', 'offer_id', 'offer_title', 'offer_surface', 'offer_capacity', 'offer_address', 'offer_price',
            'offer_price_per_seat'] + [x.pattern for x in SEARCH_WORDS]
    file_name = f'bureau_p_{datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%Sutc")}.csv'
    write_path = os.path.join('/data', file_name)
    with open(write_path, 'w') as x:
        x.write(','.join(keys))
        x.write('\n')
        for i, page_link in enumerate(get_offer_links()):
            print(f'Scraping site number {str(i).zfill(4)}, url {page_link} ...')
            try:
                data = get_offer_data(page_link)
            except Exception as e:
                print(f'Error on link {page_link}. Error {repr(e)}')
                continue
            if data:
                x.write(','.join([f'"{data[key]}"' for key in keys]))
                x.write('\n')


if __name__ == '__main__':
    write_offer_data()
