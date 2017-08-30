from __future__ import absolute_import, unicode_literals
from celery import shared_task
from raven.contrib.django.raven_compat.models import client
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .export import exportSessions 

import json
import requests

exports = {'exportSessions': exportSessions}

status_api = settings.DASHBOARD_URL + '/api/status/'

@csrf_exempt
def runAsyncExport(request):
    print('ivan')
    if request.method == 'POST':
        data = json.loads(request.body)
        print data
        status_id = data.pop('status_id')
        export_sessions.apply_async((data['setters'], status_id), queue='parladata_project')
        return JsonResponse({'status':'runned'})
    else:
        return JsonResponse({'status': 'this isnt post'})


@shared_task
def export_sessions(expoert_tasks, status_id):
    methods = [exports[task] for task in expoert_tasks]
    sendStatus(status_id, 'Running', '[]')
    try:
        for method in methods:
            #method()
            print('ivan')
        print "naj se bi exportal"
        sendStatus(status_id, 'Done', '[]')
    except:
        sendStatus(status_id, 'Fails', '[]')
        client.captureException()

def sendStatus(status_id, type_, data):
    requests.put(status_api + str(status_id) + '/',
                 data= {
                            "status_type": type_,
                            "status_note": datetime.now().strftime(settings.API_DATE_FORMAT),
                            "status_done": data
                        })