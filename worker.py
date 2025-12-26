from http.server import HTTPServer, BaseHTTPRequestHandler
class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
HTTPServer(('0.0.0.0', 8080), Health).serve_forever()