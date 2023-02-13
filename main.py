from urllib.parse import urljoin
from sys import stderr

import requests


HEADHUNTER_URL = 'https://api.hh.ru'
MOSCOW_ID = 1
MONTH_PERIOD = 30


def get_jobs(language):
    """ Функция возвращает вакансии с сайта hh.ru для программирования на определенном языке
    """
    url = urljoin(HEADHUNTER_URL, '/vacancies')
    payload = {'area': MOSCOW_ID,
               'period': MONTH_PERIOD,
               'text': f'программист {language}'}
    response = requests.get(url, params=payload)
    response.raise_for_status()

    vacancies = response.json()
    return vacancies


def predict_rub_salary(vacancy):
    """ Функция возвращает ожидаемую зарплату в рублях
    """
    salary = vacancy.get('salary')
    if salary and salary.get('currency') == 'RUR':
        salary_from = salary.get('from')
        salary_to = salary.get('to')

        if salary_from and salary_to:
            return int((salary_from + salary_to) / 2)
        elif salary_from:
            return int(1.2 * salary_from)
        elif salary_to:
            return int(0.8 * salary_to)

    return None


def main():
    language = 'python'
    try:
        jobs = get_jobs(language)
        vacancies = jobs.get('items', [])

        for vacancy in vacancies:
            print(predict_rub_salary(vacancy))

    except requests.exceptions.HTTPError:
        stderr.write(f'Не удалось сделать запрос для языка {language}\n')


if __name__ == '__main__':
    main()
