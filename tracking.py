import re
import requests
import shopify
import os

STORE_NAME = 'modelandola'
STORE_CODE_REGEX = r'MODE[0-9]*'
SUCCESS_CODE = 200

KNOWN_STATUS_MESSAGES_MAPPING = [
    ['Status: Recepción Física', 'Paquete recibido en centro de distribución'],
    ['Status: Recibido SER', 'Paquete recibido en centro de distribución'],
    ['Status: Entregado', 'Paquete entregado 😊'],
    ['Status: Planificación', 'Tu paquete está en planificación de envío, atenta a tu correo y/o mensaje de texto. Te avisaremos cuando esté en camino 😊']
]

def get_status_from_shopify(code):
    shop_url = "modelandolach.myshopify.com"
    api_version = "2021-10"

    with shopify.Session.temp(shop_url, api_version, os.environ.get("MODELADOLA_TRACKING_TOKEN")):
        orders = shopify.Order.find(name = f"#{code}", status = "any")
        if len(orders) != 1:
            return False

        order = orders[0].attributes
        if order["cancelled_at"]:
            return "El pedido ha sido cancelado"

        if order["financial_status"] != "paid":
            return "El pedido aún no ha sido pagado"

        if order["fulfillment_status"] != "fulfilled":
            return "Estamos preparando tu pedido 💞"

        return "El pedido está listo y en proceso de envío"

    return False


def get_status_message_from_alas(code):
    alas_url = f"https://integration.alasxpress.com/shopify/{STORE_NAME}/search.php"
    request_data = { 'term': f"#{code}" }

    response = requests.post(url = alas_url, data = request_data)

    if response.status_code != SUCCESS_CODE:
        return 'Ocurrió un error, intenta más tarde.'

    return parse_message_from_alas(response.text)

def parse_message_from_alas(message):
    raw_text = message.replace('<p>', '').replace('</p>', '\ns').strip()

    for known_status_message in KNOWN_STATUS_MESSAGES_MAPPING:
        alas_substring, new_message = known_status_message
        if alas_substring in raw_text:
            return new_message

    return raw_text

def get_status_from_code(code):
    if not re.fullmatch(STORE_CODE_REGEX, code):
        return "El código debe ser de la forma 'MODEXXXX'"

    shopify_status = get_status_from_shopify(code)
    if not shopify_status:
        return "No encontramos el pedido 😞"

    if shopify_status != "El pedido está listo y en proceso de envío":
        return shopify_status

    message_from_alas = get_status_message_from_alas(code)
    code_not_registered_message = "no existe"

    if code_not_registered_message in message_from_alas:
        return "Tu paquete ya está listo 💞. Llegará en un plazo máximo de 24 horas hábiles."

    return message_from_alas
