"""
Site Configuration Model
Stores global site settings like logo, favicon, etc.
"""
from django.db import models
from django.core.files.storage import default_storage
import base64


class SiteConfiguration(models.Model):
    """
    Singleton model to store site-wide configuration.
    Only one instance should exist.
    """

    # Logo settings
    logo = models.ImageField(
        'Logo do Site',
        upload_to='site_config/',
        blank=True,
        null=True,
        help_text='Logo principal do site (recomendado: 120x120px, PNG com fundo transparente)'
    )
    logo_base64 = models.TextField(
        'Logo Base64',
        blank=True,
        help_text='Logo codificada em base64 para uso em templates'
    )

    # Site metadata
    site_name = models.CharField(
        'Nome do Site',
        max_length=100,
        default='Sistema de Rifas',
        help_text='Nome exibido no site'
    )

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Configuração do Site'
        verbose_name_plural = 'Configurações do Site'

    def __str__(self):
        return f"Configurações do Site - {self.site_name}"

    def save(self, *args, **kwargs):
        """Override save to ensure only one instance exists and encode logo to base64"""
        # Ensure singleton
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValidationError('Já existe uma configuração de site. Edite a existente.')

        # Convert uploaded logo to base64
        if self.logo:
            try:
                # Read the file
                self.logo.seek(0)
                image_data = self.logo.read()

                # Encode to base64
                encoded = base64.b64encode(image_data).decode('utf-8')

                # Determine image format
                image_format = 'png'
                if hasattr(self.logo, 'name'):
                    if self.logo.name.lower().endswith('.jpg') or self.logo.name.lower().endswith('.jpeg'):
                        image_format = 'jpeg'
                    elif self.logo.name.lower().endswith('.svg'):
                        image_format = 'svg+xml'

                # Create data URI
                self.logo_base64 = f'data:image/{image_format};base64,{encoded}'

            except Exception as e:
                print(f"Error encoding logo to base64: {e}")

        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        """Get or create the site configuration singleton"""
        config, created = cls.objects.get_or_create(pk=1)
        return config

    @classmethod
    def get_logo_base64(cls):
        """Get logo as base64 string, or return default SVG logo"""
        config = cls.get_config()

        if config.logo_base64:
            return config.logo_base64

        # Default logo (the existing one from templates)
        return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjEyMCIgdmlld0JveD0iMCAwIDEyMCAxMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iNjAiIGN5PSI2MCIgcj0iNjAiIGZpbGw9IiMzMzUyNjgiLz48cGF0aCBkPSJNMzUgNDVDMzUgNDMgNDAgNDAgNDUgNDBDNTAgNDAgNTUgNDMgNTUgNDVMNjAgODBINTVMNDUgNTBMMzUgNTBMMzUgNDVaIiBmaWxsPSIjRkJCRjI0Ii8+PHBhdGggZD0iTTc1IDQ1Qzc1IDQzIDgwIDQwIDg1IDQwQzkwIDQwIDk1IDQzIDk1IDQ1TDkwIDgwSDg1TDc1IDUwTDc1IDQ1WiIgZmlsbD0iI0ZCQkYyNCIvPjxwYXRoIGQ9Ik00MCA3MEM0MCA2OCA0NSA2NSA1MCA2NUM1NSA2NSA2MCA2OCA2MCA3MEw1NSA5NUg1MEw0MCA3NUw0MCA3MFoiIGZpbGw9IiNGQkJGMjQiLz48cGF0aCBkPSJNNDUgMzVMNzUgMzVMNjAgNjBMNDUgMzVaIiBmaWxsPSIjQ0NENkUwIi8+PHBhdGggZD0iTTUwIDY1TDcwIDY1TDYwIDg1TDUwIDY1WiIgZmlsbD0iI0NDRDZFMCI+PGFuaW1hdGVUcmFuc2Zvcm0gYXR0cmlidXRlTmFtZT0idHJhbnNmb3JtIiB0eXBlPSJzY2FsZSIgZnJvbT0iMSIgdG89IjEuMSIgZHVyPSIwLjVzIiByZXBlYXRDb3VudD0iaW5maW5pdGUiLz48L3BhdGg+PC9zdmc+'


from django.core.exceptions import ValidationError
