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
local_images = config["DEFAULT"]["LocalImages"] == 'True'

# Create a custom handler for HTTP requests
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            files = os.listdir(output_dir)
            jsons = [f for f in files if f.endswith('.json')]
            random.shuffle(jsons)
            data = []
            for json_file in jsons:
                image = None
                with open(f'out/{json_file}', 'r') as f:
                    json_data = json.load(f)
                if local_images:
                    # Find image in file system
                    image = json_file.replace('.json', '.jpg')
                    if image not in files:
                        # Skip it
                        continue
                    image = f'/{output_dir}/{image}'
                elif not json_data["url"] or not json_data['meta']:
                    continue
                else:
                    image = json_data["url"]
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
