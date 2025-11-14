from django.db import models
from django.utils import timezone
from raffles.models import Raffle


class PageView(models.Model):
    """Modelo para registrar visualizações de páginas"""
    
    class PageType(models.TextChoices):
        HOME = 'home', 'Home'
        RAFFLE_PUBLIC = 'raffle_public', 'Página Pública de Raffle'
        RAFFLE_DETAILS = 'raffle_details', 'Detalhes da Raffle'
        CUSTOMER_AREA = 'customer_area', 'Minha Área'
        OTHER = 'other', 'Outra Página'
    
    page_type = models.CharField(
        'Tipo de Página',
        max_length=20,
        choices=PageType.choices,
        default=PageType.OTHER
    )
    
    raffle = models.ForeignKey(
        Raffle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='page_views',
        help_text='Raffle relacionada (se aplicável)'
    )
    
    user_agent = models.CharField('User Agent', max_length=500, blank=True)
    ip_address = models.CharField('IP Address', max_length=50, blank=True)
    referer = models.CharField('Referer', max_length=500, blank=True)
    
    # Geolocalização básica (opcional, pode ser expandido)
    country = models.CharField('País', max_length=100, blank=True)
    
    viewed_at = models.DateTimeField('Visualizado em', auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'Visualização de Página'
        verbose_name_plural = 'Visualizações de Páginas'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['page_type', '-viewed_at']),
            models.Index(fields=['raffle', '-viewed_at']),
            models.Index(fields=['-viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.get_page_type_display()} - {self.viewed_at.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def get_total_views(cls, days=None):
        """Retorna total de visualizações (opcional: dos últimos N dias)"""
        qs = cls.objects.all()
        if days:
            start_date = timezone.now() - timezone.timedelta(days=days)
            qs = qs.filter(viewed_at__gte=start_date)
        return qs.count()
    
    @classmethod
    def get_views_by_page_type(cls, days=None):
        """Retorna visualizações agrupadas por tipo de página"""
        from django.db.models import Count
        
        qs = cls.objects.all()
        if days:
            start_date = timezone.now() - timezone.timedelta(days=days)
            qs = qs.filter(viewed_at__gte=start_date)
        
        return qs.values('page_type').annotate(count=Count('id')).order_by('-count')
    
    @classmethod
    def get_views_by_raffle(cls, days=None):
        """Retorna visualizações agrupadas por raffle"""
        from django.db.models import Count
        
        qs = cls.objects.filter(raffle__isnull=False)
        if days:
            start_date = timezone.now() - timezone.timedelta(days=days)
            qs = qs.filter(viewed_at__gte=start_date)
        
        return qs.values('raffle__name', 'raffle_id').annotate(count=Count('id')).order_by('-count')
    
    @classmethod
    def get_views_by_day(cls, days=30):
        """Retorna visualizações por dia (últimos N dias)"""
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        
        start_date = timezone.now() - timezone.timedelta(days=days)
        return (
            cls.objects
            .filter(viewed_at__gte=start_date)
            .annotate(date=TruncDate('viewed_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
