import json
import requests
import time
import re

limits = {
    r"^/sites/MLA/categories$": 1000,
    r"^/categories/.*$": 10000,
    r"^/items/.*$": 10,
}
request_counts = {}

# Lista de IPs permitidas. Si esta lista está vacía, se permiten todas las IPs.
ALLOWED_IPS = ["152.152.152.152", "127.0.0.1"]

# Alternativamente, puedes usar una lista de IPs denegadas.
DENIED_IPS = ["192.168.1.100", "10.0.0.5"]

def is_rate_limited(path):
    now = time.time()
    for path_pattern, limit in limits.items():
        if re.match(path_pattern, path):
            if path_pattern not in request_counts or now - request_counts[path_pattern]['timestamp'] > 60:
                request_counts[path_pattern] = {'count': 1, 'timestamp': now}
                return False
            elif request_counts[path_pattern]['count'] >= limit:
                return True
            else:
                request_counts[path_pattern]['count'] += 1
                request_counts[path_pattern]['timestamp'] = now
                return False
    return False

def lambda_handler(event, context):
    print(f"Evento recibido en lambda_handler: {json.dumps(event)}")
    source_ip = event['requestContext']['identity']['sourceIp']
    path = event['path']
    http_method = event['httpMethod']
    headers_in = event['headers']
    body = event.get('body', None)

    print(f"Método HTTP: {http_method}")
    print(f"Ruta: {path}")
    print(f"IP de origen: {source_ip}")
    print(f"Headers recibidos: {json.dumps(headers_in)}")
    print(f"Cuerpo recibido: {body}")

    # Lógica para restringir por IP
    if ALLOWED_IPS:
        if source_ip not in ALLOWED_IPS:
            print(f"IP no permitida: {source_ip}")
            return {
                'statusCode': 403,
                'body': json.dumps({'message': 'Forbidden - IP address not allowed'}),
                'headers': {'Content-Type': 'application/json'}
            }
    elif DENIED_IPS:
        if source_ip in DENIED_IPS:
            print(f"IP denegada: {source_ip}")
            return {
                'statusCode': 403,
                'body': json.dumps({'message': 'Forbidden - IP address denied'}),
                'headers': {'Content-Type': 'application/json'}
            }

    if is_rate_limited(path):
        return {
            'statusCode': 429,
            'body': json.dumps({'message': 'Too Many Requests - Path Rate Limit'}),
            'headers': {'Content-Type': 'application/json'}
        }

    if path == '/':
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'API Proxy is running'}),
            'headers': {'Content-Type': 'application/json'}
        }
    else:
        # Construir la URL de destino
        target_url = f"https://api.mercadolibre.com{path}"
        print(f"URL de destino: {target_url}")

        # Crear una copia de los headers de entrada y eliminar el Host
        headers_to_forward = headers_in.copy()
        if 'Host' in headers_to_forward:
            del headers_to_forward['Host']
        headers_to_forward['Host'] = 'api.mercadolibre.com' # Asegurar el Host correcto

        print(f"Headers a reenviar: {json.dumps(headers_to_forward)}")

        # Reenviar la solicitud
        try:
            response = requests.request(
                method=http_method,
                url=target_url,
                headers=headers_to_forward,
                data=body
            )
            print(f"Código de estado de la respuesta de la API: {response.status_code}")
            print(f"Headers de la respuesta de la API: {json.dumps(dict(response.headers))}")
            print(f"Contenido de la respuesta de la API (primeros 200 chars): {response.content.decode('utf-8')[:200]}")

            # Formatear la respuesta para API Gateway
            headers_out = dict(response.headers)
            headers_out.pop('Content-Encoding', None)
            headers_out.pop('Transfer-Encoding', None)

            return {
                'statusCode': response.status_code,
                'body': response.content.decode('utf-8'),
                'headers': headers_out
            }
        except requests.exceptions.RequestException as e:
            print(f"Error al hacer la solicitud a la API: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'message': f'Error al contactar la API: {e}'}),
                'headers': {'Content-Type': 'application/json'}
            }