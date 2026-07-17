import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded
from database.db import add_user, get_user, remove_user

# Store temporary login states
login_states = {}

@Client.on_message(filters.command("host"))
async def host_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if already hosted
    existing = get_user(user_id)
    if existing:
        await message.reply_text("⚠️ Aap already hosted hain! Pehle `/unhost` karein ya phir se host karna hai to.")
        return
    
    await message.reply_text(
        "📱 **Host Process Started!**\n\n"
        "Kripya apna **phone number** bhejein (international format mein):\n"
        "Jaise: `+919876543210`\n\n"
        "Ya /cancel karke cancel kar sakte hain."
    )
    
    login_states[user_id] = {"step": "phone"}


@Client.on_message(filters.text & filters.private)
async def handle_host_steps(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in login_states:
        return
    
    state = login_states[user_id]
    
    # Cancel
    if message.text == "/cancel":
        del login_states[user_id]
        await message.reply_text("❌ Process cancelled.")
        return
    
    # Step 1: Phone number
    if state["step"] == "phone":
        phone = message.text.strip()
        if not re.match(r'^\+\d{7,15}$', phone):
            await message.reply_text("❌ Galat format! Sahi phone number bhejein:\n`+919876543210`")
            return
        
        try:
            # Create temp client for verification
            temp_client = Client(
                f"sessions/temp_{user_id}",
                api_id=client.api_id,
                api_hash=client.api_hash
            )
            await temp_client.connect()
            
            sent_code = await temp_client.send_code(phone)
            
            login_states[user_id] = {
                "step": "otp",
                "phone": phone,
                "temp_client": temp_client,
                "phone_code_hash": sent_code.phone_code_hash
            }
            
            await message.reply_text(
                "✅ OTP bhej diya gaya hai!\n\n"
                "Kripya **OTP code** bhejein:\n"
                "Jaise: `12345`\n\n"
                "Ya agr 2-step verification hai to password bhejein."
            )
            
        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")
            if user_id in login_states:
                del login_states[user_id]
        
        return
    
    # Step 2: OTP
    if state["step"] == "otp":
        code = message.text.strip()
        temp_client = state["temp_client"]
        
        try:
            # Try to sign in with OTP
            try:
                await temp_client.sign_in(
                    phone_number=state["phone"],
                    phone_code=code,
                    phone_code_hash=state["phone_code_hash"]
                )
            except SessionPasswordNeeded:
                # 2-step verification
                login_states[user_id]["step"] = "password"
                login_states[user_id]["temp_client"] = temp_client
                await message.reply_text("🔐 **2-Step Verification** active hai!\n\nApna password bhejein:")
                return
            
            # Success - get session string
            session_string = await temp_client.export_session_string()
            
            # Save to database
            add_user(user_id, state["phone"], session_string)
            
            await temp_client.disconnect()
            
            # Start userbot
            asyncio.create_task(start_userbot(user_id, session_string))
            
            del login_states[user_id]
            
            await message.reply_text(
                "✅ **Host Successful!** 🎉\n\n"
                "Aapka account ab linked hai! Ab aap `/add @username` se target add kar sakte hain.\n\n"
                "**Important:** Bot abhi aapke account se groups mein messages monitor karega aur targets ko auto-tag karega."
            )
            
        except PhoneCodeInvalid:
            await message.reply_text("❌ Galat OTP! Dobara bhejein:")
        except PhoneCodeExpired:
            await message.reply_text("❌ OTP expire ho gaya! /host dobara karein.")
            if user_id in login_states:
                del login_states[user_id]
        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")
            if user_id in login_states:
                del login_states[user_id]
        
        return
    
    # Step 3: 2FA Password
    if state["step"] == "password":
        password = message.text.strip()
        temp_client = state["temp_client"]
        
        try:
            await temp_client.check_password(password)
            
            # Success
            session_string = await temp_client.export_session_string()
            add_user(user_id, state["phone"], session_string)
            await temp_client.disconnect()
            
            asyncio.create_task(start_userbot(user_id, session_string))
            
            del login_states[user_id]
            
            await message.reply_text(
                "✅ **Host Successful!** 🎉\n\n"
                "Aapka account ab linked hai!"
            )
            
        except Exception as e:
            await message.reply_text(f"❌ Galat password! Dobara bhejein:")
        
        return


@Client.on_message(filters.command("unhost"))
async def unhost_command(client: Client, message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if not user:
        await message.reply_text("❌ Aap hosted nahi hain!")
        return
    
    remove_user(user_id)
    
    # Stop userbot if running
    if user_id in running_userbots:
        running_userbots[user_id].stop()
        del running_userbots[user_id]
    
    await message.reply_text("✅ Unhost successful! Aapka account remove kar diya gaya hai.")


# Store running userbots
running_userbots = {}

async def start_userbot(user_id, session_string):
    """Start userbot client for auto-tagging"""
    try:
        from config import API_ID, API_HASH
        
        userbot = Client(
            f"sessions/user_{user_id}",
            session_string=session_string,
            api_id=API_ID,
            api_hash=API_HASH,
            workers=4
        )
        
        await userbot.start()
        
        # Register message handler for auto-tag
        @userbot.on_message(filters.text & filters.group)
        async def auto_tag_handler(client: Client, message: Message):
            target_user_id = message.from_user.id
            
            # Check if this user is a target for someone
            targets = get_all_targets()
            for target in targets:
                if target["target_user_id"] == target_user_id:
                    # Found! Get the host's userbot and reply
                    host_user = get_user(target["host_user_id"])
                    if host_user:
                        await message.reply_text(
                            f"👀 **Target Tagged!**\n"
                            f"From: @{message.from_user.username or 'Unknown'}\n"
                            f"Message: {message.text[:200]}"
                        )
        
        running_userbots[user_id] = userbot
        
        print(f"✅ UserBot started for user {user_id}")
        
        await asyncio.Event().wait()  # Keep running
        
    except Exception as e:
        print(f"❌ UserBot error for {user_id}: {e}")
