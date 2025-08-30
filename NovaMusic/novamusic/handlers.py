import os
import asyncio
from typing import List

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from .clients import bot
from .db import add_served_chat, get_served_chats, get_sudoers
from .voice import player


SUDO_IDS: List[int] = [int(x) for x in os.getenv("SUDO_IDS", "").split() if x.isdigit()]


def sudo_filter(_, __, message: Message) -> bool:
    return bool(message.from_user and message.from_user.id in SUDO_IDS)


sudo = filters.create(sudo_filter)


def register_handlers() -> None:
    @bot.on_message(filters.command(["start"]))
    async def start_handler(_, message: Message):
        username = "Novamusice_bot"
        buttons = [
            [InlineKeyboardButton("➕ Beni Gruba Ekle", url=f"https://t.me/{username}?startgroup=true")],
            [
                InlineKeyboardButton("💬 Sohbet Grubu", url="https://t.me/sohbetgo_tr"),
                InlineKeyboardButton("📣 Resmi Kanal", callback_data="official_channel")
            ],
            [InlineKeyboardButton("👤 Yapımcı", url="https://t.me/dnztrmnn")],
        ]
        await message.reply_text(
            "👋 Nova Music'e hoş geldin! Aşağıdaki menüyü kullanabilirsin:",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        if message.chat and message.chat.type.name == "PRIVATE":
            pass

    @bot.on_callback_query(filters.regex("^official_channel$"))
    async def channel_placeholder_cb(_, cq: CallbackQuery):
        await cq.answer("Resmi kanal yakında eklenecek.", show_alert=True)

    @bot.on_message(filters.command(["play"]) & filters.group)
    async def play_handler(_, message: Message):
        if not message.reply_to_message or not (
            message.reply_to_message.audio or message.reply_to_message.voice
        ):
            return await message.reply_text("Lütfen bir ses mesajına/şarkıya yanıt verin.")
        media = message.reply_to_message.audio or message.reply_to_message.voice
        file_path = await bot.download_media(media)
        await player.start()
        await player.play(message.chat.id, file_path)
        await add_served_chat(message.chat.id)
        await message.reply_text("▶️ Çalma kuyruğa alındı veya başlatıldı.")

    @bot.on_message(filters.command(["pause"]) & filters.group)
    async def pause_handler(_, message: Message):
        await player.pause(message.chat.id)
        await message.reply_text("⏸️ Duraklatıldı")

    @bot.on_message(filters.command(["resume"]) & filters.group)
    async def resume_handler(_, message: Message):
        await player.resume(message.chat.id)
        await message.reply_text("▶️ Devam ediyor")

    @bot.on_message(filters.command(["stop"]) & filters.group)
    async def stop_handler(_, message: Message):
        await player.stop(message.chat.id)
        await message.reply_text("🛑 Yayın bitti")

    @bot.on_message(filters.command(["queue"]) & filters.group)
    async def queue_handler(_, message: Message):
        q = player.queues.get(message.chat.id, [])
        if not q:
            return await message.reply_text("Kuyruk boş.")
        await message.reply_text("Kuyruk:\n" + "\n".join(f"- {os.path.basename(p)}" for p in q))

    @bot.on_message(filters.command(["broadcast"]) & sudo)
    async def broadcast_handler(_, message: Message):
        if not message.reply_to_message or not (message.reply_to_message.text or message.reply_to_message.photo):
            return await message.reply_text("Yayınlamak için bir metin/medya mesajına yanıt verin.")
        text = message.reply_to_message.text or message.reply_to_message.caption or ""
        count = 0
        for chat_id in await get_served_chats():
            try:
                if message.reply_to_message.photo:
                    photo = message.reply_to_message.photo.file_id
                    await bot.send_photo(chat_id, photo=photo, caption=text)
                else:
                    await bot.send_message(chat_id, text=text)
                count += 1
                await asyncio.sleep(0.05)
            except Exception:
                continue
        await message.reply_text(f"Yayın tamamlandı. Gönderildi: {count}")

