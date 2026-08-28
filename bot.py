import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

API_ID = 24391484
API_HASH = "8515c0e7fb4d402b8d0ca5043586aa48"
BOT_TOKEN = os.environ.get("TOKEN")

CHANNEL_USERNAME = "@hninthanzin77" 

app = Client("video_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def is_subscribed(client, user_id):
    try:
        user = await client.get_chat_member(CHANNEL_USERNAME, user_id)
        if user.status in ["creator", "administrator", "member"]:
            return True
    except Exception:
        return False
    return False

@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    if CHANNEL_USERNAME and not await is_subscribed(client, user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Channel Joinရန်", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("🔄 ချက်ချင်းစစ်မည်", callback_data="check_sub")]
        ])
        await message.reply(
            "မင်္ဂလာပါရှင့်! 🌸 ကျေးဇူးပြု၍ ကျွန်ုပ်တို့၏ Channel လေးကို အရင် Join ပေးပါနော်။ ပြီးမှ Bot ကို ဆက်သုံးလို့ရပါမယ်ရှင်။",
            reply_markup=keyboard
        )
        return

    await message.reply(
        "မင်္ဂလာပါရှင်! ✨ ကျွန်ုပ်သည် TikTok နှင့် YouTube ဗီဒီယိုများကို ဒေါင်းလုပ်ဆွဲပေးသော Bot ဖြစ်ပါသည်။ ဗီဒီယိုလင့်ခ်ကို ပို့ပေးရုံဖြင့် ဒေါင်းလုပ်ဆွဲပေးပါမည်။"
    )

@app.on_callback_query(filters.regex("check_sub"))
async def check_subscription(client, callback_query):
    user_id = callback_query.from_user.id
    if await is_subscribed(client, user_id):
        await callback_query.message.edit_text("ကျေးဇူးတင်ပါတယ်ရှင်! 🎉 အခု ဗီဒီယိုလင့်ခ်များကို ပို့ပြီး ဒေါင်းလုပ်ဆွဲနိုင်ပါပြီ။")
    else:
        await callback_query.answer("ကျေးဇူးပြု၍ Channel ကို အရင် Join ပေးပါရှင်!", show_alert=True)

@app.on_message(filters.text & ~filters.command(["start"]))
async def download_video(client, message):
    user_id = message.from_user.id
    if CHANNEL_USERNAME and not await is_subscribed(client, user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Channel Joinရန်", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("🔄 ချက်ချင်းစစ်မည်", callback_data="check_sub")]
        ])
        await message.reply(
            "ကျေးဇူးပြု၍ ပထမဦးစွာ ကျွန်ုပ်တို့၏ Channel လေးကို Join ပေးပါရန် မေတ္တာရပ်ခံအပ်ပါတယ်ရှင်။",
            reply_markup=keyboard
        )
        return

    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.reply("ကျေးဇူးပြု၍ မှန်ကန်သော ဗီဒီယိုလင့်ခ် (URL) ကို ပို့ပေးပါရှင်။")
        return

    m = await message.reply("⏳ ဗီဒီယိုကို ရယူနေပါပြီ၊ ခဏစောင့်ပေးပါရှင်...")

    ydl_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'format': 'best',
    }

    try:
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await m.edit_text("📤 ဗီဒီယိုကို ပို့ဆောင်နေပါပြီ...")
        await message.reply_video(video=filename)
        
        if os.path.exists(filename):
            os.remove(filename)
        await m.delete()

    except Exception as e:
        await m.edit_text(f"❌ အမှား: {str(e)}")

if __name__ == "__main__":
app.run()


