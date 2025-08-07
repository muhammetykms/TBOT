from django.utils.deprecation import MiddlewareMixin

class KullaniciTercihiMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            request.dil_tercihi = request.user.dil_tercihi
            request.bildirim_tercihi = request.user.bildirim_tercihi
        else:
            request.dil_tercihi = 'tr'  # varsayılan dil
            request.bildirim_tercihi = True
