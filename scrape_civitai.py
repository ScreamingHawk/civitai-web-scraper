import os
import json
import requests
import configparser

# Configuration
config = configparser.ConfigParser()
config.read("config.ini")
output_dir = config["DEFAULT"]["OutputDir"]
nsfw_level = config["DEFAULT"]["NSFWLevel"]
pages = int(config["DEFAULT"]["Pages"])
page_start = int(config["DEFAULT"]["PageStart"])
local_images = config["DEFAULT"]["LocalImages"] == 'True'

for i in range(page_start, pages + page_start):
    url = f"https://civitai.com/api/v1/images?limit=100&sort=Most Reactions&nsfw={nsfw_level}&page={i}"
    print(url)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for item in data["items"]:
            item_id = item["id"]
            img_filename = f"{output_dir}/{item_id}.jpg"
            json_filename = f"{output_dir}/{item_id}.json"
            if os.path.isfile(json_filename):
                # Already downloaded
                print(f"File {json_filename} already exists.")
            else:
                print(f"Saving {json_filename}.")
                with open(json_filename, "w") as f:
                    # Always save metadata
                    json.dump(item, f, indent=1)
                if item["meta"] and item["url"] and local_images:
                    # Only save images that have metadata
                    image_response = requests.get(item["url"])
                    if image_response.status_code == 200:
                        with open(img_filename, "wb") as f:
                            f.write(image_response.content)
                        print("Image saved successfully!")
                    else:
                        print("Error saving image:", image_response.status_code)
    else:
        print("Error:", response.status_code)
