import requests
import os
from dotenv import load_dotenv
from terminaltables import DoubleTable


def get_hh_vacancies(programming_languages, area="1", period="30"):
    vacancy_stats = {}
    payload = {"period": period, "area": area , "page":0}
    for language in programming_languages:
        payload["text"] = "Программист {}".format(language)
        language_stat = predict_rub_salary_hh(payload)
        vacancy_stats[language] = language_stat
    return vacancy_stats


def get_response(url, params, headers):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    response = response.json()
    return response


def predict_rub_salary_hh(payload):
    language_salary = []
    page = 0
    url = "https://api.hh.ru/vacancies"
    headers = {"User-Agent": "HH-User-Agent"}
    response = get_response(url, payload, headers)
    pages = response["pages"]
    vacancy_numbers = response["found"]
    while page < pages:
        vacancies = response["items"]
        for vacancy in vacancies:
            salary = vacancy["salary"]
            if not salary:
                continue
            elif salary["currency"] != "RUR":
                continue
            salary_from = salary["from"]
            salary_to = salary["to"]
            average_salary = int(predict_salary(salary_from, salary_to))
            if average_salary:
                language_salary.append(average_salary)
        page += 1
    vacancies_info = {"vacancies_found": vacancy_numbers,
                      "vacancies_processed": len(language_salary),
                      "average_salary" :int(sum(language_salary)/len(language_salary))
                     }
    return vacancies_info


def predict_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        return salary_from * 1.2
    elif not salary_from and salary_to:
        return salary_to * 0.8
    elif salary_from and salary_to:
        return (salary_to + salary_from) / 2


def get_super_job_vacancies(programming_languages, super_job_key, town_id=4, catalogues=48):
    vacancy_stats = {}
    payload = {"town": town_id, "catalogues": catalogues , "page": 0, "count":100}
    for language in programming_languages:
        payload["keyword"] = language
        language_stat = predict_rub_salary_sj(payload, super_job_key)
        vacancy_stats[language] = language_stat
    return vacancy_stats


def predict_rub_salary_sj(payload, super_job_key):
    language_salary = []
    headers = {"X-Api-App-Id": super_job_key}
    url = "https://api.superjob.ru/2.0/vacancies/"
    page = 0
    response = get_response(url, payload, headers)
    vacancy_numbers = response["total"]
    pages = vacancy_numbers // 100 +1
    while page < pages:
        vacancies = response["objects"]
        for vacancy in vacancies:
            if not vacancy:
                continue
            elif vacancy["currency"] != "rub":
                continue
            average_salary = 0
            salary_from = vacancy["payment_from"]
            salary_to = vacancy["payment_to"]
            predicted_salary = predict_salary(salary_from, salary_to)
            if predicted_salary:
                average_salary = int(predicted_salary)
            if average_salary:
                language_salary.append(average_salary)
        page += 1
    vacancies_info = {"vacancies_found": vacancy_numbers,
                      "vacancies_processed": len(language_salary),
                      "average_salary": int(sum(language_salary) / len(language_salary))
                     }
    return vacancies_info


def create_table(vacancies_information, title):
    table_data = [
        ["Язык программирования", "Найдено вакансий", "Обработано вакансий", "Средняя зарплата"]
    ]
    for language, vacancies_info in vacancies_information.items():
        table_data.append([language, vacancies_info["vacancies_found"],
                           vacancies_info["vacancies_processed"],
                           vacancies_info["average_salary"]])
    table_instance = DoubleTable(table_data, title)
    return table_instance.table


def main():
    load_dotenv()
    super_job_key = os.getenv("SUPERJOB_API_SECRET_KEY")
    programming_languages = ["Python", "C", "C++", "Java",
                             "JavaScript", "PHP", "C#",
                             "Swift", "Scala", "Go"]
    hh_vacancies_info = get_hh_vacancies(programming_languages)
    sp_vacancies_info = get_super_job_vacancies(programming_languages, super_job_key)
    print(create_table(hh_vacancies_info, "HeadHunter Moscow"))
    print(create_table(sp_vacancies_info, "SuperJob Moscow"))


if __name__ == "__main__":
     main()