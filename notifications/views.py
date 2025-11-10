from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.conf import settings
from notifications.evolution import evolution_api
import requests


@staff_member_required
def whatsapp_manager(request):
    """WhatsApp Evolution API Manager"""
    context = {
        'evolution_url': settings.EVOLUTION_API_URL,
        'instance_name': settings.EVOLUTION_INSTANCE_NAME,
        'api_configured': bool(settings.EVOLUTION_API_URL and settings.EVOLUTION_API_KEY),
    }
    return render(request, 'admin/whatsapp_manager.html', context)


@staff_member_required
def get_instance_status(request):
    """Get WhatsApp instance connection status"""
    try:
        status = evolution_api.check_instance_status()
        if status:
            return JsonResponse({
                'success': True,
                'status': status
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Não foi possível obter o status da instância'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@staff_member_required
def get_qrcode(request):
    """Get QR Code for WhatsApp connection"""
    try:
        url = f"{settings.EVOLUTION_API_URL}/instance/connect/{settings.EVOLUTION_INSTANCE_NAME}"
        headers = {'apikey': settings.EVOLUTION_API_KEY}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        return JsonResponse({
            'success': True,
            'qrcode': data.get('base64', ''),
            'code': data.get('code', '')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@staff_member_required
def restart_instance(request):
    """Restart WhatsApp instance"""
    try:
        url = f"{settings.EVOLUTION_API_URL}/instance/restart/{settings.EVOLUTION_INSTANCE_NAME}"
        headers = {'apikey': settings.EVOLUTION_API_KEY}

        response = requests.put(url, headers=headers, timeout=10)
        response.raise_for_status()

        return JsonResponse({
            'success': True,
            'message': 'Instância reiniciada com sucesso'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@staff_member_required
def logout_instance(request):
    """Logout from WhatsApp instance"""
    try:
        url = f"{settings.EVOLUTION_API_URL}/instance/logout/{settings.EVOLUTION_INSTANCE_NAME}"
        headers = {'apikey': settings.EVOLUTION_API_KEY}

        response = requests.delete(url, headers=headers, timeout=10)
        response.raise_for_status()

        return JsonResponse({
            'success': True,
            'message': 'Logout realizado com sucesso'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@staff_member_required
def send_test_message(request):
    """Send test WhatsApp message"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        message = request.POST.get('message', 'Mensagem de teste do sistema de rifas!')

        if not phone:
            return JsonResponse({
                'success': False,
                'error': 'Número de telefone é obrigatório'
            })

        # Remove caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))

        # Adiciona código do Brasil se não tiver
        if not phone.startswith('55'):
            phone = '55' + phone

        try:
            result = evolution_api.send_text_message(phone, message)
            if result:
                return JsonResponse({
                    'success': True,
                    'message': 'Mensagem enviada com sucesso!',
                    'result': result
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Falha ao enviar mensagem. Verifique se o número está correto e se o WhatsApp está conectado.'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao enviar: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Método não permitido'
    })
