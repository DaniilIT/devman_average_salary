from urllib.parse import urljoin
from sys import stderr

import requests


HEADHUNTER_URL = 'https://api.hh.ru/'
MOSCOW_ID = 1
MONTH_PERIOD = 30


def count_jobs(language):
    url = urljoin(HEADHUNTER_URL, '/vacancies')
    payload = {'area': MOSCOW_ID,
               'period': MONTH_PERIOD,
               'text': f'программист {language}'}
    response = requests.get(url, params=payload)
    response.raise_for_status()

    vacancies = response.json()
    return vacancies['found']


def main():
    languages = ['java', 'Go', 'C', 'C#', 'C++', 'PHP', 'Ruby', 'java', 'javascript', 'python']
    programmer_jobs = {}
    for language in languages:
        try:
            programmer_jobs[language] = count_jobs(language)
        except requests.exceptions.HTTPError:
            stderr.write(f'Не удалось сделать запрос для языка {language}\n')

    for language, jobs_count in sorted(programmer_jobs.items(), key=lambda item: item[1], reverse=True):
        print(f'{language} - {jobs_count}')


if __name__ == '__main__':
    main()
