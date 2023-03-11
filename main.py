import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import json
import re
from tqdm import tqdm


def get_headers():
    headers = Headers(browser='chrome', os='win', headers=True)
    return headers.generate()


how_many_pages = int(input('Сколько страниц парсить?\n'))
salary_in_usd = input('Получать вакансии только с ЗП в долларах? y/n\n')

count_page = 0
for _ in range(how_many_pages):
    HOST = f'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={count_page}'
    print(f'Парсим {count_page + 1} страницу')
    count_page += 1
    response = requests.get(HOST, headers=get_headers()).text
    soup = BeautifulSoup(response, features='lxml')

    vacancy_list = soup.find('div', class_="vacancy-serp-content")
    vacancies = vacancy_list.findAll('div', class_="vacancy-serp-item__layout")
    parsed = []

    pattern = r'\d.*USD'
    for vacancy in tqdm(vacancies):
        link = vacancy.find('a')['href']
        salary = vacancy.find('span', class_="bloko-header-section-3")
        salary = 'З/П не указана' if salary is None else salary.text

        company_name = vacancy.find(attrs={'data-qa': "vacancy-serp__vacancy-employer"}).text
        company_city = vacancy.find(attrs={'data-qa': "vacancy-serp__vacancy-address"}).text
        search_salary_usd = re.search(pattern, salary)
        response = requests.get(link, headers=get_headers())
        vacancy_details = BeautifulSoup(response.text, features='lxml')
        vacancy_description = vacancy_details.find(attrs={'data-qa': 'vacancy-description'}).text.lower()
        if salary_in_usd == 'n':
            if 'django' and 'flask' in vacancy_description:
                item = {
                    'link': link,
                    'salary': salary,
                    'name': company_name,
                    'city': company_city
                }
                parsed.append(item)
        else:
            if 'django' and 'flask' in vacancy_description and search_salary_usd:
                item = {
                    'link': link,
                    'salary': salary,
                    'name': company_name,
                    'city': company_city
                }
                parsed.append(item)

with open('hh_ru.json', 'w', encoding='utf-8') as file:
    json.dump(parsed, file, ensure_ascii=False, indent=5)
