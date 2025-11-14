from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from analytics.models import PageView
import threading
import logging

logger = logging.getLogger(__name__)


class PageViewTrackingMiddleware(MiddlewareMixin):
    """Middleware para registrar visualizações de páginas"""
    
    # Páginas que queremos rastrear
    TRACKED_VIEWS = {
        'home': 'home',
        'raffle_public': 'raffle_public',
        'raffle_details': 'raffle_details',
        'customer_area': 'customer_area',
    }
    
    # Caminhos a ignorar
    IGNORED_PATHS = [
        '/admin/',
        '/api/',
        '/static/',
        '/media/',
        '/.well-known/',
        '/favicon.ico',
    ]
    
    def should_track(self, request):
        """Verifica se a requisição deve ser rastreada"""
        path = request.path
        
        # Ignorar caminhos específicos
        for ignored in self.IGNORED_PATHS:
            if path.startswith(ignored):
                return False
        
        # Apenas GET requests
        if request.method != 'GET':
            return False
        
        return True
    
    def get_client_ip(self, request):
        """Extrai o IP real do cliente"""
        # Verificar X-Forwarded-For (para proxy/load balancer)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        
        return ip[:50]  # Limitar a 50 caracteres
    
    def get_page_type(self, request):
        """Determina o tipo de página baseado na URL"""
        resolver = None
        try:
            from django.urls import resolve
            resolver = resolve(request.path)
        except:
            return PageView.PageType.OTHER
        
        view_name = resolver.url_name or ''
        
        # Mapear view names para page types
        if 'home' in view_name:
            return PageView.PageType.HOME
        elif 'raffle_public' in view_name:
            return PageView.PageType.RAFFLE_PUBLIC
        elif 'campaign_details' in view_name:
            return PageView.PageType.RAFFLE_DETAILS
        elif 'customer' in view_name:
            return PageView.PageType.CUSTOMER_AREA
        else:
            return PageView.PageType.OTHER
    
    def get_raffle_id(self, request, view_name):
        """Extrai o ID da raffle da requisição (se aplicável)"""
        try:
            from django.urls import resolve
            resolver = resolve(request.path)
            
            # Para URLs que têm 'pk' ou 'slug'
            if 'pk' in resolver.kwargs:
                return resolver.kwargs.get('pk')
            elif 'slug' in resolver.kwargs:
                # Converter slug para ID
                from raffles.models import Raffle
                slug = resolver.kwargs.get('slug')
                raffle = Raffle.objects.filter(slug=slug).first()
                if raffle:
                    return raffle.id
        except:
            pass
        
        return None
    
    def process_response(self, request, response):
        """Registra a visualização em background"""
        if not self.should_track(request):
            return response
        
        # Executar em thread separada para não bloquear a resposta
        thread = threading.Thread(
            target=self._track_view,
            args=(request,)
        )
        thread.daemon = True
        thread.start()
        
        return response
    
    def _track_view(self, request):
        """Registra a visualização no banco de dados"""
        try:
            from django.urls import resolve
            
            resolver = resolve(request.path)
            view_name = resolver.url_name or ''
            page_type = self.get_page_type(request)
            raffle_id = self.get_raffle_id(request, view_name)
            
            PageView.objects.create(
                page_type=page_type,
                raffle_id=raffle_id,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                ip_address=self.get_client_ip(request),
                referer=request.META.get('HTTP_REFERER', '')[:500],
            )
        except Exception as e:
            logger.error(f"Erro ao registrar visualização: {e}")
