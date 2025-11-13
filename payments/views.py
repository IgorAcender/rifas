from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import mercadopago
from raffles.models import RaffleOrder
import json


def webhook_parser(request_data, content_type):
    """
    Parse webhook data from different content types
    """
    if isinstance(request_data, dict):
        return request_data
    
    if content_type == 'application/x-www-form-urlencoded':
        # Convert form data to dict
        return dict(request_data)
    
    try:
        return json.loads(request_data)
    except (json.JSONDecodeError, TypeError):
        return request_data if isinstance(request_data, dict) else {}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_mercadopago_payment(request):
    """Create a direct PIX payment on MercadoPago"""
    order_id = request.data.get('order_id')

    try:
        order = RaffleOrder.objects.get(id=order_id, user=request.user)
    except RaffleOrder.DoesNotExist:
        return Response({'error': 'Pedido não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if order.status == RaffleOrder.Status.PAID:
        return Response({'error': 'Este pedido já foi pago.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if MercadoPago is configured
    if not settings.MERCADOPAGO_ACCESS_TOKEN:
        return Response({
            'error': 'Sistema de pagamento não configurado',
            'details': 'Entre em contato com o administrador.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    # Usar email e CPF do usuário se disponível, senão usar valores padrão
    payer_email = request.user.email or f"user{request.user.id}@noemail.com"
    payer_cpf = request.user.cpf or "00000000000"

    # Create PIX payment data
    payment_data = {
        "transaction_amount": float(order.amount),
        "description": f"Instituto Acender - Pedido #{order.id}",
        "payment_method_id": "pix",
        "payer": {
            "email": payer_email,
            "first_name": request.user.get_short_name(),
            "last_name": ' '.join(request.user.get_full_name().split(' ')[1:]) or request.user.get_short_name(),
            "identification": {
                "type": "CPF",
                "number": payer_cpf
            },
        },
        "external_reference": str(order.id),
        "notification_url": request.build_absolute_uri(f'/api/payments/mercadopago/webhook/'),
    }

    print(f"DEBUG: Creating PIX payment for order {order.id}")
    print(f"DEBUG: Amount: {payment_data['transaction_amount']}")
    print(f"DEBUG: MercadoPago Token configured: {bool(settings.MERCADOPAGO_ACCESS_TOKEN)}")

    try:
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        print(f"DEBUG: MercadoPago response status: {payment_response['status']}")
        
        if payment_response["status"] >= 400:
            error_detail = payment.get('message', 'Erro desconhecido')
            print(f"ERROR: MercadoPago error: {error_detail}")
            return Response({
                'error': 'Erro ao criar pagamento PIX', 
                'details': error_detail,
                'full_response': payment
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"ERROR: Exception creating payment: {str(e)}")
        return Response({
            'error': 'Erro ao conectar com MercadoPago',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Save payment ID from the payment itself
    order.payment_id = payment["id"]
    order.save(update_fields=['payment_id'])

    # Extract PIX data to return to frontend
    pix_data = {
        "payment_id": payment["id"],
        "qr_code_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
        "qr_code": payment["point_of_interaction"]["transaction_data"]["qr_code"],
    }

    return Response(pix_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_status(request, order_id):
    """Check the status of a specific order"""
    try:
        order = RaffleOrder.objects.get(id=order_id, user=request.user)

        response_data = {
            'status': order.status
        }

        # Se o pedido foi pago, incluir informações sobre prêmios ganhos
        if order.status == RaffleOrder.Status.PAID:
            print(f"🔍 DEBUG: Pedido {order_id} está pago. payment_data: {order.payment_data}")
            if order.payment_data and 'won_prizes' in order.payment_data:
                response_data['won_prizes'] = order.payment_data['won_prizes']
                print(f"🏆 DEBUG: Retornando won_prizes: {response_data['won_prizes']}")
            else:
                print(f"⚠️ DEBUG: Sem won_prizes em payment_data")

        return Response(response_data)
    except RaffleOrder.DoesNotExist:
        return Response({'error': 'Pedido não encontrado'}, status=status.HTTP_404_NOT_FOUND)


@require_http_methods(["POST"])
@csrf_exempt
def mercadopago_webhook(request):
    """MercadoPago webhook handler - Accepts both JSON and form-urlencoded"""
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Parse webhook data - handle both JSON and form-urlencoded
        content_type = request.META.get('CONTENT_TYPE', 'application/json')
        
        if 'application/x-www-form-urlencoded' in content_type:
            # Convert form data to dict
            request_data = dict(request.POST)
            # Convert single-item lists to strings
            request_data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in request_data.items()}
        elif 'application/json' in content_type:
            import json
            request_data = json.loads(request.body)
        else:
            # Fallback to DRF parsing
            request_data = request.data if hasattr(request, 'data') else request.POST.dict()

        logger.info(f"Webhook received: {request_data}")

        if request_data.get("action") == "payment.updated":
            payment_id = request_data.get('data', {}).get('id') if isinstance(request_data.get('data'), dict) else request_data.get('data', {}).get('id') if isinstance(request_data.get('data'), list) else None
            logger.info(f"Payment updated: {payment_id}")
        else:
            # Not a payment update, ignore
            logger.info(f"Ignoring webhook action: {request_data.get('action')}")
            return Response(status=status.HTTP_200_OK)

        if not payment_id:
            logger.warning("No payment_id in webhook data")
            return Response(status=status.HTTP_200_OK)

        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        payment_info = sdk.payment().get(payment_id)

        if payment_info["status"] != 200:
            return Response(status=status.HTTP_200_OK)

        payment_data = payment_info["response"]
        external_reference = payment_data.get("external_reference")

        if not external_reference:
            logger.warning("No external_reference in payment data")
            return Response(status=status.HTTP_200_OK)

        try:
            order = RaffleOrder.objects.get(id=external_reference)
        except RaffleOrder.DoesNotExist:
            return Response(status=status.HTTP_200_OK)

        # Check payment status and mark as paid if approved
        if payment_data["status"] == "approved" and order.status != RaffleOrder.Status.PAID:
            logger.info(f"✅ Payment approved for order {order.id}")
            logger.info(f"👤 User: {order.user.name} (ID: {order.user.id})")
            logger.info(f"📱 WhatsApp: {order.user.whatsapp}")

            # Mark as paid (this also allocates bonus numbers if referral was used)
            order.mark_as_paid()
            logger.info(f"💰 Order {order.id} marked as paid")

            # Get allocated numbers
            numbers = list(order.allocated_numbers.values_list('number', flat=True))
            logger.info(f"🔢 Allocated numbers: {numbers}")

            # Send WhatsApp notification with numbers
            from notifications.whatsapp import send_payment_confirmation, send_referral_share_invitation

            logger.info(f"📤 Attempting to send WhatsApp to {order.user.whatsapp}")
            try:
                result = send_payment_confirmation(order)
                if result:
                    logger.info(f"✅ WhatsApp sent successfully to {order.user.whatsapp}")
                    logger.info(f"📋 Response: {result}")
                else:
                    logger.error(f"❌ WhatsApp sending failed for order {order.id} - No result returned")
            except Exception as e:
                logger.error(f"❌ Error sending WhatsApp notification: {e}", exc_info=True)

            # Send referral share invitation if eligible
            if (order.raffle.enable_referral and
                order.quantity >= order.raffle.referral_min_purchase):
                logger.info(f"📤 Sending referral share invitation to {order.user.whatsapp}")
                try:
                    result = send_referral_share_invitation(order)
                    if result:
                        logger.info(f"✅ Referral invitation sent successfully")
                    else:
                        logger.error(f"❌ Failed to send referral invitation")
                except Exception as e:
                    logger.error(f"❌ Error sending referral invitation: {e}", exc_info=True)

        # Save the latest payment data for reference
        # Preserve any won_prizes or milestone data that mark_as_paid() may have stored
        try:
            existing_payment_data = order.payment_data or {}
        except Exception:
            existing_payment_data = {}

        # Keys we want to keep if present
        for key in ('won_prizes', 'milestone_achieved', 'milestone_prize'):
            if key in existing_payment_data and key not in payment_data:
                payment_data[key] = existing_payment_data[key]

        order.payment_data = payment_data
        order.save(update_fields=['payment_data'])

        return Response(status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
        return Response(status=status.HTTP_200_OK)
