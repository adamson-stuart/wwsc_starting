from http.server import HTTPServer, SimpleHTTPRequestHandler

class HTTPHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print ("GET")

class MyHTTPServer(HTTPServer):
    def __init__(self, base_path, server_address, RequestHandlerClass = HTTPHandler):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)

httpd = HTTPServer("",("",8080))
httpd.serve_forever()

