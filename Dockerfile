FROM python:3.8
RUN apt-get update && apt-get install --yes postgresql-client
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install -r requirements_3.txt
EXPOSE 8000
