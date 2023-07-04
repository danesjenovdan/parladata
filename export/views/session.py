from export.views.common import ExportResourceView

from export.resources.session import VoteResource


class ExportVotesView(ExportResourceView):
    """
    Export votes from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "votes"
    resource = VoteResource()
