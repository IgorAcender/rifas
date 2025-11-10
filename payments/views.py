from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import mercadopago
from raffles.models import RaffleOrder


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
        if order.status == RaffleOrder.Status.PAID and 'won_prizes' in order.payment_data:
            response_data['won_prizes'] = order.payment_data['won_prizes']

        return Response(response_data)
    except RaffleOrder.DoesNotExist:
        return Response({'error': 'Pedido não encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def mercadopago_webhook(request):
    """MercadoPago webhook handler"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Webhook received: {request.data}")

    if request.data.get("action") == "payment.updated":
        payment_id = request.data.get('data', {}).get('id')
        logger.info(f"Payment updated: {payment_id}")
    else:
        # Not a payment update, ignore
        logger.info(f"Ignoring webhook action: {request.data.get('action')}")
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
        from notifications.whatsapp import send_payment_confirmation

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

    # Save the latest payment data for reference
    order.payment_data = payment_data
    order.save(update_fields=['payment_data'])

    return Response(status=status.HTTP_200_OK)
