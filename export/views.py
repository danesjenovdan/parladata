from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse

from .resources import VoteResource, MPResource

from rest_framework_csv import renderers as r
from rest_framework.renderers import JSONRenderer, BaseRenderer


class ExportVotesView(views.APIView):
    renderer_classes = [r.CSVRenderer, JSONRenderer ]

    def get(self, request, format=None):
        dataset = VoteResource().export()
        filename = "votes"

        if (format == "json"):
            return HttpResponse(dataset.json, headers={
                'Content-Disposition': f'attachment; filename="{filename}.json"',
            })
        elif (format == "csv"):
            # return Response(dataset.csv)
            return HttpResponse(dataset.csv, headers={
                'Content-Disposition': f'attachment; filename="{filename}.csv"',
            })
        
        # format not supported
        return Response({'detail': 'format not supported'}, status=status.HTTP_404_NOT_FOUND)


class ExportParliamentMembersView(views.APIView):
    renderer_classes = [r.CSVRenderer, JSONRenderer ]

    def get(self, request, format=None):
        dataset = MPResource().export()
        filename = "parliament-members"

        if (format == "json"):
            return HttpResponse(dataset.json, headers={
                'Content-Disposition': f'attachment; filename="{filename}.json"',
            })
        elif (format == "csv"):
            return HttpResponse(dataset.csv, headers={
                'Content-Disposition': f'attachment; filename="{filename}.csv"',
            })

        # format not supported
        return Response({'detail': 'format not supported'}, status=status.HTTP_404_NOT_FOUND)


# TODO: zamenjaj HttpResponse s StreamingHttpResponse?
# https://docs.djangoproject.com/en/4.0/ref/request-response/#django.http.StreamingHttpResponse
