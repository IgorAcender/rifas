from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import PageView
from raffles.models import Raffle
import json


@staff_member_required
def analytics_dashboard(request):
    """Dashboard com analytics de visualizações de páginas"""
    
    # Totais gerais
    total_views = PageView.get_total_views()
    views_today = PageView.get_total_views(days=1)
    views_this_week = PageView.get_total_views(days=7)
    
    # Views por tipo de página
    views_by_type = PageView.get_views_by_page_type()
    
    # Views por raffle
    views_by_raffle = list(PageView.get_views_by_raffle())
    top_raffles = views_by_raffle[:10]  # Top 10 raffles
    
    # Trend dos últimos 30 dias
    daily_views = list(PageView.get_views_by_day(days=30))
    
    # Preparar dados para gráfico
    days_data = []
    for item in daily_views:
        days_data.append({
            'date': item['date'].strftime('%d/%m'),
            'count': item['count']
        })
    
    # Preparar dados para gráfico de tipo de página
    type_data = []
    for item in views_by_type:
        type_data.append({
            'type': item['page_type'],
            'label': dict(PageView.PageType.choices).get(item['page_type'], item['page_type']),
            'count': item['count']
        })
    
    # Preparar dados para tabela de raffles
    raffle_data = []
    raffle_ids = [item['raffle_id'] for item in top_raffles if item.get('raffle_id')]
    raffles_map = {r.id: r for r in Raffle.objects.filter(id__in=raffle_ids)}
    
    for item in top_raffles:
        raffle_id = item.get('raffle_id')
        raffle = raffles_map.get(raffle_id)
        if raffle:
            raffle_data.append({
                'raffle_name': raffle.name,
                'raffle_id': raffle.id,
                'count': item['count']
            })
    
    context = {
        'total_views': total_views,
        'views_today': views_today,
        'views_this_week': views_this_week,
        'views_by_type': type_data,
        'top_raffles': raffle_data,
        'daily_views_json': json.dumps(days_data),
        'type_views_json': json.dumps(type_data),
    }
    
    return render(request, 'analytics/dashboard.html', context)
