# parladata
parladata

# setup with croatian database
* docker-compose build
* docker-compose up -d
* docker-compose exec parladata python manage.py migrate
* docker-compose exec parladata python manage.py download_and_set_database
