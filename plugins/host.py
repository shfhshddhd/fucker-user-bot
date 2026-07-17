import asyncio
import re
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded
from database.db import add_user, get_user, remove_user, get_all_users

# Temporary storage for login flow
login_states = {}
running_userbots = {}

@Client.on_message(filters.command("host"))
async def host_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if already hosted
    existing = get_user(user_id)
    if existing:
        await message.reply_text(
            "⚠️ **Aap already hosted hain!**\n\n"
            "Agar phir se host karna hai to pehle `/unhost` karein."
        )
        return
    
    await message.reply_text(
        "📱 **Host Process Started!**\n\n"
        "Kripya apna **phone number** international format mein bhejein:\n"
        "Jaise: `+919876543210`\n\n"
        "Ya /cancel karein."
    )
    
    login_states[user_id] = {"step": "phone"}


@Client.on_message(filters.command("unhost"))
async def unhost_command(client: Client, message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if not user:
        await message.reply_text("❌ Aap hosted nahi hain!")
        return
    
    # Stop userbot if running
    if user_id in running_userbots:
        try:
            await running_userbots[user_id].stop()
        except:
            pass
        del running_userbots[user_id]
    
    # Remove session file
    session_path = f"sessions/user_{user_id}.session"
    if os.path.exists(session_path):
        os.remove(session_path)
    
    remove_user(user_id)
    await message.reply_text("✅ **Unhost successful!** Aapka account remove kar diya gaya hai.")


@Client.on_message(filters.command("restart"))
async def restart_userbot(client: Client, message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if not user:
        await message.reply_text("❌ Pehle `/host` karein!")
        return
    
    await message.reply_text("🔄 UserBot restart ho raha hai...")
    
    # Stop existing
    if user_id in running_userbots:
        try:
            await running_userbots[user_id].stop()
        except:
            pass
        del running_userbots[user_id]
    
    # Start again
    asyncio.create_task(start_userbot(user_id, user["session_string"]))
    await message.reply_text("✅ UserBot restarted!")


@Client.on_message(filters.text & filters.private)
async def handle_host_steps(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in login_states:
        return
    
    state = login_states[user_id]
    
    # Cancel
    if message.text.strip() == "/cancel":
        # Clean up temp client if exists
        if "temp_client" in state:
            try:
                await state["temp_client"].disconnect()
            except:
                pass
        del login_states[user_id]
        await message.reply_text("❌ **Process cancelled.**")
        return
    
    # ---------- STEP 1: Phone Number ----------
    if state["step"] == "phone":
        phone = message.text.strip()
        if not re.match(r'^\+\d{7,15}$', phone):
            await message.reply_text(
                "❌ **Galat format!**\n\n"
                "Sahi format mein phone number bhejein:\n"
                "`+919876543210`\n\n"
                "Ya /cancel karein."
            )
            return
        
        try:
            # Create a NEW temp client - IMPORTANT: same object will be used for sign_in
            temp_client = Client(
                f"sessions/temp_{user_id}",
                api_id=client.api_id,
                api_hash=client.api_hash,
                in_memory=True  # Don't save session file
            )
            
            await temp_client.connect()
            
            # Send OTP
            sent_code = await temp_client.send_code(phone)
            
            # Save everything in state
            login_states[user_id] = {
                "step": "otp",
                "phone": phone,
                "temp_client": temp_client,
                "phone_code_hash": sent_code.phone_code_hash
            }
            
            await message.reply_text(
                "✅ **OTP bhej diya gaya hai!** 🔢\n\n"
                "Kripya apna **OTP code** bhejein (Sirf numbers):\n"
                "Jaise: `12345`\n\n"
                "Ya /cancel karein."
            )
            
        except Exception as e:
            await message.reply_text(f"❌ Error: `{str(e)}`")
            # Clean up
            if user_id in login_states:
                if "temp_client" in login_states[user_id]:
                    try:
                        await login_states[user_id]["temp_client"].disconnect()
                    except:
                        pass
                del login_states[user_id]
        
        return
    
    # ---------- STEP 2: OTP ----------
    if state["step"] == "otp":
        code = message.text.strip()
        temp_client = state["temp_client"]
        
        try:
            # IMPORTANT: Same temp_client object - WITHOUT disconnecting!
            try:
                signed_in = await temp_client.sign_in(
                    phone_number=state["phone"],
                    phone_code_hash=state["phone_code_hash"],
                    phone_code=code
                )
                
                # Success! Get session string
                session_string = await temp_client.export_session_string()
                
                # Save to database
                add_user(user_id, state["phone"], session_string)
                
                # Disconnect temp client
                try:
                    await temp_client.disconnect()
                except:
                    pass
                
                # Remove temp session file
                temp_session = f"sessions/temp_{user_id}.session"
                if os.path.exists(temp_session):
                    os.remove(temp_session)
                
                # Start the persistent userbot
                asyncio.create_task(start_userbot(user_id, session_string))
                
                # Clean up login state
                del login_states[user_id]
                
                await message.reply_text(
                    "✅ **Host Successful! 🎉**\n\n"
                    "Aapka account ab linked hai!\n\n"
                    "**Agle steps:**\n"
                    "1️⃣ `/add @username` se target add karein\n"
                    "2️⃣ Group mein jaake `/connect` karein\n"
                    "3️⃣ Bot automatically targets ko tag karega\n\n"
                    "**Commands:**\n"
                    "`/add @username` - Target add\n"
                    "`/remove @username` - Target hatayein\n"
                    "`/list` - Targets dekhein\n"
                    "`/connect` - Group connect karein\n"
                    "`/restart` - UserBot restart\n"
                    "`/unhost` - Account hataayein"
                )
            
            except SessionPasswordNeeded:
                # 2FA required
                login_states[user_id]["step"] = "password"
                await message.reply_text(
                    "🔐 **2-Step Verification** active hai!\n\n"
                    "Apna **password** bhejein:"
                )
            
        except PhoneCodeInvalid:
            await message.reply_text(
                "❌ **Galat OTP!** ❌\n\n"
                "Sahi OTP dobara bhejein:"
            )
        except PhoneCodeExpired:
            await message.reply_text(
                "❌ **OTP expire ho gaya!** ⏰\n\n"
                "Wapas `/host` karke naya OTP lijiye."
            )
            # Clean up
            if user_id in login_states:
                if "temp_client" in login_states[user_id]:
                    try:
                        await login_states[user_id]["temp_client"].disconnect()
                    except:
                        pass
                del login_states[user_id]
        except Exception as e:
            await message.reply_text(f"❌ Error: `{str(e)}`")
            if user_id in login_states:
                if "temp_client" in login_states[user_id]:
                    try:
                        await login_states[user_id]["temp_client"].disconnect()
                    except:
                        pass
                del login_states[user_id]
        
        return
    
    # ---------- STEP 3: 2FA Password ----------
    if state["step"] == "password":
        password = message.text.strip()
        temp_client = state["temp_client"]
        
        try:
            await temp_client.check_password(password)
            
            # Success!
            session_string = await temp_client.export_session_string()
            add_user(user_id, state["phone"], session_string)
            
            try:
                await temp_client.disconnect()
            except:
                pass
            
            # Remove temp session
            temp_session = f"sessions/temp_{user_id}.session"
            if os.path.exists(temp_session):
                os.remove(temp_session)
            
            # Start userbot
            asyncio.create_task(start_userbot(user_id, session_string))
            
            del login_states[user_id]
            
            await message.reply_text(
                "✅ **Host Successful! 🎉**\n\n"
                "Aapka account ab linked hai! (`2FA` enabled)"
            )
            
        except Exception as e:
            await message.reply_text(
                "❌ **Galat password!**\n\n"
                "Dobara try karein:"
            )


async def start_userbot(user_id, session_string):
    """Start userbot for auto-tag monitoring"""
    try:
        from config import API_ID, API_HASH
        
        userbot = Client(
            f"sessions/user_{user_id}",
            session_string=session_string,
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True,
            workers=4
        )
        
        await userbot.start()
        print(f"✅ UserBot started for user {user_id}")
        
        # Store in running dict
        running_userbots[user_id] = userbot
        
        @userbot.on_message(filters.group & filters.text)
        async def auto_tag_handler(ubot: Client, msg: Message):
            try:
                # Get all targets
                from database.db import get_all_targets
                all_targets = get_all_targets()
                
                for target in all_targets:
                    if target["host_user_id"] == user_id and target["target_user_id"] == msg.from_user.id:
                        # Target found - reply
                        await msg.reply_text(
                            f"👋 **@{msg.from_user.username or 'User'}!**"
                        )
                        break
            except Exception as e:
                print(f"Auto-tag error for {user_id}: {e}")
        
        # Keep running
        await asyncio.Event().wait()
        
    except Exception as e:
        print(f"❌ UserBot failed for {user_id}: {e}")
