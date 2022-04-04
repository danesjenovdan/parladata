import pytest
import json
import io

from export.views import *

from rest_framework.test import APIClient

client = APIClient()

# testing:
# does endpoint return a successful response (status 200)
# does endpoint return the correct content type
# does response content contain correct fields
# does endpoint return 404 for wrong format or no format

# --- ExportVotesView ---

@pytest.mark.django_db()
def test_export_votes_csv():
    response = client.get('/v3/data/export-votes.csv')
    # successful response
    assert response.status_code == 200
    # correct response type
    assert response.headers['content-type'] == 'text/csv'
    # containts correct fields
    content = response.getvalue()
    lines = content.splitlines()
    headers = lines[0].decode("utf-8").split(',')
    assert 'id' in headers
    assert 'name' in headers
    assert 'motion__text' in headers
    assert 'motion__summary' in headers
    assert 'result' in headers

@pytest.mark.django_db()
def test_export_votes_json_status():
    response = client.get('/v3/data/export-votes.json')
    # successful response
    assert response.status_code == 200
    # correct response type
    assert response.headers['content-type'] == 'application/json'
    # containts correct fields
    content = json.loads(response.getvalue())
    if len(content) > 0:
        json_keys = content[0].keys()
        assert 'id' in json_keys
        assert 'name' in json_keys
        assert 'motion__text' in json_keys
        assert 'motion__summary' in json_keys
        assert 'result' in json_keys

@pytest.mark.django_db()
def test_export_votes_wrong_format():
    response = client.get('/v3/data/export-votes.xslx')
    assert response.status_code == 404

@pytest.mark.django_db()
def test_export_votes_no_format():
    response = client.get('/v3/data/export-votes')
    assert response.status_code == 404


# --- ExportParliamentMembersView ---

@pytest.mark.django_db()
def test_export_parliament_members_csv_status():
    response = client.get('/v3/data/export-parliament-members.csv')
    # successful response
    assert response.status_code == 200
    # correct response type
    assert response.headers['content-type'] == 'text/csv'
    # containts correct fields
    content = response.getvalue()
    lines = content.splitlines()
    headers = lines[0].decode("utf-8").split(',')
    assert 'id' in headers
    assert 'name' in headers
    assert 'date_of_birth' in headers
    assert 'age' in headers
    assert 'education_level' in headers
    assert 'preferred_pronoun' in headers
    assert 'number_of_mandates' in headers

@pytest.mark.django_db()
def test_export_parliament_members_json_status():
    response = client.get('/v3/data/export-parliament-members.json')
    # successful response
    assert response.status_code == 200
    # correct response type
    assert response.headers['content-type'] == 'application/json'
    # containts correct fields
    content = json.loads(response.getvalue())
    if len(content) > 0:
        json_keys = content[0].keys()
        assert 'id' in json_keys
        assert 'name' in json_keys
        assert 'date_of_birth' in json_keys
        assert 'age' in json_keys
        assert 'education_level' in json_keys
        assert 'preferred_pronoun' in json_keys
        assert 'number_of_mandates' in json_keys

@pytest.mark.django_db()
def test_export_parliament_members_wrong_format():
    response = client.get('/v3/data/export-parliament-members.xslx')
    assert response.status_code == 404

@pytest.mark.django_db()
def test_export_parliament_members_no_format():
    response = client.get('/v3/data/export-parliament-members')
    assert response.status_code == 404
