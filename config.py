import os

from dotenv import load_dotenv
from urllib.parse import urlparse


load_dotenv()

bot_token = os.environ["BOT_TOKEN"]
qiwi_token = os.environ["QIWI_TOKEN"]
postgres_url = urlparse(os.environ["DATABASE_URL"])
username = postgres_url.username
password = postgres_url.password
database = postgres_url.path[1:]
hostname = postgres_url.hostname
port = postgres_url.port
