import os
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

TOKEN = os.getenv("8551748426:AAGA9GV9ixiLhYozFIYWo04-hbckiFHy7Eo")   # Render hosting uchun


def search_youtube(query):
    ydl_opts = {
        "quiet": True,
        "format": "best",
        "default_search": "ytsearch10",
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        results = []

        if "entries" in info:
            for entry in info["entries"]:
                results.append({
                    "title": entry.get("title"),
                    "url": entry.get("webpage_url"),
                    "duration": entry.get("duration")
                })

        return results


def download_audio(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "song.%(ext)s",
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3"
        }],
        "max_filesize": 100 * 1024 * 1024
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def download_video(url):
    ydl_opts = {
        "format": "mp4",
        "outtmpl": "video.%(ext)s",
        "quiet": True,
        "max_filesize": 100 * 1024 * 1024
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def message_handler(update, context):
    query = update.message.text
    results = search_youtube(query)

    if not results:
        update.message.reply_text("Hech qanday natija topilmadi 😔")
        return

    buttons = []
    for r in results:
        btn_text = r["title"][:40]
        buttons.append([InlineKeyboardButton(btn_text, callback_data=r["url"])])

    update.message.reply_text(
        "Topilgan qo‘shiqlar 👇\nBirini tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def button_handler(update, context):
    query = update.callback_query
    url = query.data

    query.answer("Yuklanmoqda... ⏳")

    try:
        # AUDIO
        download_audio(url)
        query.message.reply_audio(audio=open("song.mp3", "rb"))

        # VIDEO
        download_video(url)
        query.message.reply_video(video=open("video.mp4", "rb"))

        # YouTube LINK
        query.message.reply_text(f"🔗 Havola:\n{url}")

        os.remove("song.mp3")
        os.remove("video.mp4")

    except Exception as e:
        query.message.reply_text("Xatolik: yuklab bo‘lmadi.")
        print(e)


updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
dp.add_handler(CallbackQueryHandler(button_handler))

updater.start_polling()
