# job_hunter
Небольшое приложение, собирающее информацию с [HeadHunter](https://hh.ru/) и [SuperJob](https://www.superjob.ru/).
Выводит информацию по нескольким языкам программирования( можно поменять ) - средняя зарплата, количество ваканский,
сколько вакансий обработано. Вся информация собирается по Москве( можно поменять ).
### Как запустить
* Для запуска сайта вам понадобится Python третьей версии.
* Скачайте код с GitHub. Затем установите зависимости
```sh
pip install -r requirements.txt
```
* Создайте файл `.env` в директории с проектом.
* Заполните `.env` следующими переменными:
  `SUPERJOB_API_SECRET_KEY="KEY"` - `KEY`, Ключ для api [SuperJob](https://api.superjob.ru/#password)
  
Для получения `SUPERJOB_API_SECRET_KEY` перейдите по ссылке [SuperJob](https://api.superjob.ru/#password) и
ознакомьтесь с документаций, в ней содержится инструкция.
* Запустите код
```sh
python main.py
```
### Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/modules/).

