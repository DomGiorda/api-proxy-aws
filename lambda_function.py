import json
import requests
import time

# Simulación de un diccionario para almacenar los contadores de rate limit (NO usar en producción)
ip_rate_limits = {}
REQUESTS_PER_MINUTE_IP = 2  # Ejemplo: 2 requests por minuto por IP

def lambda_handler(event, context):
    print(f"Evento recibido en lambda_handler: {json.dumps(event)}")
    print(f"REQUESTS_PER_MINUTE_IP: {REQUESTS_PER_MINUTE_IP}") # Verificar el valor del límite

    try:
        source_ip = event['requestContext']['identity']['sourceIp']
        path = event['path']
        http_method = event['httpMethod']
        headers_in = event['headers']
        body = event.get('body', None)

        print(f"Método HTTP: {http_method}")
        print(f"Ruta: {path}")
        print(f"Headers recibidos: {json.dumps(headers_in)}")
        print(f"Cuerpo recibido: {body}")
        print(f"ip_rate_limits al inicio de la invocación: {ip_rate_limits}") # Ver el estado del diccionario

        # Rate Limiting por IP (Implementación básica en memoria)
        now = time.time()
        print(f"Tiempo actual: {now}")

        if source_ip not in ip_rate_limits:
            ip_rate_limits[source_ip] = {'count': 1, 'timestamp': now} # Inicializar el contador a 1 en la primera solicitud
            print(f"IP nueva detectada. Inicializando contador para {source_ip}: {ip_rate_limits[source_ip]}")
        else:
            last_request_time = ip_rate_limits[source_ip]['timestamp']
            time_elapsed = now - last_request_time
            print(f"Tiempo transcurrido desde la última solicitud de {source_ip}: {time_elapsed}")

            if time_elapsed > 60:
                ip_rate_limits[source_ip]['count'] = 1 # Reiniciar el contador a 1 después de un minuto
                ip_rate_limits[source_ip]['timestamp'] = now
                print(f"Ha pasado más de un minuto. Reiniciando contador para {source_ip}: {ip_rate_limits[source_ip]}")
            elif ip_rate_limits[source_ip]['count'] >= REQUESTS_PER_MINUTE_IP:
                print(f"Too Many Requests - IP Rate Limit {source_ip}: {ip_rate_limits[source_ip]}")
                return {
                    'statusCode': 429,
                    'body': json.dumps({'message': 'Too Many Requests - IP Rate Limit'}),
                    'headers': {'Content-Type': 'application/json'}
                }
            else:
                ip_rate_limits[source_ip]['count'] += 1
                ip_rate_limits[source_ip]['timestamp'] = now
                print(f"Incrementando contador para {source_ip}: {ip_rate_limits[source_ip]}")

        print(f"ip_rate_limits después de la lógica de rate limit: {ip_rate_limits}") # Ver el estado final del diccionario

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

            headers_to_forward = {
                'User-Agent': headers_in.get('User-Agent', 'python-requests'),
                'Accept': headers_in.get('Accept', '*/*'),
                'Host': 'api.mercadolibre.com'
            }
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

    except Exception as e:
        print(f"Error general en lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error'}),
            'headers': {'Content-Type': 'application/json'}
        }