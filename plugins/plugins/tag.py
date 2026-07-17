from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.host import running_userbots
from database.db import get_targets, get_user
import asyncio

# Store which groups to monitor for each user
user_group_selection = {}

async def get_userbot(user_id):
    return running_userbots.get(user_id)

@Client.on_message(filters.command("connect"))
async def connect_group(client: Client, message: Message):
    """Connect current group for auto-tag"""
    user_id = message.from_user.id
    
    user = get_user(user_id)
    if not user:
        await message.reply_text("❌ Pehle `/host` karein!")
        return
    
    if not message.chat.type in ["group", "supergroup"]:
        await message.reply_text("❌ Yeh command sirf group mein use karein!")
        return
    
    group_id = message.chat.id
    group_title = message.chat.title or "Unknown Group"
    
    # Connect this group
    userbot = running_userbots.get(user_id)
    if userbot:
        # Add handler for this specific group
        @userbot.on_message(filters.chat(group_id))
        async def group_tag_handler(client: Client, message: Message):
            await handle_auto_tag(client, message, user_id)
    
    await message.reply_text(f"✅ **Connected!** Group `{group_title}` ab monitor hoga!")
    await message.delete()

async def handle_auto_tag(client: Client, message: Message, host_user_id):
    """Handle auto-tag for a specific host's targets"""
    try:
        # Get targets for this host
        targets = get_targets(host_user_id)
        if not targets:
            return
        
        # Check if message author is a target
        msg_user_id = message.from_user.id
        
        for target in targets:
            if target["target_user_id"] == msg_user_id:
                # This is a target's message - reply with tag
                await message.reply_text(
                    f"📍 **Target Located!**\n"
                    f"👤 @{message.from_user.username or 'Unknown'}\n"
                    f"💬 {message.text[:300]}"
                )
                break
    except Exception as e:
        print(f"Auto-tag error: {e}")
