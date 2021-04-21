# we have to use python 3.8 since Lemmagen does not support 3.9
FROM python:3.8

RUN apt-get update && \
    apt-get upgrade -y

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=parlalize.settings.k8s

CMD python manage.py runserver 0.0.0.0:8000


# FROM python:3.8
# RUN apt-get update && apt-get install --yes postgresql-client
# RUN mkdir /app
# WORKDIR /app
# COPY . /app
# RUN pip install -r requirements.txt
# EXPOSE 8000
