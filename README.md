# parladata
parladata

# setup with croatian database
* docker-compose build
* docker-compose up -d
* docker-compose exec parladata python manage.py download_and_set_database

# setup with minimal setup
* docker-compose build
* docker-compose up -d
* docker-compose exec parladata python manage.py migrate
* docker-compose exec parladata python manage.py min_seed

user for login: parlauser:password


