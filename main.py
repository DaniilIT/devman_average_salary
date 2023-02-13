from itertools import count
from urllib.parse import urljoin
from sys import stderr

import requests


HEADHUNTER_URL = 'https://api.hh.ru'
MOSCOW_ID = 1
MONTH_PERIOD = 30


def get_jobs(language, page_number):
    """ Функция возвращает вакансии с сайта hh.ru для программирования на определенном языке
    """
    url = urljoin(HEADHUNTER_URL, '/vacancies')
    payload = {'area': MOSCOW_ID,
               'period': MONTH_PERIOD,
               'text': f'программист {language}',
               'per_page': 100,
               'page': page_number}
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
            return (salary_from + salary_to) / 2
        elif salary_from:
            return 1.2 * salary_from
        elif salary_to:
            return 0.8 * salary_to

    return None


def get_hh_statistics(languages):
    """ Возвращает статистику по языкам программирования
    """
    programmer_jobs = {}
    for language in languages:
        jobs_count = None
        salaries = []
        for page_number in count():
            print(f'{language}: page №{page_number}')
            try:
                jobs = get_jobs(language, page_number)
                vacancies = jobs.get('items')

                for vacancy in vacancies:
                    salary = predict_rub_salary(vacancy)
                    if salary:
                        salaries.append(salary)

                if page_number == (jobs.get('pages') - 1):
                    jobs_count = jobs.get('found')
                    break

            except requests.exceptions.HTTPError:
                stderr.write(f'Не удалось сделать запрос для языка {language}\n')
                break

        vacancies_processed = len(salaries)
        average_salary = int(sum(salaries) / vacancies_processed)

        programmer_jobs[language] = {
            'vacancies_found': jobs_count,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary,
        }

    return programmer_jobs


def main():
    languages = ['Fortran', 'Go', 'C', 'C#', 'C++', 'PHP', 'Ruby', 'Java', 'Javascript', 'Python']
    programmer_jobs = get_hh_statistics(languages)

    for language, programmer_job in sorted(programmer_jobs.items(),
                                           key=lambda item: item[1]['average_salary'], reverse=True):
        print(f'{language}:')
        for k, v in programmer_job.items():
            print(f'\t{k}: {v}')


if __name__ == '__main__':
    main()
