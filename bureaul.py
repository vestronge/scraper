import datetime
import os
import re
import json

import requests
from bs4 import BeautifulSoup

SEARCH_WORDS = [re.compile(x, flags=re.I) for x in [
    "coproriété", "monopropriété", "divisible", "immeuble", "indépendant", "independant"]]

KEYS = [
    'street', 'zip_code', 'city', 'latitude', 'longitude', 'transaction_date',
    'is_sale', 'is_rental', 'is_office', 'is_land', 'is_business_center', 'is_commercial', 'is_warehouse',
    'is_activity', 'is_shared_space', 'is_closed_office', 'sale_price', 'yearly_rent', 'seat_price', 'displayed_price',
    'hide_price',  'hide_address',  'total_surface', 'leasing_right_price', 'label', 'is_new', 'is_exclusive',
    'is_super_premium', 'is_ephemeral_rental', 'monthly_rent', 'monthly_rent_transmitted', 'weekly_rent',
    'weekly_rent_transmitted', 'entrance_fee', 'business_assets_transfer_price', 'minimal_surface', 'num_seats',
    'video_url', 'virtual_tour_url', 'is_listing', 'is_transaction', 'contact_form_url', 'price_value', 'price_label',
    'customer__listings_addresses_policy', 'customer__id', 'customer__name', 'customer__trade_name', 'customer__url',
    'customer__phone_rfc3966', 'customer__contact_name', 'customer__phone', 'customer__has_call_tracking',
    'customer__callr_phone__did_number_national',
]
MAIN_LINK = '/immobilier-d-entreprise/annonces/paris-75/location-bureaux'
BASE_URL = 'https://www.bureauxlocaux.com'


def get_offer_links():
    total_searches, link_count = None, 0
    global MAIN_LINK, BASE_URL
    next_links = [{'href': MAIN_LINK}]
    js_regex = re.compile('<script.*?> *(.*?) *</script> *$', flags=re.S | re.I)
    ids_done, links_visited = set(), set()
    while next_links:
        next_link = next_links.pop(0)
        if (not next_link) or next_link['href'] in links_visited:
            continue
        links_visited.add(next_link['href'])
        txt = requests.get(BASE_URL + next_link['href']).content
        soup = BeautifulSoup(txt, features='lxml')
        if not total_searches:
            total_searches = soup.find('div', {'data-label': 'locations'})['data-count']
            print(f"Total estimated links to be scraped {total_searches}")
        js_content = soup.find('script', {'type': 'text/json', 'id': 'listings-data'}).prettify()
        js_content = js_content.replace('\n', '')
        f_o = js_regex.match(js_content)
        if f_o:
            items = json.loads(f_o.group(1))['results']['items']
            for item_dict in items:
                if not item_dict.get('url'):
                    continue
                current_id = item_dict['id']
                if current_id not in ids_done:
                    yield item_dict
                    link_count += 1
                    ids_done.add(current_id)
        next_links.extend(soup.findAll('a', {'data-page': True}))
    print(int(total_searches) - 2 < link_count < int(total_searches) + 2)


def get_offer_data(item_dict):
    global BASE_URL, SEARCH_WORDS
    page_link = BASE_URL + item_dict['url']
    data = {'page_link': page_link, 'id': item_dict['id']}
    data.update({x: item_dict.get(x) for x in KEYS})
    txt = requests.get(page_link).content
    soup = BeautifulSoup(txt, features='lxml')
    description = soup.find('div', {'class': 'ad-description'})
    content = description.prettify()
    data.update({x.pattern: bool(x.search(content)) for x in SEARCH_WORDS})
    return data


def write_offer_data():
    keys = ['page_link', 'id'] + KEYS + [x.pattern for x in SEARCH_WORDS]
    file_name = f'bureau_l_{datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%Sutc")}.csv'
    write_path = os.path.join('/data', file_name)
    with open(write_path, 'w') as x:
        x.write(','.join(keys))
        x.write('\n')
        for i, item_dict in enumerate(get_offer_links()):
            print(f'Scraping site number {str(i).zfill(4)}, url {item_dict["url"]} ...')
            try:
                data = get_offer_data(item_dict)
            except Exception as e:
                print(f'Error on link {item_dict["url"]}. Error {repr(e)}')
                continue
            if data:
                x.write(','.join([f'"{data[key]}"' for key in keys]))
                x.write('\n')


if __name__ == '__main__':
    write_offer_data()
