from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
import mercadopago
from raffles.models import RaffleOrder


@api_view(['POST'])
def create_mercadopago_payment(request):
    """Create MercadoPago payment preference"""
    order_id = request.data.get('order_id')

    try:
        order = RaffleOrder.objects.get(id=order_id, user=request.user)
    except RaffleOrder.DoesNotExist:
        return Response({'error': 'Pedido não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if order.status == RaffleOrder.Status.PAID:
        return Response({'error': 'Pedido já pago'}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize MercadoPago SDK
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    # Create preference
    preference_data = {
        "items": [{
            "title": f"Rifa: {order.raffle.name}",
            "quantity": order.quantity,
            "unit_price": float(order.amount / order.quantity),
        }],
        "payer": {
            "name": order.user.name,
            "phone": {
                "number": order.user.whatsapp
            }
        },
        "external_reference": str(order.id),
        "notification_url": request.build_absolute_uri('/api/payments/mercadopago/webhook/'),
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    # Save payment ID
    order.payment_id = preference["id"]
    order.save(update_fields=['payment_id'])

    return Response({
        'preference_id': preference["id"],
        'init_point': preference["init_point"],
        'sandbox_init_point': preference["sandbox_init_point"],
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def mercadopago_webhook(request):
    """MercadoPago webhook handler"""
    # Get payment info from webhook
    payment_id = request.data.get('data', {}).get('id')

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

    # Check payment status
    if payment_data["status"] == "approved":
        numbers = order.mark_as_paid()

        # TODO: Send WhatsApp notification with numbers
        # from notifications.tasks import send_whatsapp_notification
        # send_whatsapp_notification.delay(order.id)

    order.payment_data = payment_data
    order.save(update_fields=['payment_data'])

    return Response(status=status.HTTP_200_OK)
