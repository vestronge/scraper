import datetime
import os
import re

import requests
from bs4 import BeautifulSoup

SEARCH_WORDS = [re.compile(x, flags=re.I) for x in [
    "coproriété", "monopropriété", "divisible", "immeuble", "indépendant", "independant"]]

KEYS = [
    'offer_area', 'offer_post_code', 'offer_property_type_label', 'offer_online_date', 'offer_districts',
    'offer_default_sector', 'offer_price', 'agency_id', 'offer_loc_id',
]
MAIN_LINK = 'https://www.logic-immo.com/bureau-commerce-paris/location-bureau-commerce-paris-75-100_1.html'


def get_offer_links():
    total_searches, link_count = None, 0
    global MAIN_LINK
    next_link = {'href': MAIN_LINK}
    while next_link or link_count < 10:
        txt = requests.get(next_link['href']).content
        soup = BeautifulSoup(txt, features='lxml')
        if not total_searches:
            total_searches = soup.find('input', {'name': 'nbResultats'})['value']
            print(f"Total estimated links to be scraped {total_searches}")
        for x in soup.find_all('div', {'class': 'offer-block'}):
            yield x.find('a', {'class': 'offer-link'})['href']
            link_count += 1
        next_link = soup.find('link', {'rel': 'next'})
    print(int(total_searches) - 2 < link_count < int(total_searches) + 2)


def get_offer_data(page_link):
    txt = requests.get(page_link).content
    soup = BeautifulSoup(txt, features='lxml')
    # TODO: 'template-offer-view-expired'
    if not soup.find('body', {'class': 'template-offer-view'}):
        return
    offer = soup.find('section', {'class': 'navPrevPrext'})
    data = {'offer_id': offer['data-offer-id'], 'offer_type': offer['data-mapper'], 'offer_link': page_link}
    data.update({
        k: soup.find('input', {'class': 'contact_offer_data', 'data-contact-dataname': k})['value'] for k in KEYS})
    global SEARCH_WORDS
    try:
        description = soup.find('div', {'class': 'offer-description-text'})
        content = description.find('meta', {'itemprop': 'description'})['content']
    except Exception as e:
        print(f'Failed fetching description on link {page_link}. Error {repr(e)}')
        content = ''
    data.update({x.pattern: bool(x.search(content)) for x in SEARCH_WORDS})
    return data


def write_offer_data():
    keys = ['offer_link', 'offer_id', 'offer_type'] + KEYS + [x.pattern for x in SEARCH_WORDS]
    file_name = f'immo_{datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%Sutc")}.csv'
    write_path = os.path.join('/data', file_name)
    with open(write_path, 'w') as x:
        x.write(','.join(keys))
        x.write('\n')
        for i, page_link in enumerate(get_offer_links()):
            if i > 10:
                return
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
