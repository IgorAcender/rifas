"""
Context processors for templates
"""
from .models import SiteConfiguration


def site_config(request):
    """
    Add site configuration to all template contexts.
    This includes the logo and site name.
    """
    config = SiteConfiguration.get_config()

    return {
        'site_logo': config.get_logo_base64(),
        'site_name': config.site_name,
        'site_config': config,
    }
