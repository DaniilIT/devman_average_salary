from itertools import count
from sys import stderr
from urllib.parse import urljoin

import requests
from dotenv import dotenv_values
from terminaltables import AsciiTable

HEADHUNTER_URL = 'https://api.hh.ru'
HH_MOSCOW_ID = 1
HH_MONTH_PERIOD = 30

SUPERJOB_URL = 'https://api.superjob.ru/2.0/'
SJ_MOSCOW_ID = 4
SJ_CATALOG_KEY = 48


def get_jobs_hh(language, page_number):
    """ Функция возвращает вакансии с сайта hh.ru для программирования на определенном языке
    """
    url = urljoin(HEADHUNTER_URL, '/vacancies')
    payload = {'area': HH_MOSCOW_ID,
               'period': HH_MONTH_PERIOD,
               'text': f'программист {language.lower()}',
               'per_page': 100,
               'page': page_number}
    response = requests.get(url, params=payload)
    response.raise_for_status()

    vacancies = response.json()
    return vacancies


def predict_salary(salary_from, salary_to):
    """ Функция возвращает ожидаемую зарплату
    """
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return 1.2 * salary_from
    elif salary_to:
        return 0.8 * salary_to

    return None


def predict_rub_salary_hh(vacancy):
    """ Функция возвращает ожидаемую зарплату в рублях для headhunter
    """
    salary = vacancy.get('salary')
    if salary and salary.get('currency') == 'RUR':
        return predict_salary(salary.get('from'), salary.get('to'))

    return None


def get_hh_statistics(language):
    """ Возвращает статистику по языку программирования
    """
    jobs_count = None
    salaries = []
    for page_number in count():
        try:
            jobs = get_jobs_hh(language, page_number)
            vacancies = jobs.get('items')

            for vacancy in vacancies:
                salary = predict_rub_salary_hh(vacancy)
                if salary:
                    salaries.append(salary)

            if page_number == (jobs.get('pages') - 1):
                jobs_count = jobs.get('found')
                break

        except requests.exceptions.HTTPError:
            stderr.write(f'Не удалось сделать запрос для языка {language}\n')
            break

    vacancies_processed = len(salaries)
    try:
        average_salary = int(sum(salaries) / vacancies_processed)
    except ZeroDivisionError:
        average_salary = 0

    return {
        'vacancies_found': jobs_count,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary,
    }


def predict_rub_salary_sj(vacancy):
    """ Функция возвращает ожидаемую зарплату в рублях для superjob
    """
    if vacancy.get('currency') == 'rub':
        return predict_salary(vacancy.get('payment_from'), vacancy.get('payment_to'))

    return None


def get_jobs_sj(token, language, page_number):
    """ Функция возвращает вакансии с сайта superjob для программирования на определенном языке
    """
    url = urljoin(SUPERJOB_URL, 'vacancies/')
    headers = {'X-Api-App-Id': token}
    payload = {'town': SJ_MOSCOW_ID,
               'catalogues': SJ_CATALOG_KEY,
               'keyword': language.lower(),
               'count': 100,
               'page': page_number}
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()

    vacancies = response.json()
    return vacancies


def get_sj_statistics(token, language):
    """ Возвращает статистику по языку программирования
    """
    jobs_count = None
    salaries = []
    for page_number in count():
        try:
            jobs = get_jobs_sj(token, language, page_number)
            vacancies = jobs.get('objects')

            for vacancy in vacancies:
                salary = predict_rub_salary_sj(vacancy)
                if salary:
                    salaries.append(salary)

            if not jobs.get('more'):
                jobs_count = jobs.get('total')
                break

        except requests.exceptions.HTTPError:
            stderr.write(f'Не удалось сделать запрос для языка {language}\n')
            break

    vacancies_processed = len(salaries)
    try:
        average_salary = int(sum(salaries) / vacancies_processed)
    except ZeroDivisionError:
        average_salary = 0

    return {
        'vacancies_found': jobs_count,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary,
    }


def print_statistics_table(statistics, title):
    """ Напечатать таблицу со статистикой по зарплате
    """
    rows = [['язык программирования', 'вакансий найдено', 'вакансий обработано', 'средняя зарплата']]
    for language, language_statistics in sorted(statistics.items(),
                                                key=lambda item: item[1]['average_salary'], reverse=True):
        rows.append([language,
                     language_statistics['vacancies_found'],
                     language_statistics['vacancies_processed'],
                     language_statistics['average_salary'],
                     ])

    table = AsciiTable(rows, title)
    print()
    print(table.table)


def main():
    languages = ['Fortran', 'Go', 'C', 'C#', 'C++', 'PHP', 'Ruby', 'Java', 'JavaScript', 'Python']
    superjob_token = dotenv_values('.env')['superjob_token']

    hh_statistics = {}
    sj_statistics = {}
    for language in languages:
        print(language)
        hh_statistics[language] = get_hh_statistics(language)
        sj_statistics[language] = get_sj_statistics(superjob_token, language)

    print_statistics_table(hh_statistics, 'HeadHunter Moscow')
    print_statistics_table(sj_statistics, 'SuperJob Moscow')


if __name__ == '__main__':
    main()
