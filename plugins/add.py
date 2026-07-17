from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import add_target, get_user, get_targets

@Client.on_message(filters.command("add"))
async def add_target_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if user is hosted
    user = get_user(user_id)
    if not user:
        await message.reply_text("❌ Pehle `/host` karein apna account!")
        return
    
    # Get target username/ID from command
    if len(message.command) < 2:
        await message.reply_text("Usage: `/add @username` ya `/add 123456789`")
        return
    
    target_input = message.command[1].strip()
    
    # Remove @ symbol if present
    if target_input.startswith('@'):
        target_input = target_input[1:]
    
    # Try to resolve the target
    try:
        # Get userbot for this user
        from plugins.host import running_userbots
        userbot = running_userbots.get(user_id)
        
        if not userbot:
            await message.reply_text("❌ Aapka userbot active nahi hai! /host dobara karein.")
            return
        
        # Try to get user info
        try:
            target_user = await userbot.get_users(target_input)
            target_user_id = target_user.id
            target_username = target_user.username or target_input
        except:
            await message.reply_text("❌ Target user nahi mila! Sahi username ya ID daalein.")
            return
        
        # Check if already added
        existing_targets = get_targets(user_id)
        for t in existing_targets:
            if t["target_user_id"] == target_user_id:
                await message.reply_text(f"⚠️ @{target_username} already target list mein hai!")
                return
        
        # Add to database
        add_target(user_id, target_user_id, target_username)
        
        await message.reply_text(
            f"✅ **Target Added!** 🎯\n\n"
            f"User: @{target_username}\n"
            f"ID: `{target_user_id}`\n\n"
            f"Group mein koi bhi message karein, ye target automatically tag hoga!"
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
