![Build Status](https://github.com/VOVSn/foodgram/actions/workflows/main.yml/badge.svg)
[![Python Version](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Django](https://img.shields.io/badge/django-3.2.3-green.svg)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/drf-3.12.4-blueviolet.svg)](https://www.django-rest-framework.org/)
[![Gunicorn](https://img.shields.io/badge/gunicorn-20.1.0-green.svg)](https://gunicorn.org/)


### Описание проекта:

  Данный проект является обучающим проектом по работе с Django REST Framework с практикой разворачивания в контейнерах Docker и CI/CD автоматизации.

### Автор проекта:

  Данный проект был разработан [Vladimir Korolev](https://github.com/VOVSn)

  Рабочая версия проекта доступна по адресу:

  [FOODSocialNetwork](https://foodgram.vovsn.com) foodgram.vovsn.com

  API документация к проекту доступна по адресу:

  [Redoc документация Фудграм](https://foodgram.vovsn.com/api/docs/)


### Использованные технологии:

  В данном проекте используются технологии:

  [Django](https://www.djangoproject.com/)

  [Django rest framework](https://www.django-rest-framework.org/)

  Для промышленной реализации проекта используются:

  [Gunicorn](https://docs.gunicorn.org/en/stable/index.html)

  [Nginx](https://nginx.org/en/docs/)

  Для контейнеризации и сборки образов используются:

  [Docker](https://docs.docker.com/manuals/)

  [Docker HUB](https://docs.docker.com/docker-hub/)

  Для автоматизации CI/CD используются:

  [Git Hub Actions](https://docs.github.com/ru/actions/about-github-actions/understanding-github-actions)



### В бэкэнде проекта использовались следующие библиотеки:
  Django, djangorestframework, djoser, Pillow, psycopg2-binary, PyJWT,
  python-dotenv PyYAML.
  версии библиотек а также остальные зависимости указаны в requirements.txt

### Переменные окружения:

  Для работы проекта необходим файл (.env) с переменными окружения следующего вида:
```
  POSTGRES_DB=<name>

  POSTGRES_USER=<db_user>

  POSTGRES_PASSWORD=<db_password>

  DB_HOST=<db_container_name>

  DB_PORT=5432

  SECRET_KEY="django-insecure-secret-key-example-12345"

  ALLOWED_HOSTS=<domain_name.tld>, <IP>

  DOMAIN="localhost"

  DEBUG=True

  DB_ENGINE=PG
```
### Как запустить проект локально:

  Клонировать репозиторий и перейти в него в командной строке:

  ```
  git clone git@github.com:vovsn/foodgram.git
  ```

  ```
  cd foodgram
  ```

  Cоздать и активировать виртуальное окружение:

  ```
  python -m venv env
  ```

  ```
  source env/bin/activate
  ```

  Установить зависимости из файла requirements.txt:

  ```
  python -m pip install --upgrade pip
  ```

  ```
  pip install -r requirements.txt
  ```

  Выполнить миграции:

  ```
  python manage.py migrate
  ```

  Запустить проект:
  ```
  python manage.py runserver
  ```
  Импортировать данные таблицы ингредиентов:
  ```
  python manage.py import_csv_data
  ```

### Как запустить проект в контейнерах:

  ```
  cd infra
  docker compose up -d
  ```
### Для промышленного запуска проекта необходимо:

  Скачать последние образы с DocherHub:
  ```
  docker compose -f docker-compose.production.yml pull
  ```

  Остановить текущие рабочие контейнеры и удалить их:
  ```
  docker compose -f docker-compose.production.yml down
  ```

  Запустить проект:
  ```
  docker compose -f docker-compose.production.yml up -d
  ```

  Применить миграции:
  ```
  docker compose -f docker-compose.production.yml exec backend python manage.py migrate
  ```

  Собрать статику:
  ```
  docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic 
  ```

  Импортировать данные таблицы ингредиентов:
  ```
  docker compose -f docker-compose.production.yml exec backend python manage.py import_csv_data
  ```



###
# Примеры запросов:

### Получение списка recipes:

```
curl -X GET \
  http://foodgram.vovsn.com/api/recipes/
```
### Пример ответа:

```
{
  "count": 123,
  "next": "http://foodgram.vovsn.com/api/recipes/?page=4",
  "previous": "http://foodgram.vovsn.com/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://foodgram.vovsn.com/media/users/image.png"
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.vovsn.com/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```
