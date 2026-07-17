# 🤖 FUCKER USER BOT v1.0

Multi-user Telegram UserBot jo groups mein targets ko auto-tag karta hai.

## 🚀 Features

- `/host` - Apna account login karein
- `/add @username` - Target add karein
- `/remove @username` - Target hatayein
- `/list` - Targets dekhein
- `/connect` - Group ko connect karein
- Plugin-based architecture - aage naye features easy add

## 🛠 Deploy on Railway (FREE)

### Step 1: GitHub Repository

1. Apne GitHub account mein login karein
2. **New Repository** banayein (Public ya Private)
3. **Upload files** karein - saari files jo maine di hain
4. **Commit changes** karein

### Step 2: Bot banayein (Telegram se)

1. [@BotFather](https://t.me/botfather) pe jaayein
2. `/newbot` bhejein
3. Bot ka naam: `Fucker User Bot`
4. Username: `@fucker_user_bot` (ya kuch aur available)
5. Bot token copy karein

### Step 3: API ID + Hash

1. [my.telegram.org](https://my.telegram.org/apps) pe jaayein
2. Login karein
3. **API ID** aur **API Hash** copy karein

### Step 4: Railway Deploy

1. [Railway.app](https://railway.app) pe jaayein
2. GitHub se connect karein
3. **New Project** → **Deploy from GitHub repo**
4. Apni repo select karein
5. **Variables** mein daalein:
   - `API_ID` = aapka API ID
   - `API_HASH` = aapka API Hash
   - `BOT_TOKEN` = BotFather se token
   - `ADMIN_ID` = aapka Telegram ID
6. **Deploy** button dabayein!

### Step 5: Use karein

1. Apne bot ko start karein: `/start`
2. Phir `/host` se apna account login karein
3. `/add @username` se target add karein
4. Group mein jaake `/connect` karein
5. Ab jab bhi target group mein message karega, bot auto-tag karega!

## 🔧 Plugin System

Naye commands add karne ke liye:
1. `plugins/` folder mein naya `.py` file banayein
2. Command handler likhein
3. Bot restart karein

## ⚠️ Disclaimer

This bot is for educational purposes only. Use responsibly.
