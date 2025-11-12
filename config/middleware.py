"""
Custom middleware for error handling
"""
import logging
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


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
        logger.error(
            f"Error occurred: {type(exception).__name__}: {str(exception)}",
            exc_info=True,
            extra={
                'user': request.user.username if request.user.is_authenticated else 'Anonymous',
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
