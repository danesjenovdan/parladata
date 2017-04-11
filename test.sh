#!/bin/bash

cd "/home/parladaddy/parladata"
source  "venv/bin/activate"
python manage.py runscript test > test.log 2>&1 &&
deactivate

echo "End test"
