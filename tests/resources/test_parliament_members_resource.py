import pytest
import json

from export.resources import *

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_export_as_generator_json():
    resource = MPResource()
    generator = resource.export_as_generator_json()
    chunks = list(generator)
    chunks_joined = ''.join(chunks)
    res = json.loads(chunks_joined)
    # check num of results
    assert len(res) == 43
    # check keys
    json_keys = res[0].keys()
    assert 'id' in json_keys
    assert 'name' in json_keys
    assert 'date_of_birth' in json_keys
    assert 'age' in json_keys
    assert 'education_level' in json_keys
    assert 'preferred_pronoun' in json_keys
    assert 'number_of_mandates' in json_keys
    
@pytest.mark.django_db()
def test_export_as_generator_csv():
    resource = MPResource()
    generator = resource.export_as_generator_csv()
    chunks = list(generator)
    chunks_joined = ''.join(chunks)
    lines = chunks_joined.splitlines()
    headers = lines[0].split(',')
    # check num of results
    assert len(lines) == 45 # len(results) + headers + empty line
    # check headers
    assert 'id' in headers
    assert 'name' in headers
    assert 'date_of_birth' in headers
    assert 'age' in headers
    assert 'education_level' in headers
    assert 'preferred_pronoun' in headers
    assert 'number_of_mandates' in headers 