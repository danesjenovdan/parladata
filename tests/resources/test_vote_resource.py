import pytest
import json

from export.resources import *

from tests.fixtures.common import *

# resource = ExportModelResource()
# queryset = Vote.objects.get_queryset()
# exported = resource.export_as_generator_json()

@pytest.mark.django_db()
def test_export_as_generator_json():
    resource = VoteResource()
    generator = resource.export_as_generator_json()
    chunks = list(generator)
    chunks_joined = ''.join(chunks)
    res = json.loads(chunks_joined)
    # check num of results
    assert len(res) == 37
    # check keys
    json_keys = res[0].keys()
    assert 'id' in json_keys
    assert 'name' in json_keys
    assert 'motion__text' in json_keys
    assert 'motion__summary' in json_keys
    assert 'result' in json_keys

@pytest.mark.django_db()
def test_export_as_generator_csv():
    resource = VoteResource()
    generator = resource.export_as_generator_csv()
    chunks = list(generator)
    chunks_joined = ''.join(chunks)
    lines = chunks_joined.splitlines()
    headers = lines[0].split(',')
    # check num of results
    assert len(lines) == 39 # len(results) + headers + empty line
    # check headers
    assert 'id' in headers
    assert 'name' in headers
    assert 'motion__text' in headers
    assert 'motion__summary' in headers
    assert 'result' in headers