from __future__ import absolute_import, unicode_literals
from celery import shared_task
from raven.contrib.django.raven_compat.models import client
from datetime import datetime

from parladata_project.settings import API_DATE_FORMAT, PARLALIZE_API_KEY, DASHBOARD_URL

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied

from .export import exportSessions, exportSession

import json
import requests

exports = {'exportSessions': exportSessions,
           'exportSession': exportSession}

status_api = DASHBOARD_URL + '/api/status/'

@csrf_exempt
def runAsyncExport(request):
    print('ivan')
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        status_id = data.pop('status_id')
        auth_key = request.META['HTTP_AUTHORIZATION']
        if auth_key != PARLALIZE_API_KEY:
            print("auth fail")
            sendStatus(status_id, "Fail", "Authorization fails")
            raise PermissionDenied
        if data['attr']:
            attr = data['attr']
        else:
            attr = None
        export_sessions.apply_async((data['setters'], status_id, attr), queue='parladata_project')
        return JsonResponse({'status':'runned'})
    else:
        return JsonResponse({'status': 'this isnt post'})


@shared_task
def export_sessions(expoert_tasks, status_id, attr=None):
    methods = [exports[task] for task in expoert_tasks]
    sendStatus(status_id, 'Running', '[]')
    if attr:
        data = {'session_id': attr}
    else:
        data = {}
    try:
        resp = "ni slo zgleda"
        for method in methods:
            resp = method(**data)
        sendStatus(status_id, 'Done', resp)
    except:
        sendStatus(status_id, 'Fails', resp)
        client.captureException()

def sendStatus(status_id, type_, data):
    requests.put(status_api + str(status_id) + '/',
                 data= {
                            "status_type": type_,
                            "status_note": datetime.now().strftime(API_DATE_FORMAT),
                            "status_done": data
                        })
