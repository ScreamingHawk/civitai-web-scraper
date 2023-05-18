import http.server
import socketserver
import os
import json
import random
import configparser
from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, FileSystemLoader

# Configuration
config = configparser.ConfigParser()
config.read("config.ini")
output_dir = config["DEFAULT"]["OutputDir"]
PORT = int(config["DEFAULT"]["ServerPort"])
ITEMS_PER_PAGE = int(config["DEFAULT"]["ItemsPerPage"])
local_images = config["DEFAULT"]["LocalImages"] == 'True'

data = []

def load_image_data():
    print("Loading image data...")
    global data
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
    print(f"{len(data)} image data loaded!")

# Create a custom handler for HTTP requests
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global data

        url_parts = urlparse(self.path)
        path = url_parts.path
        query = parse_qs(url_parts.query)
        search_term = query.get('search', [''])[0]  # Get search term from query params

        if path == '/':
            # Write the HTML page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            env = Environment(loader=FileSystemLoader('.'))
            template = env.get_template('web/template.html')
            output = template.render()
            self.wfile.write(output.encode('utf-8'))

        elif path.startswith(f"/{output_dir}/") or path.startswith('/web/'):
            # Write other static files
            self.send_response(200)
            if path.endswith('.json'):
                self.send_header('Content-type', 'application/json')
            elif path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('.' + path, 'rb') as f:
                self.wfile.write(f.read())

        elif path.startswith("/page/"):
            # Pagination
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            page_number = int(path.split("/")[2])
            start_index = ITEMS_PER_PAGE * (page_number - 1)
            end_index = start_index + ITEMS_PER_PAGE

            if search_term:
                # Filter data based on search term
                filtered_data = [item for item in data if search_term.lower() in json.dumps(item['data']).lower()]
                page_data = filtered_data[start_index:end_index]
            else:
                page_data = data[start_index:end_index]

            self.wfile.write(json.dumps(page_data).encode('utf-8'))

        else:
            # 404 probably
            super().do_GET()

load_image_data()

# Start the server
with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
