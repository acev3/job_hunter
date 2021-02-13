import requests
import os
from dotenv import load_dotenv
from terminaltables import DoubleTable


def get_hh_vacancies(programming_languages, area="1", period="30"):
    vacancy_stats = {}
    url = "https://api.hh.ru/vacancies"
    headers = {"User-Agent": "HH-User-Agent"}
    payload = {"period": period, "area": area, "page": 0}
    for language in programming_languages:
        payload["text"] = "Программист {}".format(language)
        language_stat = predict_rub_salary_hh(url, payload, headers)
        vacancy_stats[language] = language_stat
    return vacancy_stats


def get_response(url, params, headers):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    response = response.json()
    return response


def predict_rub_salary_hh(url, payload, headers):
    language_salary = []
    page = 0
    vacancies_amount = 0
    pages_number = 1
    while page < pages_number:
        payload["page"] = page
        response = get_response(url, payload, headers)
        pages_number = response["pages"]
        vacancies = response["items"]
        vacancies_amount += len(vacancies)
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
    average_salary = int(sum(language_salary) / len(language_salary)) if len(language_salary) else 0
    hh_vacancies = {"vacancies_found": vacancies_amount,
                    "vacancies_processed": len(language_salary),
                    "average_salary": average_salary
                    }
    return hh_vacancies


def predict_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        return salary_from * 1.2
    elif not salary_from and salary_to:
        return salary_to * 0.8
    elif salary_from and salary_to:
        return (salary_to + salary_from) / 2


def get_super_job_vacancies(programming_languages, super_job_key,
                            town_id=4, catalogues=48):
    vacancy_stats = {}
    headers = {"X-Api-App-Id": super_job_key}
    url = "https://api.superjob.ru/2.0/vacancies/"
    payload = {"town": town_id, "catalogues": catalogues,
               "page": 0, "count": 100
               }
    for language in programming_languages:
        payload["keyword"] = language
        language_stat = predict_rub_salary_sj(url, payload, headers)
        vacancy_stats[language] = language_stat
    return vacancy_stats


def predict_rub_salary_sj(url, payload, headers):
    language_salary = []
    page = 0
    pages_number = 1
    while page < pages_number:
        payload["page"] = page
        response = get_response(url, payload, headers)
        vacancies_amount = response['total']
        pages_number = vacancies_amount // 100 + 1
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
        if not response["more"]:
            break
    average_salary = int(sum(language_salary) / len(language_salary)) if len(language_salary) else 0
    sj_vacancies = {"vacancies_found": vacancies_amount,
                    "vacancies_processed": len(language_salary),
                    "average_salary": average_salary
                    }
    return sj_vacancies


def create_table(vacancies_information, title):
    table_data = [
        ["Язык программирования", "Найдено вакансий",
         "Обработано вакансий", "Средняя зарплата"
         ]
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
    hh_vacancies = get_hh_vacancies(programming_languages)
    sp_vacancies = get_super_job_vacancies(programming_languages,
                                           super_job_key
                                           )
    print(create_table(hh_vacancies, "HeadHunter Moscow"))
    print(create_table(sp_vacancies, "SuperJob Moscow"))


if __name__ == "__main__":
    main()
