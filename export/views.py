from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse, StreamingHttpResponse

from .resources import VoteResource, MPResource

from rest_framework_csv import renderers as r
from rest_framework.renderers import JSONRenderer, BaseRenderer


class ExportVotesView(views.APIView):
    """
    Export all votes from database and return them as a file in one of the allowed formats (json, csv).
    """
    renderer_classes = [r.CSVRenderer, JSONRenderer ]

    def get(self, request, format=None):
        filename = "votes"

        if (format == "json"):
            dataset_json = VoteResource().export_as_generator_json()
            return StreamingHttpResponse(dataset_json, headers={
                'Content-Disposition': f'attachment; filename="{filename}.json"'
            })

        elif (format == "csv"):
            dataset_csv = VoteResource().export_as_generator_csv()
            return StreamingHttpResponse(dataset_csv, headers={
                'Content-Disposition': f'attachment; filename="{filename}.csv"'
            })
        
        # format not supported
        return Response({'detail': 'format not supported'}, status=status.HTTP_404_NOT_FOUND)


class ExportParliamentMembersView(views.APIView):
    """
    Export all parliament members from database and return them as a file in one of the allowed formats (json, csv).
    """
    renderer_classes = [r.CSVRenderer, JSONRenderer ]

    def get(self, request, format=None):
        filename = "parliament-members"

        if (format == "json"):
            dataset_json = MPResource().export_as_generator_json()
            return StreamingHttpResponse(dataset_json, headers={
                'Content-Disposition': f'attachment; filename="{filename}.json"'
            })
        elif (format == "csv"):
            dataset_csv = MPResource().export_as_generator_csv()
            return StreamingHttpResponse(dataset_csv, headers={
                'Content-Disposition': f'attachment; filename="{filename}.csv"'
            })

        # format not supported
        return Response({'detail': 'format not supported'}, status=status.HTTP_404_NOT_FOUND)
