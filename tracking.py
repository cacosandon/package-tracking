import re
import requests

STORE_NAME = 'modelandola'
STORE_CODE_REGEX = r'MODE[1-9]*'
SUCCESS_CODE = 200

KNOWN_STATUS_MESSAGES_MAPPING = [
    ['Status: Recibido SER', 'Paquete recibido en centro de distribución'],
    ['Status: Entregado', 'Paquete entregado 😊'],
    ['Status: Planificación', 'Tu paquete está en preparación, atenta a tu correo y/o mensaje de texto. Te avisaremos cuando esté en camino :)']
]

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
        return 'El pedido no existe'

    message_from_alas = get_status_message_from_alas(code)
    code_not_registered_message = 'no existe'

    if code_not_registered_message in message_from_alas:
        return 'Tu paquete está en preparación. Llegará en un plazo máximo de 24 horas hábiles.'
    
    return message_from_alas

