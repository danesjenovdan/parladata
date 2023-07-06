import pytest
import json

from tests.fixtures.common import *
from export.resources.group import *

class GroupResourceExportTest:
    resource = None
    headers = ['name', 'value', 'timestamp']
    csv_results_count = 3
    json_results_count = 1

    @pytest.mark.django_db()
    def test_export_as_generator_json(self, first_mandate, first_group):
        resource = self.resource()
        generator = resource.export_as_generator_json(
            mandate_id=first_mandate.id,
            request_id=first_group.id
        )
        chunks = list(generator)
        chunks_joined = ''.join(chunks)
        res = json.loads(chunks_joined)
        # check num of results
        assert len(res) == self.json_results_count
        # check keys
        if self.json_results_count > 0:
            json_keys = res[0].keys()

            for header in self.headers:
                assert header in json_keys

    @pytest.mark.django_db()
    def test_export_as_generator_csv(self, first_mandate, first_group):
        resource = self.resource()
        generator = resource.export_as_generator_csv(
            mandate_id=first_mandate.id,
            request_id=first_group.id
        )
        chunks = list(generator)
        chunks_joined = ''.join(chunks)
        lines = chunks_joined.splitlines()
        headers = lines[0].split(',')
        # check num of results
        assert len(lines) == self.csv_results_count # len(results) + headers + empty line
        # check headers
        for header in self.headers:
            assert header in headers


class TestGroupDiscordResource(GroupResourceExportTest):
    resource = GroupDiscordResource
    csv_results_count = 3
    json_results_count = 1


class TestGroupVocabularySizeResource(GroupResourceExportTest):
    resource = GroupVocabularySizeResource
    csv_results_count = 3
    json_results_count = 1


class TestGroupNumberOfQuestionsResource(GroupResourceExportTest):
    resource = GroupNumberOfQuestionsResource
    csv_results_count = 3
    json_results_count = 1


class TestGroupMonthlyVoteAttendanceResource(GroupResourceExportTest):
    resource = GroupMonthlyVoteAttendanceResource
    csv_results_count = 4
    json_results_count = 2


class TestGroupVoteAttendanceResource(GroupResourceExportTest):
    resource = GroupVoteAttendanceResource
    csv_results_count = 3
    json_results_count = 1


class TestGroupVotesInCommonResource(GroupResourceExportTest):
    resource = GroupVotesInCommonResource
    csv_results_count = 2
    json_results_count = 0
    headers = ['name', 'target_person', 'value', 'timestamp']


class TestGroupTfidfResource(GroupResourceExportTest):
    resource = GroupTfidfResource
    csv_results_count = 2
    json_results_count = 0
    headers = ['name', 'token', 'value', 'timestamp']


class TestGroupStyleScoresResource(GroupResourceExportTest):
    resource = GroupStyleScoresResource
    csv_results_count = 2
    json_results_count = 0
    headers = ['name', 'style', 'value', 'timestamp']


class TestGroupInfoResource(GroupResourceExportTest):
    resource = GroupInfoResource
    csv_results_count = 3
    json_results_count = 1
    headers = ['name', 'acronym', 'email','facebook', 'twitter']


class TestGroupMembersResource(GroupResourceExportTest):
    resource = GroupMembersResource
    csv_results_count = 6
    json_results_count = 4
    headers = ['name', 'role', 'organization', 'on_behalf_of', 'start_time', 'end_time', 'mandate']


class TestGroupDeviationFromGroupResource(GroupResourceExportTest):
    resource = GroupDeviationFromGroupResource
    csv_results_count = 3
    json_results_count = 1
