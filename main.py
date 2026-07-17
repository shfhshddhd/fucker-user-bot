import asyncio
import logging
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN
from database.db import init_db

logging.basicConfig(level=logging.INFO)

async def main():
    # Initialize database
    init_db()
    
    # Start Bot
    bot = Client(
        "fucker_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins")
    )
    
    await bot.start()
    print("🤖 Fucker User Bot started!")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
