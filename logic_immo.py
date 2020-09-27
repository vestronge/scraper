import requests
from bs4 import BeautifulSoup


KEYS = [
    'offer_area', 'offer_post_code', 'offer_property_type_label', 'offer_online_date', 'offer_districts',
    'offer_default_sector', 'offer_price', 'agency_id', 'offer_loc_id',
]


def get_offer_links():
    main_link = 'https://www.logic-immo.com/bureau-commerce-paris/location-bureau-commerce-paris-75-100_1.html'
    total_searches, link_count = None, 0
    next_link = {'href': main_link}
    while next_link:
        txt = requests.get(next_link['href']).content
        soup = BeautifulSoup(txt, features='lxml')
        for x in soup.find_all('div', {'class': 'offer-block'}):
            yield x.find('a', {'class': 'offer-link'})['href']
            link_count += 1
        total_searches = total_searches or soup.find('input', {'name': 'nbResultats'})['value']
        next_link = soup.find('link', {'rel': 'next'})
    assert int(total_searches) - 2 < link_count < int(total_searches) + 2

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
    return data


def write_offer_data(write_path):
    keys = ['offer_link', 'offer_id', 'offer_type'] + KEYS
    with open(write_path, 'w') as x:
        x.write(','.join(keys))
        x.write('\n')
        for i, page_link in enumerate(get_offer_links()):
            print(i, page_link)
            try:
                data = get_offer_data(page_link)
            except Exception as e:
                print(f'Error on link {page_link}. Error {repr(e)}')
                continue
            if data:
                x.write(','.join([f'"{data[key]}"' for key in keys]))
                x.write('\n')


# write_offer_data('/Users/ehteshamakhtarsiddiqui/Desktop/immo.csv')
