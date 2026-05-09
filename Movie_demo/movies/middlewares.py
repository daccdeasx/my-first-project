# movies/middlewares.py
import json
import time
from django.utils.deprecation import MiddlewareMixin

from movies.llm import logger


class APILogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        log_data = {
            "path": request.path,
            "method": request.method,
            "status": response.status_code,
            "duration": round(time.time() - request.start_time, 3),
            "user": request.user.id if request.user.is_authenticated else None
        }

        if 400 <= response.status_code < 500:
            logger.warning(json.dumps(log_data))
        elif response.status_code >= 500:
            logger.error(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))

        return response