from export.resources.person import (
    VocabularySizeResource,
    PersonNumberOfSpokenWordsResource,
    DeviationFromGroupResource,
    PersonMonthlyVoteAttendanceResource,
    PersonPersonVoteAttendanceResource,
    ExportPersonStyleScoresResource,
    ExportPersonAvgSpeechesPerSessionResource,
    VotingDistanceResource,
    PersonNumberOfQuestionsResource,
    PersonPublicQuestionsResource,
    PersonTfidfResource,
    PersonMembershipResource,
    PersonBallotsResource,
    PersonQuestionsResource,
)

from export.views.common import ExportResourceView

class ExportVocabularySize(ExportResourceView):
    """
    Export person's vocabulary size from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "vocabulary_size"
    resource = VocabularySizeResource()


class ExportPersonNumberOfSpokenWords(ExportResourceView):
    """
    Export person's number of spoken words from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "number_of_spoken_words"
    resource = PersonNumberOfSpokenWordsResource()


class ExportDeviationFromGroup(ExportResourceView):
    filename = "deviation_from_group_resource"
    resource = DeviationFromGroupResource()


class ExportPersonMonthlyVoteAttendance(ExportResourceView):
    filename = "person_monthly_vote_attendance"
    resource = PersonMonthlyVoteAttendanceResource()


class ExportPersonVoteAttendance(ExportResourceView):
    filename = "person_vote_attendance"
    resource = PersonPersonVoteAttendanceResource()


class ExportPersonStyleScores(ExportResourceView):
    filename = "person_style_scores"
    resource = ExportPersonStyleScoresResource()


class ExportPersonAvgSpeechesPerSession(ExportResourceView):
    filename = "person_avg_speeches_per_session"
    resource = ExportPersonAvgSpeechesPerSessionResource()


class ExportVotingDistance(ExportResourceView):
    filename = "voting_distance"
    resource = VotingDistanceResource()


class ExportPersonNumberOfQuestions(ExportResourceView):
    filename = "person_number_of_questions"
    resource = PersonNumberOfQuestionsResource()


class ExportPersonPublicQuestionView(ExportResourceView):
    filename = "person_public_questions"
    resource = PersonPublicQuestionsResource()


class ExportPersonTfidfView(ExportResourceView):
    filename = "person_tfidf"
    resource = PersonTfidfResource()


class ExportPersonMembership(ExportResourceView):
    filename = "person_membership"
    resource = PersonMembershipResource()


class ExportPersonBallots(ExportResourceView):
    filename = "person_ballots"
    resource = PersonBallotsResource()


class ExportPersonQuestions(ExportResourceView):
    filename = "questions"
    resource = PersonQuestionsResource()
