from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.conf import settings
from notifications.evolution import evolution_api
from notifications.models import WhatsAppMessageTemplate
import requests


@staff_member_required
def whatsapp_manager(request):
    """WhatsApp Evolution API Manager"""
    # Get current message templates
    payment_template = WhatsAppMessageTemplate.get_default_template()
    referral_template = WhatsAppMessageTemplate.get_referral_bonus_template()
    referral_share_template = WhatsAppMessageTemplate.get_referral_share_template()

    context = {
        'evolution_url': settings.EVOLUTION_API_URL,
        'instance_name': settings.EVOLUTION_INSTANCE_NAME,
        'api_configured': bool(settings.EVOLUTION_API_URL and settings.EVOLUTION_API_KEY),
        'message_template': payment_template,
        'referral_bonus_template': referral_template,
        'referral_share_template': referral_share_template,
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


@staff_member_required
def save_message_template(request):
    """Save WhatsApp message template"""
    if request.method == 'POST':
        template_text = request.POST.get('template')
        template_name = request.POST.get('template_name', 'payment_confirmation')

        if not template_text:
            return JsonResponse({
                'success': False,
                'error': 'Template é obrigatório'
            })

        # Validate template_name
        if template_name not in ['payment_confirmation', 'referral_bonus_notification', 'referral_share_invitation']:
            return JsonResponse({
                'success': False,
                'error': 'Nome de template inválido'
            })

        try:
            template, created = WhatsAppMessageTemplate.objects.get_or_create(
                name=template_name,
                defaults={"template": template_text}
            )
            if not created:
                template.template = template_text
                template.save()

            return JsonResponse({
                'success': True,
                'message': 'Template salvo com sucesso!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao salvar: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Método não permitido'
    })
