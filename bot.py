import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("TOKEN")
CHANNEL = "@hninthanzin77"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=user.id)
        if member.status in ['left', 'kicked']:
            raise Exception("Not member")
    except:
        kb = [[InlineKeyboardButton("📢 Channel Join ရန်", url="https://t.me/hninthanzin77")],
              [InlineKeyboardButton("✅ Join ပြီးပါပြီ", callback_data="check")]]
        await update.message.reply_text("ကျေးဇူးပြု၍ ပထမဦးစွာ Channel Join ပါ။", reply_markup=InlineKeyboardMarkup(kb))
        return
    await update.message.reply_text("မင်္ဂလာပါ! ဗီဒီယို Link ပို့ပေးပါ။")

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=query.from_user.id)
        if member.status not in ['left', 'kicked']:
            await query.message.edit_text("ကျေးဇူးတင်ပါတယ်! Link ပို့ပြီး ဒေါင်းလို့ရပါပြီ။")
            return
    except:
        pass
    await query.answer("❌ Channel ကို မဝင်ရသေးပါ။", show_alert=True)

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return
    msg = await update.message.reply_text("⏳ ဒေါင်းလုပ်ဆွဲနေပါပြီ...")
    try:
        with yt_dlp.YoutubeDL({'format': 'best', 'outtmpl': 'vid.%(ext)s', 'max_filesize': 50*1024*1024}) as ydl:
            info = ydl.extract_info(url, download=True)
            f = ydl.prepare_filename(info)
        await update.message.reply_video(video=open(f, 'rb'))
        os.remove(f)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ အမှား: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    app.run_polling()

if __name__ == "__main__":
    main()
