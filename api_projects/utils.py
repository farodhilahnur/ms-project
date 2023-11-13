from rest_framework.views import exception_handler
from django.http import Http404, HttpResponse
from rest_framework.request import Request
from rest_framework.response import Response

import uuid
import json
import logging

def not_found_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Http404):  
        # custom exception message
        custom_response_data = { 
            'code': 'not_found', 
            'message': 'Not Found' 
        }
        response.data = custom_response_data # set the custom response data on response object

    return response

def invalid_handler(message):

    # custom exception message
    custom_response_data = { 
        'code': 'validation_error', 
        'message': message
    }
    response = custom_response_data # set the custom response data on response object

    return response

def err_resp(status=500, message="Internal Server error", errs=None):
    err = {
        "success": False,
        "message": message,

    }
    if errs is not None:
        err['errs'] = errs
    return Response(status=status, data=err)


def succ_resp(status=200, data=None):
    if data is not None:
        data = data
    return Response(status=status, data=data)

def get_uuid():
    return str(uuid.uuid4())

def api_500_handler(exception, context):
    response = exception_handler(exception, context)

    try:
        message = str(response.context)
        logger = logging.getLogger(__name__)
        logger.error(str(response.context))

    except AttributeError:
        message = str(exception)
        status = 500

    response = HttpResponse(
        json.dumps({'message': message}),
        content_type="application/json", status=400
    )
    return response