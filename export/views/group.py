from export.resources.group import (
    GroupDiscordResource,
    GroupVocabularySizeResource,
    GroupNumberOfQuestionsResource,
    GroupMonthlyVoteAttendanceResource,
    GroupVoteAttendanceResource,
    GroupVotesInCommonResource,
    GroupTfidfResource,
)
from export.views.common import ExportResourceView


class ExportGroupDiscord(ExportResourceView):
    """
    Export group's discord from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "group_discord"
    resource = GroupDiscordResource()


class ExportGroupVocabularySize(ExportResourceView):
    """
    Export group's vocabulary size from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "group_vocabulary_size"
    resource = GroupVocabularySizeResource()


class ExportGroupNumberOfQuestions(ExportResourceView):
    """
    Export group's number of questions from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "group_number_of_questions"
    resource = GroupNumberOfQuestionsResource()


class ExportGroupMonthlyVoteAttendance(ExportResourceView):
    """
    Export group's monthly vote attendance from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "group_monthly_vote_attendance"
    resource = GroupMonthlyVoteAttendanceResource()


class ExportGroupVoteAttendance(ExportResourceView):
    """
    Export group's vote attendance from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "group_vote_attendance"
    resource = GroupVoteAttendanceResource()


class ExportGroupVotesInCommon(ExportResourceView):
    """
    Export group's votes in common from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "group_votes_in_common"
    resource = GroupVotesInCommonResource()


class ExportGroupTfidf(ExportResourceView):
    """
    Export group's tfidf from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "group_tfidf"
    resource = GroupTfidfResource()
