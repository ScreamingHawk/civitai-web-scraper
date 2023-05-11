# civitai-web-scraper

Scrape Civitai for AI generated images and prompts.

## Install

Clone the repo with:

```sh
git clone https://github.com/ScreamingHawk/civitai-web-scraper.git
```

Initialise the python environment:

```sh
py -m venv venv
.\venv\Scripts\activate
py -m pip install -r requirements.txt
```

Run the following and then update the config values

```sh
cp config.example.ini config.ini
```

## Usage

Run the script

```sh
py scrape_civitai.py
```

Run the server

```sh
py server.py
```
