import os

# API credentials - yeh my.telegram.org se lo
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Bot admin - aapka Telegram ID yahan daalo
ADMIN_IDS = [int(os.environ.get("ADMIN_ID", 0))]
