import json
import re
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

HEAD = 'https://spb.hh.ru/'
MAIN = f'{HEAD}search/vacancy?text=python&area=1&area=2'
LINK_PATTERN = r'href=\"(\S*)\"'
CITY_PATTERN = r'"vacancy-serp__vacancy-address">([А-Яа-я-]*)\<'
COMPANY_PATTERN = r'([А-Яа-яA-Za-z\s-]*)<\/a>'


def _get_headers():
    head = Headers(browser='chrome', os='win').generate()
    return head


def _get_data(raw_data, pattern):
    data = re.search(pattern, raw_data)
    return data.group(1)


def parce_vacancy_list():
    main_page = requests.get(MAIN, headers=_get_headers()).text
    bs_main = BeautifulSoup(main_page, features='html5lib')
    content = bs_main.find(class_='vacancy-serp-content')
    vacancy = content.find_all(class_='serp-item')
    return vacancy


def write_json(data):
    with open('data.json', 'w', ) as outfile:
        json.dump(data, outfile, ensure_ascii=False)


if __name__ == '__main__':
    parsed_data = []
    for item in parce_vacancy_list():
        title = str(item.find('h3').find('span').text)
        link_teg = str(item.find('h3').find('span'))
        link = _get_data(link_teg, LINK_PATTERN)

        company_teg = str(item.find(class_="bloko-v-spacing-container bloko-v-spacing-container_base-2"))
        company = _get_data(company_teg, COMPANY_PATTERN)

        city_teg = str(item.find(class_="vacancy-serp-item__info"))
        city = _get_data(city_teg, CITY_PATTERN)

        vacancy_page = requests.get(link, headers=_get_headers()).text
        bs_vacancy = BeautifulSoup(vacancy_page, features='lxml')
        fork = str(bs_vacancy.find(class_='vacancy-title').find('span').text).replace(u'\xa0', '')

        vacancy_text = str(bs_vacancy.find(class_='g-user-content'))
        if ("Flask" in vacancy_text or 'Django' in vacancy_text) and 'USD' in fork:
            parsed_data.append({
                'link': link,
                'fork': fork,
                'company': company,
                'city': city
            })
        write_json(parsed_data)
