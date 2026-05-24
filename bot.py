import os
import base64
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)
from openai import OpenAI
from dotenv import load_dotenv

# تحميل المتغيرات (يعمل محلياً من ملف .env، وفي Railway من Variables)
load_dotenv()

BOT_TOKEN = os.getenv("8977843494:AAHQuMmrfbBTu0GtJII5E5BDfb5Vt3ooCbo")
OPENAI_API_KEY = os.getenv("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")

client = OpenAI(api_key=OPENAI_API_KEY)
memory = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك، أنا دراكون، مساعدك الذكي.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in memory:
        memory[user_id] = [{"role": "system", "content": "أنت دراكون، مساعد ذكي ومحترف."}]

    memory[user_id].append({"role": "user", "content": text})
    if len(memory[user_id]) > 11:
        memory[user_id] = [memory[user_id][0]] + memory[user_id][-10:]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=memory[user_id]
        )
        reply = response.choices[0].message.content
        memory[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)
    except Exception as e:
        print(f"Error details: {e}")
        await update.message.reply_text("عذراً، حدث خطأ أثناء الاتصال بالذكاء الاصطناعي. تأكد من إعداد المفاتيح بشكل صحيح.")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🔍 جاري التحليل...")
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_path = f"{photo.file_id}.jpg"
    await file.download_to_drive(image_path)

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "حلل هذه الصورة."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}]
        )
        await update.message.reply_text(response.choices[0].message.content)
    finally:
        if os.path.exists(image_path): os.remove(image_path)
        await status_msg.delete()

# تشغيل البوت
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
    print("✅ دراكون يعمل الآن...")
    app.run_polling(drop_pending_updates=True)
