import logging

logger = logging.getLogger(__name__)

class LogHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        logger.info("LogHeadersMiddleware inicializado")

    def __call__(self, request):
        logger.info(f"Request Method: {request.method}, Path: {request.path}")
        logger.info(f"Request Origin: {request.headers.get('Origin')}")
        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = 'https://barbely.vercel.app'  # Forçar o header
        response['Access-Control-Allow-Methods'] = 'DELETE, GET, OPTIONS, PATCH, POST, PUT'
        response['Access-Control-Allow-Headers'] = 'accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with'
        logger.info(f"Response Status: {response.status_code}")
        logger.info(f"Response Headers: {response.headers}")
        return response