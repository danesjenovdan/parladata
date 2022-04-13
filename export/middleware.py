from datetime import datetime

from django.http import JsonResponse


class ExportMiddleware:
    """
    Checks the presence and correctness of mandate_id parameter,
    returns 400 if something is wrong, otherwise
    casts and assigns it to the request object.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # only trigger if it's a /export/ url
        if '/export/' not in request.path:
            return self.get_response(request)

        # get params
        request_id = request.GET.get('mandate_id', None)

        # if no id was supplied, return
        if not request_id:
            content = {'error': '`mandate_id` is required.'}
            return JsonResponse(content, status=400)
            # we return a JsonResponse instead of DRF's Response
            # return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # if id is not an integer return
        try:
            request.mandate_id = int(request_id)
        except ValueError:
            content = {'error': '`mandate_id` needs to be an integer.'}
            return JsonResponse(content, status=400)

        return self.get_response(request)