import logging

logger = logging.getLogger(__name__)

class LogHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Request Method: {request.method}, Path: {request.path}")
        logger.info(f"Request Origin: {request.headers.get('Origin')}")
        response = self.get_response(request)
        logger.info(f"Response Headers: {response.headers}")
        return response