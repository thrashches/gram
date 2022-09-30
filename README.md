# praktikum_new_diplom

Проект FOODGRAM
[![foodgram_workflow](https://github.com/brigantesco/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg?branch=master)](https://github.com/brigantesco/foodgram-project-react/actions/workflows/foodgram.yml)
Проект находится по адресу: 
84.252.129.8

Описание:
Онлайн и API сервис для публикации рецептов, можно добавлять понравившиеся рецепты и скачивать список продуктов для них, 
подписываться на других пользователей.

Технологии:
Python, Django, PostgreSQL, Docker, Docker-Compose, Nginx, Gunicorn

Как запустить проект:
- Скачать проект: https://github.com/brigantesco/foodgram-project-react
- Зайдите на свой сервер с помощью ssh-соединения
- Обновите систему: sudo apt upgrade -y 
- Установите менеджер пакетов pip, утилиту для создания виртуального окружения venv, систему контроля версий git: sudo apt install python3-pip python3-venv git -y
- Установите Docker: sudo apt install docker.io
- Установите Docker-Compose: sudo apt install docker-compose
- Скопируйте файлы docker-compose.yaml и nginx.conf из вашего проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx.conf
- Для работы с БД  PostgreSQL понадобятся следующие настройки:
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=127.0.0.1
    DB_PORT=5432
- Запустить проект: sudo docker-compose up -d

Автор:
Ястребов Андрей

Лицензия: 
MIT