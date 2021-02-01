import requests
import os
from dotenv import load_dotenv
from terminaltables import DoubleTable


def get_hh_vacancies(programming_languages, area="1", period="30"):
    vacancies_stat = {}
    payload = {"period": period, "area": area , "page":0}
    for language in programming_languages:
        payload['text'] = "Программист {}".format(language)
        language_stat = predict_rub_salary_hh(payload)
        vacancies_stat[language] = language_stat
    return vacancies_stat


def get_request(url, params, headers):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    response = response.json()
    return response


def predict_rub_salary_hh(payload):
    language_info = []
    page = 0
    url = "https://api.hh.ru/vacancies"
    headers = {"User-Agent": "HH-User-Agent"}
    pages = get_request(url, payload, headers)['pages']
    vacancies_number = get_request(url, payload, headers)['found']
    while page < pages:
        vacancies = get_request(url, payload, headers)['items']
        for vacancy in vacancies:
            salary = vacancy['salary']
            if salary is None:
                continue
            elif salary['currency'] != 'RUR':
                continue
            salary_from = salary['from']
            salary_to = salary['to']
            average_salary = int(predict_salary(salary_from, salary_to))
            if average_salary != 0:
                language_info.append(average_salary)
        page += 1
    vacancies_info = {"vacancies_found": vacancies_number,
                     "vacancies_processed": len(language_info),
                     "average_salary" :int(sum(language_info)/len(language_info))
                     }
    return vacancies_info


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to in (0, None):
        return salary_from * 1.2
    elif salary_from in (0, None) and salary_to:
        return salary_to * 0.8
    elif salary_from and salary_to:
        return (salary_to + salary_from) / 2


def get_super_job_vacancies(programming_languages, town_id=4, catalogues=48):
    vacancies_stat = {}
    payload = {"town": town_id, "catalogues": catalogues , "page": 0, "count":100}
    for language in programming_languages:
        payload['keyword'] = language
        language_stat = predict_rub_salary_sj(payload)
        vacancies_stat[language] = language_stat
    return vacancies_stat


def predict_rub_salary_sj(payload):
    load_dotenv()
    SUPER_JOB_KEY = os.getenv("SECRET_KEY_SUPERJOB_API")
    language_info = []
    headers = {"X-Api-App-Id": SUPER_JOB_KEY}
    url = "https://api.superjob.ru/2.0/vacancies/"
    page = 0
    #pages = get_request(url, payload, headers)['pages']
    vacancies_number = get_request(url, payload, headers)['total']
    pages = vacancies_number // 100 +1
    while page < pages:
        vacancies = get_request(url, payload, headers)['objects']
        for vacancy in vacancies:
            if vacancy is None:
                continue
            elif vacancy['currency'] != 'rub':
                continue
            average_salary = 0
            salary_from = vacancy['payment_from']
            salary_to = vacancy['payment_to']
            if predict_salary(salary_from, salary_to):
                average_salary = int(predict_salary(salary_from, salary_to))
            if average_salary!=0:
                language_info.append(average_salary)
        page += 1
    vacancies_info = {"vacancies_found": vacancies_number,
                      "vacancies_processed": len(language_info),
                      "average_salary": int(sum(language_info) / len(language_info))
                      }
    return vacancies_info


def create_table(vacancies_information, title):
    TABLE_DATA = [
        ['Язык программирования', 'Найдено вакансий', 'Обработано вакансий', 'Средняя зарплата']
    ]
    for language in vacancies_information.keys():
        TABLE_DATA.append([language, vacancies_information[language]['vacancies_found'],
                           vacancies_information[language]['vacancies_processed'],
                           vacancies_information[language]['average_salary']])
    table_instance = DoubleTable(TABLE_DATA, title)
    return table_instance.table


def main():
    programming_languages = ['Python', 'C', 'C++', 'Java',
                             'JavaScript', 'PHP', 'C#',
                             'Swift', 'Scala', 'Go']
    hh_vacancies_info = get_hh_vacancies(programming_languages)
    sp_vacancies_info = get_super_job_vacancies(programming_languages)
    print(create_table(hh_vacancies_info,"HeadHunter Moscow"))
    print()
    print(create_table(sp_vacancies_info,"SuperJob Moscow"))
    print()


if __name__ == '__main__':
     main()