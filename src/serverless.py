from http.server import HTTPServer, BaseHTTPRequestHandler
import imp
import json
import socketserver
from typing import Tuple
import logging

def loadModule(module_name):
    fp, path, desc = imp.find_module(module_name)
    httpObj = imp.load_module("% s.% s" % (module_name, "http"), fp, path, desc)
    return httpObj

class S(BaseHTTPRequestHandler):
    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer) -> None:
        module = loadModule("serve")
        httpObj = module.http()

        self.getHandler = httpObj.getHandler

        try:
            self.postHandler = httpObj.postHandler
        except:
            self.postHandler = None

        try:
            self.headHandler = httpObj.headHandler
        except:
            self.headHandler = None

        super().__init__(request, client_address, server)
        
    def _set_headers(self, headers):
        self.send_response(200)
        for header, val in headers.items():
            self.send_header(header, val)
        self.end_headers()

    def _serialise(self, ds):
        json_string = json.dumps(ds)
        return json_string.encode(encoding='utf_8')

    def _log(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))

    def do_GET(self):
        self.getHandler(self)

    def do_HEAD(self):
        self.headHandler(self)

    def do_POST(self):
        self.postHandler(self)

def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8080):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"⚡Starting serverless server on {addr}:{port}")
    httpd.serve_forever()