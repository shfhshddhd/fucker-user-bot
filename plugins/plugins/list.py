from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import get_targets, get_user

@Client.on_message(filters.command("list"))
async def list_targets(client: Client, message: Message):
    user_id = message.from_user.id
    
    user = get_user(user_id)
    if not user:
        await message.reply_text("❌ Pehle `/host` karein!")
        return
    
    targets = get_targets(user_id)
    
    if not targets:
        await message.reply_text("📭 **Target List:** Empty\n\n/add @username se target add karein.")
        return
    
    text = "🎯 **Your Targets:**\n\n"
    for i, target in enumerate(targets, 1):
        text += f"{i}. @{target['target_username']} (ID: `{target['target_user_id']}`)\n"
    
    text += f"\nTotal: {len(targets)} targets"
    await message.reply_text(text)
