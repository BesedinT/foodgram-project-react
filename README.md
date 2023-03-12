# Foodgram - Продуктовый помощник

![example workflow](https://github.com/BesedinT/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание проекта

Foodgram это ресурс для публикации рецептов.  
Пользователи могут создавать свои рецепты, читать рецепты других пользователей, подписываться на интересных авторов, добавлять лучшие рецепты в избранное, а также создавать список покупок и загружать его в txt формате

Функционал проекта адаптирован для использования PostgreSQL и развертывания в контейнерах Docker. Используются инструменты CI и CD

Проект запущен и доступен по [адресу](http://foodgram.myddns.me)

## Стек технологий

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)

## Запуск проекта

- Склонируйте репозитрий на свой компьютер 

- Выполните вход на удаленный сервер  

- Установите docker на сервер:  

`$ sudo apt install docker.io`  

- Установить docker-compose на сервер согласно [документации](https://docs.docker.com/compose/install/)

- Скопируйте файлы docker-compose.yml, nginx.conf из директории infra и статику redoc на сервер:

`$ scp docker-compose.yml <username>@<host>:/home/<username>/`   
`$ scp nginx.conf <username>@<host>:/home/<username>/`  
`$ scp -r /docs/ <username>@<host>:/home/<username>/`

- Для работы с Workflow необходимо добавить в GitHub Actions secrets переменные окружения для работы:
    >DB_ENGINE = django.db.backends.postgresql  
    >DB_NAME = # название БД  
    >POSTGRES_USER = # ваше имя пользователя  
    >POSTGRES_PASSWORD = # пароль для доступа к БД  
    >DB_HOST = db  
    >DB_PORT = 5432 
     
    >SECRET_KEY = '# Django SECRET_KEY'  
    
    >DOCKER_USERNAME = # имя пользователя на DockerHub  
    >DOCKER_PASSWORD = # пароль DockerHub  
    
    >USER = # имя пользователя на удаленном сервере  
    >HOST = # IP удаленного сервера  
    >PASSPHRASE = # пароль ssh-ключа  
    >SSH_KEY = # SSH ключ (для получения выполните команду на локальном компьютере: cat ~/.ssh/id_rsa) 
    
    >TELEGRAM_TO = # ID чата, в который придет сообщение о выполнении Workflow  
    >TELEGRAM_TOKEN = # токен вашего бота
    
    >ALLOWED_HOSTS = # имена используемых хостов/доменов (добавьте значение: web) 
    >DEBUG = # параметр DEBUG файла settings.py (FALSE или TRUE, параметр допустимо не указывать, значение по умолчанию - FALSE)  
    

- Workflow запускается после каждого пуша проекта на GitHub и состоит из четырёх шагов:
     - проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
     - cборка и доставка докер-образа для контейнера web на Docker Hub
     - автоматический деплой проекта на удаленный сервер
     - отправка уведомления в Telegram о том, что процесс деплоя успешно завершился 

- Последующие действия выполняются на удаленном сервере после успешного деплоя   

- Выполните миграции   

`$ sudo docker-compose exec backend python manage.py makemigrations`    
`$ sudo docker-compose exec backend python manage.py migrate`  

- Соберите статику     

`$ sudo docker-compose exec backend python manage.py collectstatic --no-input`    

- Для доступа к админке не забудьте создать суперюзера  

`$ sudo docker-compose exec backend python manage.py createsuperuser`  

- Загрузите ингредиенты и тэги в базу данных командой:

`$ sudo docker-compose exec backend python manage.py import_data`

__________________________________

Проект запустится на http://{IP адрес удаленного сервера}/   

Полная документация доступна по адресу http://{IP адрес удаленного сервера}/api/docs/

## Автор backend'а:

Анатолий Беседин

GitHub: https://github.com/BesedinT  
