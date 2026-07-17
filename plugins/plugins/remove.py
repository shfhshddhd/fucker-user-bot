from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import remove_target, get_user, get_targets

@Client.on_message(filters.command("remove"))
async def remove_target_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    user = get_user(user_id)
    if not user:
        await message.reply_text("❌ Pehle `/host` karein!")
        return
    
    if len(message.command) < 2:
        await message.reply_text("Usage: `/remove @username` ya `/remove 123456789`")
        return
    
    target_input = message.command[1].strip()
    if target_input.startswith('@'):
        target_input = target_input[1:]
    
    try:
        remove_target(user_id, target_input)
        await message.reply_text(f"✅ `{target_input}` target list se hata diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
