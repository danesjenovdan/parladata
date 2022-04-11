from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse, StreamingHttpResponse

from .resources import VoteResource, MPResource

from rest_framework_csv import renderers as r
from rest_framework.renderers import JSONRenderer, BaseRenderer


class ExportResourceView(views.APIView):
    """
    A view meant to be extended.
    Exports resource objects and returns them as files.
    """
    renderer_classes = [r.CSVRenderer, JSONRenderer ]
    filename = None
    resource = None

    def get(self, request, format=None):
        mandate_id = request.query_params.get('mandate_id')

        if (format == "json"):
            dataset_json = self.resource.export_as_generator_json(mandate_id=mandate_id)
            return StreamingHttpResponse(dataset_json, headers={
                'Content-Disposition': f'attachment; filename="{self.filename}.json"'
            }, content_type="application/json")
        elif (format == "csv"):
            dataset_csv = self.resource.export_as_generator_csv(mandate_id=mandate_id)
            return StreamingHttpResponse(dataset_csv, headers={
                'Content-Disposition': f'attachment; filename="{self.filename}.csv"'
            }, content_type="text/csv")
        
        # format not supported
        return Response({'detail': 'format not supported'}, status=status.HTTP_404_NOT_FOUND)


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
