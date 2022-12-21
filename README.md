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

# Editing the test database

First flush your data (warning, irreversible deletion) with `python manage.py flush`, then import the test database
with `python manage.py loaddata tests/fixtures/test_db.json`. Edit the database as you see fit, then save it to a
json file with `python manage.py dumpdata -e contenttypes -e auth.permission -o tests/fixtures/test_db.json`. This will save it directly to the
appropriate folder.

## Special cases that should not be overwritten
- vote id 37 contains only anonymous ballots
- vote id 36 contains some anonymous ballots
- vote id 35 contains no ballots at all
