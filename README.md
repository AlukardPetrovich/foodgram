![test_and_deploy](https://github.com/AlukardPetrovich/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)

# project "Foodgram"

Продуктовый помошник для обмена рецептами, подписками на интересных авторов и составления списка покупок

## Стэк технологий:
Python, Django, Django_rest_framework, Docker, Docker_compose, Github actions, Yandex cloud.

## Запуск на удаленном сервере
Слонируйте проект(потребуется только папка "infra"):
```
git clone git@github.com:AlukardPetrovich/foodgram-project-react.git
```
Создайте и призведите начальную конфигурацию удаленного сервера. скопируйте файлы из папки "infra" в домашнюю папку на удаленном сервере:
```
scp infra/* <имя_пользователя>@<IP сервера>:/home/<имя_пользователя>/
```
подключитесь к нему по SSH:
```
ssh <имя_пользователя>@<IP сервера>
```
Создайте файл с переменными окружения:
```
nano .env
```
и внесите в него все необходимые переменные окружения:
```
SECRET_KEY=<ваш_секретный_ключ_django>
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
ALLOWED_HOSTS='127.0.0.1 <IP сервера>'
``` 
установите Docker:
```
sudo apt install docker.io
```
установите [Docker-compose](https://docs.docker.com/compose/install/) в соответствии с ОС сервера

Разверните проект используя Docker compose:
```
sudo docker-compose up -d --build
```
Выполните миграции, соберите статику и создайте суперпользователя:
```
sudo docker exec  <name или id контейнера backend> python manage.py migrate
```
```
sudo docker exec  <name или id контейнера backend> python manage.py collectstatic
```
```
sudo docker exec  <name или id контейнера backend> python manage.py createsuperuser
```

## Доступность проекта
На текущий момент проект запущен и [доступен](http://foodgram.ddns.net/signin)

Также доступна [админка](http://foodgram.ddns.net/admin/login/?next=/admin/)

Данные для входа в админку:
Login:
```
Super
```
Password:
```
posma2-Gumgeg-gumrer
```



