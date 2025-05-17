import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from moviepy.editor import VideoFileClip

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь видео, и я вырежу хайлайт.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        await update.message.reply_text("Пожалуйста, отправь видеофайл.")
        return

    file = await context.bot.get_file(video.file_id)
    file_path = f"{video.file_id}.mp4"
    await file.download_to_drive(file_path)

    output_path = f"highlight_{video.file_id}.mp4"
    clip = VideoFileClip(file_path).subclip(0, min(10, video.duration))
    clip.write_videofile(output_path, codec="libx264")

    await update.message.reply_video(video=open(output_path, "rb"))
    os.remove(file_path)
    os.remove(output_path)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
app.run_polling()
