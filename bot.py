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
import os
import base64

# تحميل ملف .env
load_dotenv()

# قراءة التوكن والمفتاح
BOT_TOKEN = os.getenv("8977843494:AAHQuMmrfbBTu0GtJII5E5BDfb5Vt3ooCbo")
OPENAI_API_KEY = os.getenv("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")

# تشغيل OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# حفظ المحادثات
memory = {}

# رسالة البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 اهلاً بك\n"
        "انا بوت ذكاء اصطناعي مثل ChatGPT و Gemini\n"
        "ارسل رسالة او صورة للتحليل."
    )

# الرد على الرسائل النصية
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append({
        "role": "user",
        "content": text
    })

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "أنت مساعد ذكي احترافي مثل ChatGPT و Gemini. "
                    "تجيب بالعربية والانكليزية وتساعد في البرمجة والتحليل."
                )
            },
            *memory[user_id]
        ]
    )

    reply = response.choices[0].message.content

    memory[user_id].append({
        "role": "assistant",
        "content": reply
    })

    await update.message.reply_text(reply)

# تحليل الصور
async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🔍 جاري تحليل الصورة...")

    photo = update.message.photo[-1]

    file = await context.bot.get_file(photo.file_id)

    image_path = "image.jpg"

    await file.download_to_drive(image_path)

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "قم بتحليل هذه الصورة بالتفصيل"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )

    result = response.choices[0].message.content

    await update.message.reply_text(result)

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()

# الأوامر
app.add_handler(CommandHandler("start", start))

# الرسائل النصية
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# الصور
app.add_handler(MessageHandler(filters.PHOTO, analyze_image))

print("✅ البوت يعمل...")

app.run_polling()
