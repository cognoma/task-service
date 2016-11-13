import re

from rest_framework import authentication, permissions
from rest_framework import exceptions
from django.conf import settings
import jwt

class CognomaAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return None

        auth_header = request.META['HTTP_AUTHORIZATION']

        if not auth_header:
            return None

        match = re.match("^(?P<type>Bearer|JWT)\s(?P<token>.+)$", auth_header)

        if not match:
            return None

        auth_type = match.group('type')
        token = match.group('token')

        if auth_type == 'JWT':
            try:
                payload = jwt.decode(token, settings.JWT_PUB_KEY, algorithms=["RS256"])
            except:
                return None

            if 'service' not in payload:
                return None

            service = payload['service']

            return (service, {'type': auth_type, 'service': service})
        else:
            return None

    def authenticate_header(self, request):
        return "HTTP 401 Unauthorized"

class TaskServicePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user: ## the "service" from above
            raise exceptions.NotAuthenticated()

        return True

class QueuePullPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user: ## the "service" from above
            raise exceptions.NotAuthenticated()

        return True
