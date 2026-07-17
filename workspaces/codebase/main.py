import asyncio
import logging
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN
from database.db import init_db
from aiohttp import web

logging.basicConfig(level=logging.INFO)

async def health_handler(request):
    return web.Response(text="OK", status=200)

async def start_health_server():
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()
    logging.info("Health server started on port 8000")

async def main():
    # Initialize database
    init_db()

    # Start health-check HTTP server
    await start_health_server()

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
