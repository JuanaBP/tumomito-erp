from django.utils.deprecation import MiddlewareMixin


class BitacoraMiddleware(MiddlewareMixin):
    """Registra acciones POST/PUT/DELETE de usuarios autenticados."""

    def process_response(self, request, response):
        try:
            if request.user.is_authenticated and request.method in ('POST', 'PUT', 'DELETE'):
                from apps.personal.models import Bitacora
                Bitacora.objects.create(
                    user=request.user,
                    accion=f"{request.method} {request.path}",
                    ip=self._get_ip(request),
                )
        except Exception:
            pass
        return response

    @staticmethod
    def _get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
