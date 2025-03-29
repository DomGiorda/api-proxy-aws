import unittest
import json
from lambda_function import lambda_handler, ip_rate_limits, REQUESTS_PER_MINUTE_IP

class TestRateLimiting(unittest.TestCase):

    def setUp(self):
        # Establecer un límite de velocidad bajo para facilitar la prueba
        global REQUESTS_PER_MINUTE_IP
        self.original_rate_limit = REQUESTS_PER_MINUTE_IP
        REQUESTS_PER_MINUTE_IP = 2  # Por ejemplo, 2 requests por minuto

        # Limpiar los contadores de rate limit antes de cada prueba
        ip_rate_limits.clear()

    def tearDown(self):
        # Restaurar el límite de velocidad original después de la prueba
        global REQUESTS_PER_MINUTE_IP
        REQUESTS_PER_MINUTE_IP = self.original_rate_limit

        # Limpiar los contadores de rate limit después de cada prueba
        ip_rate_limits.clear()

    def test_ip_rate_limit_exceeded(self):
        mock_event = {
            'path': '/categories/MLA1055',
            'httpMethod': 'GET',
            'headers': {'Host': 'localhost:8080', 'User-Agent': 'test', 'Accept': '*/*'},
            'body': None,
            'requestContext': {
                'identity': {
                    'sourceIp': '192.168.1.1'
                }
            }
        }
        context = {}

        # La primera solicitud debería pasar
        response1 = lambda_handler(mock_event, context)
        self.assertEqual(response1['statusCode'], 200)

        # La segunda solicitud debería pasar
        response2 = lambda_handler(mock_event, context)
        self.assertEqual(response2['statusCode'], 200)

        # La tercera solicitud desde la misma IP debería ser rate-limited
        response3 = lambda_handler(mock_event, context)
        self.assertEqual(response3['statusCode'], 429)
        self.assertIn('Too Many Requests - IP Rate Limit', response3['body'])

    def test_ip_rate_limit_reset_after_minute(self):
        mock_event = {
            'path': '/categories/MLA1132',
            'httpMethod': 'GET',
            'headers': {'Host': 'localhost:8080', 'User-Agent': 'test', 'Accept': '*/*'},
            'body': None,
            'requestContext': {
                'identity': {
                    'sourceIp': '192.168.1.2'
                }
            }
        }
        context = {}

        # Dos solicitudes iniciales
        response1 = lambda_handler(mock_event, context)
        self.assertEqual(response1['statusCode'], 200)
        response2 = lambda_handler(mock_event, context)
        self.assertEqual(response2['statusCode'], 200)

        # Tercera solicitud debería ser rate-limited
        response3 = lambda_handler(mock_event, context)
        self.assertEqual(response3['statusCode'], 429)

        # Esperar más de un minuto (61 segundos para asegurar que el contador se reinicie)
        import time
        time.sleep(61)

        # La siguiente solicitud después de esperar debería pasar
        response4 = lambda_handler(mock_event, context)
        self.assertEqual(response4['statusCode'], 200)

if __name__ == '__main__':
    unittest.main()