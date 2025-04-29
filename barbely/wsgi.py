import os
import logging

logger = logging.getLogger(__name__)
logger.info("Inicializando WSGI application")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbely.settings')

application = get_wsgi_application()

# Log todas as requisições no nível do WSGI
def log_request(environ, start_response):
    logger.info(f"WSGI Request: {environ['REQUEST_METHOD']} {environ['PATH_INFO']}")
    return application(environ, start_response)

application = log_request