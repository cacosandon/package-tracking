import re
import requests
import shopify
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

STORE_NAME = 'modelandola'
STORE_CODE_REGEX = r'MODE[0-9]*'
SUCCESS_CODE = 200

ALAS_TOKEN = os.environ.get("ALAS_TOKEN")

def get_status_from_shopify(code):
    shop_url = "modelandolach.myshopify.com"
    api_version = "2021-10"

    with shopify.Session.temp(shop_url, api_version, os.environ.get("MODELADOLA_TRACKING_TOKEN")):
        orders = shopify.Order.find(name = f"#{code}", status = "any")
        if len(orders) != 1:
            return False

        order = orders[0].attributes

        if order["cancelled_at"]:
            return "El pedido ha sido cancelado."

        if order["financial_status"] != "paid":
            return "El pedido aún no ha sido pagado."

        if order["fulfillment_status"] != "fulfilled":
            return "Estamos preparando tu pedido 💞"

        return "El pedido está listo y en proceso de envío."

    return False


def get_status_message_from_alas(code):
    alas_url = f"https://us-central1-api-ce0-alas.cloudfunctions.net/getDeliveryOrder?token={ALAS_TOKEN}"
    request_data = { 'external_id': f"#{code}" }

    response = requests.post(url = alas_url, data = request_data)

    if response.status_code != SUCCESS_CODE:
        return 'Ocurrió un error, intenta más tarde.'

    return parse_message_from_alas(response.text)

def parse_message_from_alas(message):
    data = json.loads(message)
    if len(data) == 0:
        return "no existe"

    str_datetime = data[0]['time_info']['b2c_delivery_expected']
    datetime_string = datetime.strptime(str_datetime, "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y")

    return f"Tu pedido llegará el {datetime_string}."

def get_status_from_code(code):
    if not re.fullmatch(STORE_CODE_REGEX, code):
        return "El código debe ser de la forma 'MODEXXXX'."

    shopify_status = get_status_from_shopify(code)
    if not shopify_status:
        return "No encontramos el pedido 😞"

    if shopify_status != "El pedido está listo y en proceso de envío.":
        return shopify_status

    message_from_alas = get_status_message_from_alas(code)
    code_not_registered_message = "no existe"

    if code_not_registered_message in message_from_alas:
        return "Tu paquete ya está listo 💞. Llegará en un plazo máximo de 24 horas hábiles. Atenta a tus mensajes de texto!"

    return message_from_alas
