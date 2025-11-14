"""
Custom middleware for error handling and dynamic site URL detection
"""
import logging
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


class DynamicSiteURLMiddleware:
    """
    Middleware to dynamically set SITE_URL based on the current domain being accessed.
    This allows backup domains to work seamlessly without hardcoding the domain.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get the current domain from the request
        domain = request.get_host()  # Returns 'example.com' or 'example.com:8000'
        
        # Determine if it's HTTPS or HTTP
        protocol = 'https' if request.is_secure() else 'http'
        
        # Set SITE_URL dynamically based on current domain
        request.site_url = f"{protocol}://{domain}"
        
        # Store in request for use in views
        response = self.get_response(request)
        return response


class SilentErrorMiddleware:
    """
    Middleware to catch and hide database/system errors from end users.
    Logs errors but shows friendly message instead.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """
        Catch exceptions and handle them gracefully for non-staff users
        """
        # Log the error for debugging
        # Build a safe user identifier without assuming a `username` attribute exists
        user_identifier = 'Anonymous'
        try:
            if hasattr(request, 'user') and request.user.is_authenticated:
                u = request.user
                user_identifier = getattr(u, 'username', None) or getattr(u, 'name', None) or getattr(u, 'email', 'AuthenticatedUser')
        except Exception:
            # Fallback in case request.user access itself raises
            user_identifier = 'AuthenticatedUser'

        logger.error(
            f"Error occurred: {type(exception).__name__}: {str(exception)}",
            exc_info=True,
            extra={
                'user': user_identifier,
                'path': request.path,
                'method': request.method,
            }
        )
        
        # If user is staff/admin, let Django show the detailed error (for debugging)
        if request.user.is_authenticated and request.user.is_staff:
            return None  # Let Django handle it normally
        
        # For regular users, show a friendly error message
        messages.error(
            request,
            'Ocorreu um erro temporário. Por favor, tente novamente em alguns instantes.'
        )
        
        # Redirect to a safe page based on context
        if request.path.startswith('/minha-area'):
            return redirect('customer_area')
        elif request.path.startswith('/dashboard') or request.path.startswith('/admin'):
            return redirect('admin_login')
        else:
            return redirect('home')


class CleanupExpiredReservationsMiddleware:
    """Middleware para limpar reservas expiradas a cada hora"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_cleanup_hour = None
    
    def __call__(self, request):
        """Verificar a cada request se deve fazer cleanup"""
        from django.utils import timezone
        
        now = timezone.now()
        
        # Se mudou de hora, fazer cleanup
        if self.last_cleanup_hour != now.hour:
            self.cleanup_expired_reservations(now)
            self.last_cleanup_hour = now.hour
        
        response = self.get_response(request)
        return response
    
    def cleanup_expired_reservations(self, now):
        """Limpar reservas expiradas"""
        try:
            from raffles.models import RaffleNumber
            
            # Liberar números com reserva expirada
            expired = RaffleNumber.objects.filter(
                status=RaffleNumber.Status.RESERVED,
                reserved_expires_at__isnull=False,
                reserved_expires_at__lt=now
            )
            
            count = expired.count()
            
            if count > 0:
                expired.update(
                    status=RaffleNumber.Status.AVAILABLE,
                    user=None,
                    order=None,
                    reserved_at=None,
                    reserved_expires_at=None
                )
                logger.info(f'🔄 Cleanup automático ({now.hour}h): {count} número(s) liberado(s)')
        except Exception as e:
            logger.error(f'❌ Erro ao fazer cleanup de reservas: {e}')

