# Foodgram
## Приложение «Продуктовый помощник»
[![Django-app workflow](https://github.com/Vladimir-spb/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/Vladimir-spb/foodgram-project-react/actions/workflows/foodgram_workflow.yml)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=008080)](https://cloud.yandex.ru/)

## Развёрнутый проект
http://158.160.12.99


## Описание проекта

### Главная страница
Содержимое главной страницы — список первых шести рецептов,
отсортированных по дате публикации (от новых к старым).
Остальные рецепты доступны на следующих страницах: внизу страницы есть пагинация.
### Страница рецепта
На странице — полное описание рецепта. Для авторизованных пользователей — 
возможность добавить рецепт в избранное и в список покупок, возможность
подписаться на автора рецепта.
### Страница пользователя
На странице — имя пользователя, все рецепты, опубликованные пользователем
и возможность подписаться на пользователя.

## Техническое описание проекта

В проекте реализован _**API**_-**сервис** для аутентификации пользователей и работы со всеми ресурсами.

Увидеть полную спецификацию API вы сможете развернув проект локально http://127.0.0.1/api/docs/ или на вашем хосте.

## Описание Workflow

Workflow состоит из четырёх шагов:
1. Проверка кода на соответствие PEP8;
2. Сборка и публикация образа на DockerHub;
3. Автоматический деплой на удаленный сервер;
4. Отправка telegram-ботом уведомления в чат.

## Установка:
1. Клонируйте репозиторий на локальную машину.
   ```https://github.com/Vladimir-spb/foodgram-project-react```
2. Установите виртуальное окружение в папке проекта.
```
python -m venv venv
```

3. Активируйте виртуальное окружение.
   ``` .venv\Scripts\activate```
4. Установите зависимости.
```
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```
## Запуск проекта в контейнерах
1. Выполните команду:
   ```docker-compose up -d --build```
2. Для остановки контейнеров из директории `infra/` выполните команду:
   ```docker-compose down -v```

В репозитории на Гитхабе добавьте данные в `Settings - Secrets - Actions secrets`:
```
DOCKER_USERNAME - имя пользователя в DockerHub
DOCKER_PASSWORD - пароль пользователя в DockerHub
HOST - ip-адрес сервера
USER - пользователь
SSH_KEY - приватный ssh-ключ
PASSPHRASE - кодовая фраза для ssh-ключа
SECRET_KEY - секретный ключ приложения django
ALLOWED_HOSTS - список разрешённых адресов
TELEGRAM_TO - id своего телеграм-аккаунта
TELEGRAM_TOKEN - токен бота
DB_NAME - postgres (по умолчанию)
DB_ENGINE - django.db.backends.postgresql
DB_HOST - db (по умолчанию)
DB_PORT - 5432 (по умолчанию)
POSTGRES_USER - postgres (по умолчанию)
POSTGRES_PASSWORD - postgres (по умолчанию)
```

### Подготовка сервера

Остановите службу nginx:
```
sudo systemctl stop nginx 
```
Установите docker и docker-compose:
```
sudo apt install docker.io
sudo apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh 
sudo apt install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" 
sudo apt install docker-ce docker-compose -y
```
Community Edition (CE) — бесплатная и общедоступная версия - Она идеально подходит для решения базовых задач по контейнеризации

Скопируйте файлы docker-compose.yaml и nginx.conf из вашего проекта на сервер в home/<ваш_username>/

### После успешного деплоя последовательно выполнить:

 a) sudo docker-compose exec backend python manage.py makemigrations
 b) sudo docker-compose exec backend python manage.py migrate
 c) sudo docker-compose exec backend python manage.py createsuperuser
 d) sudo docker-compose exec backend python manage.py collectstatic --no-input

### Загрузка ингредиентов из CSV- файла:
sudo docker-compose exec backend python manage.py loading_ingredients

### Работа с fixture:
## Для создания дампа (резервной копии) необходимо выполнить команду: 
- docker-compose exec backend python manage.py dumpdata > fixtures.json
## Для загрузки:
- docker-compose exec backend python manage.py loaddata fixtures.json


## Автор:
Коршак Владимир