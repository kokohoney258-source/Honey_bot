import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Render က Bot ကို မရပ်အောင် Web Server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Honey Downloader Bot is running!")


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()


threading.Thread(target=run_web_server, daemon=True).start()


# Telegram Settings
API_ID = 24391484
API_HASH = "8515c0e7fb4d402b8d0ca5043586aa48"
BOT_TOKEN = os.environ.get("TOKEN")

# မင်း Channel username
CHANNEL_USERNAME = "@hninthanzin77"


app = Client(
    "video_downloader_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# User က Channel Join ထားလားစစ်မယ်
async def is_subscribed(client, user_id):
    try:
        user = await client.get_chat_member(CHANNEL_USERNAME, user_id)

        if str(user.status) in [
            "ChatMemberStatus.OWNER",
            "ChatMemberStatus.ADMINISTRATOR",
            "ChatMemberStatus.MEMBER",
            "owner",
            "administrator",
            "member"
        ]:
            return True

        return False

    except Exception:
        return False


# Channel Join Keyboard
def join_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 Channel လေးကို Join ပေးပါ",
                url="https://t.me/hninthanzin77"
            )
        ],
        [
            InlineKeyboardButton(
                "🔄 Join ပြီးပါပြီ",
                callback_data="check_sub"
            )
        ]
    ])


# /start
@app.on_message(filters.command("start"))
async def start_command(client, message):

    user_id = message.from_user.id

    if not await is_subscribed(client, user_id):

        await message.reply(
            "🌸 မင်္ဂလာပါရှင့်… 🌸\n\n"
            "💕 Honey Downloader Bot မှ ကြိုဆိုပါတယ်ရှင့်။\n\n"
            "ဒီ Bot ကို အသုံးပြုမယ်ဆိုရင် အောက်က "
            "ကျွန်မတို့ Channel လေးကို အရင် Join ပေးပါနော်။\n\n"
            "✨ Channel Join ပြီးရင်\n"
            "🔄 “Join ပြီးပါပြီ” ကိုနှိပ်ပါရှင့်။",
            reply_markup=join_keyboard()
        )

        return

    await message.reply(
        "🎉 မင်္ဂလာပါရှင့်… ကြိုဆိုပါတယ် 💕\n\n"
        "✨ TikTok / YouTube / Facebook စတဲ့\n"
        "Link တွေကို ဒီမှာပို့နိုင်ပါတယ်ရှင့်။\n\n"
        "📹 Video ဖြစ်ရင် Video အဖြစ်\n"
        "🖼️ Photo ဖြစ်ရင် Photo အဖြစ်\n"
        "📥 ရယူပို့ပေးပါမယ်ရှင့်။\n\n"
        "💗 Link ကို ပို့လိုက်ပါနော်…"
    )


# Join ပြီးပြီလားစစ်မယ်
@app.on_callback_query(filters.regex("^check_sub$"))
async def check_subscription(client, callback_query):

    user_id = callback_query.from_user.id

    if await is_subscribed(client, user_id):

        await callback_query.message.edit_text(
            "🎉 ကျေးဇူးတင်ပါတယ်ရှင့် 💕\n\n"
            "အခု Bot ကို အသုံးပြုလို့ရပါပြီ။\n\n"
            "📹 Video Link\n"
            "🖼️ Photo Link\n\n"
            "ပို့လိုက်ရုံနဲ့ ရယူပေးပါမယ်ရှင့် ✨"
        )

        await callback_query.answer("အဆင်ပြေပါပြီ 💕")

    else:
        await callback_query.answer(
            "🥺 Channel ကို အရင် Join ပေးပါနော်။",
            show_alert=True
        )


# Link Download
@app.on_message(filters.text & ~filters.command(["start"]))
async def download_media(client, message):

    user_id = message.from_user.id

    # Channel မ Join ရသေးရင်
    if not await is_subscribed(client, user_id):

        await message.reply(
            "🔒 Bot ကိုအသုံးပြုရန်\n"
            "အရင်ဆုံး Channel လေးကို Join ပေးပါရှင့် 💕",
            reply_markup=join_keyboard()
        )

        return


    url = message.text.strip()


    # URL မဟုတ်ရင်
    if not (
        url.startswith("http://")
        or url.startswith("https://")
    ):
        await message.reply(
            "❌ Link မှန်ကန်မှုမရှိပါရှင့်။\n\n"
            "📎 Video သို့မဟုတ် Photo Link ကို\n"
            "ပို့ပေးပါနော်။"
        )
        return


    m = await message.reply(
        "⏳ Link ကို စစ်ဆေးနေပါပြီ...\n"
        "ခဏလေးစောင့်ပေးပါရှင့် 💕"
    )


    os.makedirs("downloads", exist_ok=True)


    ydl_opts = {
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "format": "best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }


    try:

        # Media ရယူမယ်
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            # Playlist/entries ဖြစ်ရင် ပထမ Media ကိုယူ
            if "entries" in info and info["entries"]:

                info = next(
                    entry
                    for entry in info["entries"]
                    if entry
                )

            filename = ydl.prepare_filename(info)


        # File မရှိရင် downloads folder ထဲရှာ
        if not os.path.exists(filename):

            media_id = str(info.get("id", ""))

            for file in os.listdir("downloads"):

                if media_id in file:

                    filename = os.path.join(
                        "downloads",
                        file
                    )

                    break


        if not os.path.exists(filename):

            await m.edit_text(
                "❌ Media File ကို မတွေ့ပါရှင့်။\n"
                "နောက်တစ်ခါ ပြန်စမ်းပေးပါနော်။"
            )

            return


        await m.edit_text(
            "📤 Media ကို ပို့နေပါပြီ...\n"
            "ခဏလေးစောင့်ပေးပါရှင့် 💕"
        )


        # File extension စစ်မယ်
        extension = filename.lower().split(".")[-1]


        photo_extensions = [
            "jpg",
            "jpeg",
            "png",
            "webp"
        ]


        if extension in photo_extensions:

            await message.reply_photo(
                photo=filename,
                caption="🖼️ Honey Downloader Bot မှ ရယူပေးပါတယ်ရှင့် 💕"
            )

        else:

            await message.reply_video(
                video=filename,
                caption="📹 Honey Downloader Bot မှ ရယူပေးပါတယ်ရှင့် 💕",
                supports_streaming=True
            )


        # Download ပြီးရင် File ဖျက်မယ်
        if os.path.exists(filename):

            os.remove(filename)


        await m.delete()


    except Exception as e:

        print(e)

        await m.edit_text(
            "❌ Download မရသေးပါရှင့် 🥺\n\n"
            "🔹 Link က မမှန်နိုင်ပါတယ်\n"
            "🔹 Post ကို Private ထားနိုင်ပါတယ်\n"
            "🔹 Website ဘက်က ယာယီပြဿနာဖြစ်နိုင်ပါတယ်\n\n"
            "ခဏနေရင် ပြန်စမ်းကြည့်ပေးပါနော် 💕"
        )


if __name__ == "__main__":
    app.run()

