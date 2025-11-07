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

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    # Usar email e CPF do usuário se disponível, senão usar valores padrão
    payer_email = request.user.email or f"user{request.user.id}@noemail.com"
    payer_cpf = request.user.cpf or "00000000000"

    # Create PIX payment data
    payment_data = {
        "transaction_amount": float(order.amount),
        "description": f"Rifa: {order.raffle.name} - Pedido #{order.id}",
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

    payment_response = sdk.payment().create(payment_data)
    payment = payment_response["response"]

    if payment_response["status"] >= 400:
        return Response({'error': 'Erro ao criar pagamento PIX', 'details': payment}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({'status': order.status})
    except RaffleOrder.DoesNotExist:
        return Response({'error': 'Pedido não encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def mercadopago_webhook(request):
    """MercadoPago webhook handler"""
    if request.data.get("action") == "payment.updated":
        payment_id = request.data.get('data', {}).get('id')
    else:
        # Not a payment update, ignore
        return Response(status=status.HTTP_200_OK)

    if not payment_id:
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
        order.mark_as_paid()

        # TODO: Send WhatsApp notification with numbers
        # from notifications.tasks import send_whatsapp_notification
        # send_whatsapp_notification.delay(order.id)

    # Save the latest payment data for reference
    order.payment_data = payment_data
    order.save(update_fields=['payment_data'])

    return Response(status=status.HTTP_200_OK)
