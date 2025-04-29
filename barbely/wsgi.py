import os
import logging

logger = logging.getLogger(__name__)
logger.info("Inicializando WSGI application")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbely.settings')

# Crie a aplicação WSGI
application = get_wsgi_application()

# Função para logar requisições
def log_request(app):
    def wrapped(environ, start_response):
        logger.info(f"WSGI Request: {environ['REQUEST_METHOD']} {environ['PATH_INFO']}")
        return app(environ, start_response)
    return wrapped

# Aplique a função de log à aplicação
application = log_request(application)