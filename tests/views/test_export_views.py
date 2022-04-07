import pytest
import json

from export.views import *

from rest_framework.test import APIClient

client = APIClient()

# testing:
# does endpoint return a successful response (status 200)
# does endpoint return the correct content type
# does response content contain correct fields
# does endpoint return 404 for wrong format or no format
# does endpoint return empty file for non-existing mandate

# --- ExportVotesView ---

@pytest.mark.django_db()
def test_export_votes_csv():
    response = client.get('/v3/export/mandate/1/votes.csv')
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
def test_export_votes_json():
    response = client.get('/v3/export/mandate/1/votes.json')
    # successful response
    assert response.status_code == 200
    # correct response type
    assert response.headers['content-type'] == 'application/json'
    # containts correct fields
    content = json.loads(response.getvalue())
    json_keys = content[0].keys()
    assert 'id' in json_keys
    assert 'name' in json_keys
    assert 'motion__text' in json_keys
    assert 'motion__summary' in json_keys
    assert 'result' in json_keys

@pytest.mark.django_db()
def test_export_votes_wrong_format():
    response = client.get('/v3/export/mandate/1/votes.xslx')
    assert response.status_code == 404

@pytest.mark.django_db()
def test_export_votes_no_format():
    response = client.get('/v3/export/mandate/1/votes')
    assert response.status_code == 404

@pytest.mark.django_db()
def test_export_votes_json_wrong_mandate():
    response = client.get('/v3/export/mandate/2/votes.json')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    content = json.loads(response.getvalue())
    assert content == []

@pytest.mark.django_db()
def test_export_votes_csv_wrong_mandate():
    response = client.get('/v3/export/mandate/2/votes.csv')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/csv'
    content = response.getvalue()
    lines = content.splitlines()
    assert len(lines) == 2 # headers and empty line
    headers = lines[0].decode("utf-8").split(',')
    assert 'id' in headers
    assert 'name' in headers
    assert 'motion__text' in headers
    assert 'motion__summary' in headers
    assert 'result' in headers


# --- ExportParliamentMembersView ---

@pytest.mark.django_db()
def test_export_parliament_members_csv():
    response = client.get('/v3/export/mandate/1/parliament-members.csv')
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
def test_export_parliament_members_json():
    response = client.get('/v3/export/mandate/1/parliament-members.json')
    # successful response
    assert response.status_code == 200
    # correct response type
    assert response.headers['content-type'] == 'application/json'
    # containts correct fields
    content = json.loads(response.getvalue())
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
    response = client.get('/v3/export/mandate/1/parliament-members.xslx')
    assert response.status_code == 404

@pytest.mark.django_db()
def test_export_parliament_members_no_format():
    response = client.get('/v3/export/mandate/1/parliament-members')
    assert response.status_code == 404

@pytest.mark.django_db()
def test_export_parliament_members_json_wrong_mandate():
    response = client.get('/v3/export/mandate/2/parliament-members.json')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    content = json.loads(response.getvalue())
    assert content == []

@pytest.mark.django_db()
def test_export_parliament_members_csv_wrong_mandate():
    response = client.get('/v3/export/mandate/2/parliament-members.csv')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/csv'
    content = response.getvalue()
    lines = content.splitlines()
    assert len(lines) == 2 # headers and empty line
    headers = lines[0].decode("utf-8").split(',')
    assert 'id' in headers
    assert 'name' in headers
    assert 'date_of_birth' in headers
    assert 'age' in headers
    assert 'education_level' in headers
    assert 'preferred_pronoun' in headers
    assert 'number_of_mandates' in headers
