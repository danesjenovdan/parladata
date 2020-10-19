FROM python:3.7
RUN apt-get update
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install -r requirements_3.txt
EXPOSE 8000
