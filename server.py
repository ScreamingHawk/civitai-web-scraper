import http.server
import socketserver
import os
import json
import random
import configparser
from jinja2 import Environment, FileSystemLoader

# Configuration
config = configparser.ConfigParser()
config.read("config.ini")
output_dir = config["DEFAULT"]["OutputDir"]
PORT = int(config["DEFAULT"]["ServerPort"])

# Create a custom handler for HTTP requests
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            files = os.listdir(output_dir)
            images = [f for f in files if f.endswith('.jpg')]
            random.shuffle(images)
            data = []
            for image in images:
                json_file = image.replace('.jpg', '.json')
                if json_file in files:
                    with open(f'out/{json_file}', 'r') as f:
                        json_data = json.load(f)
                    data.append({'image': image, 'data': json_data})

            env = Environment(loader=FileSystemLoader('.'))
            template = env.get_template('web/template.html')
            output = template.render(data=data)
            self.wfile.write(output.encode('utf-8'))
        elif self.path.startswith(f"/{output_dir}/") or self.path.startswith('/web/'):
            self.send_response(200)
            if self.path.endswith('.json'):
                self.send_header('Content-type', 'application/json')
            elif self.path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('.' + self.path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()

# Start the server
with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
