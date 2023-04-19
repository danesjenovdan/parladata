import pytest
import json

from export.resources import *

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_export_as_generator_json(first_mandate):
    resource = GroupDiscordResource()
    generator = resource.export_as_generator_json(mandate_id=first_mandate.id)
    chunks = list(generator)
    chunks_joined = ''.join(chunks)
    res = json.loads(chunks_joined)
    # check num of results
    assert len(res) == 7
    # check keys
    json_keys = res[0].keys()
    assert 'name' in json_keys
    assert 'value' in json_keys
    assert 'timestamp' in json_keys

@pytest.mark.django_db()
def test_export_as_generator_csv(first_mandate):
    resource = GroupDiscordResource()
    generator = resource.export_as_generator_csv(mandate_id=first_mandate.id)
    chunks = list(generator)
    chunks_joined = ''.join(chunks)
    lines = chunks_joined.splitlines()
    headers = lines[0].split(',')
    # check num of results
    assert len(lines) == 9 # len(results) + headers + empty line
    # check headers
    assert 'name' in headers
    assert 'value' in headers
    assert 'timestamp' in headers
