from export.resources.misc import (
    VoteResource,
    MPResource,
    GroupsResource,
    LegislationResource,
)

from export.views.common import ExportResourceView

class ExportVotesView(ExportResourceView):
    """
    Export all votes from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "votes"
    resource = VoteResource()


class ExportParliamentMembersView(ExportResourceView):
    """
    Export all parliament members from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "parliament-members"
    resource = MPResource()


class ExportParliamentGroupsView(ExportResourceView):
    """
    Export all parliament members from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "parliament-members"
    resource = GroupsResource()


class ExportLegislationView(ExportResourceView):
    """
    Export all legislation from database and return them as a file in one of the allowed formats (json, csv).
    """
    filename = "legislation"
    resource = LegislationResource()
