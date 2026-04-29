from django.utils.deprecation import MiddlewareMixin


class BitacoraMiddleware(MiddlewareMixin):
    """Middleware simple que registra accesos a la app por usuarios autenticados."""

    def process_response(self, request, response):
        try:
            if request.user.is_authenticated and request.method in ('POST', 'PUT', 'DELETE'):
                from apps.personal.models import Login, Bitacora
                login = Login.objects.filter(user=request.user).first()
                if login:
                    Bitacora.objects.create(
                        login=login,
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
