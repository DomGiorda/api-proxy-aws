import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from lambda_function import lambda_handler


class LocalRequestHandler(BaseHTTPRequestHandler):
    def do_ANY(self):
        path = self.path
        method = self.command
        headers = dict(self.headers)
        body = None  # Inicializar body a None por defecto

        try:
            content_length = int(headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else None
        except Exception as e:
            print(f"Error al leer el cuerpo de la solicitud: {e}")

        print(f"Path recibido: {path}")  # Esta línea ahora debería estar bien

        event = {
            'path': path,
            'httpMethod': method,
            'headers': headers,
            'body': body,
            'requestContext': {
                'identity': {
                    'sourceIp': '127.0.0.1'  # IP local para pruebas
                }
            }
        }

        context = {}

        response = lambda_handler(event, context)

        self.send_response(response.get('statusCode', 200))
        response_headers = response.get('headers', {'Content-Type': 'application/json'})
        for key, value in response_headers.items():
            self.send_header(key, value)
        self.end_headers()

        response_body = response.get('body', '')
        if isinstance(response_body, dict):
            self.wfile.write(json.dumps(response_body).encode('utf-8'))
        elif isinstance(response_body, str):
            self.wfile.write(response_body.encode('utf-8'))
        else:
            self.wfile.write(str(response_body).encode('utf-8'))

    def do_GET(self):
        self.do_ANY()

    def do_POST(self):
        self.do_ANY()

    def do_PUT(self):
        self.do_ANY()

    def do_DELETE(self):
        self.do_ANY()

    def do_PATCH(self):
        self.do_ANY()

    def do_OPTIONS(self):
        self.do_ANY()


def run(server_class=HTTPServer, handler_class=LocalRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Servidor local corriendo en http://localhost:{port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Servidor detenido.')


if __name__ == '__main__':
    run()
