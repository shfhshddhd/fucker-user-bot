from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    text = """👋 **Welcome to FUCKER USER BOT!**

**Commands:**
• `/host` - Apna account login karein
• `/add @username` - Target add karein
• `/remove @username` - Target hatayein
• `/list` - Targets dekhein
• `/groups` - Linked groups dekhein

Made with ❤️ by @fuckeruserbot"""
    await message.reply_text(text)
