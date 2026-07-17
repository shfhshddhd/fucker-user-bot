import asyncio
import logging
import os
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN
from database.db import init_db

# Make sure sessions directory exists
os.makedirs("sessions", exist_ok=True)
os.makedirs("database", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Suppress pyrogram connection logs
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session").setLevel(logging.WARNING)

async def main():
    print("🚀 Initializing database...")
    init_db()
    
    print("🤖 Starting FUCKER USER BOT...")
    
    bot = Client(
        "fucker_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins"),
        workers=8
    )
    
    await bot.start()
    
    bot_info = await bot.get_me()
    print(f"✅ Bot started: @{bot_info.username}")
    
    await idle()
    await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
