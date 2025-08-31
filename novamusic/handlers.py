import os
import asyncio
from typing import List

from hydrogram import filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from .clients import bot
from .db import add_served_chat, get_served_chats, get_sudoers
from .voice import player
from .search import search_youtube, download_audio


SUDO_IDS: List[int] = [int(x) for x in os.getenv("SUDO_IDS", "").split() if x.isdigit()]


def sudo_filter(_, __, message: Message) -> bool:
    return bool(message.from_user and message.from_user.id in SUDO_IDS)


sudo = filters.create(sudo_filter)


def register_handlers() -> None:
    @bot.on_message(filters.command(["ping"], prefixes=["/", ".", "!", ""]))
    async def ping_handler(_, message: Message):
        print(f"[Nova][HANDLER] /ping from={getattr(message.from_user,'id',None)} chat={message.chat.id}")
        await message.reply_text("pong")

    # Debug logging; disable with DEBUG_LOG=0
    @bot.on_message()
    async def debug_any(_, message: Message):
        # default on unless explicitly set to 0
        if os.getenv("DEBUG_LOG", "1") != "0":
            try:
                print(f"[Nova][DBG] msg chat={message.chat.id} from={getattr(message.from_user,'id',None)} text={getattr(message,'text',None)!r}")
            except Exception:
                pass
    @bot.on_message(filters.command(["start"], prefixes=["/", ".", "!", ""]))
    async def start_handler(_, message: Message):
        print(f"[Nova][HANDLER] /start from={getattr(message.from_user,'id',None)} chat={message.chat.id}")
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

    # Fallback for private chats without slash commands
    @bot.on_message(filters.private & filters.text)
    async def fallback_private(_, message: Message):
        text = (message.text or "").strip().lstrip("/").lower()
        print(f"[Nova][HANDLER] fallback_private text={text!r} from={getattr(message.from_user,'id',None)} chat={message.chat.id}")
        if text == "ping":
            return await message.reply_text("pong")
        if text == "start":
            return await start_handler(_, message)

    @bot.on_callback_query(filters.regex("^official_channel$"))
    async def channel_placeholder_cb(_, cq: CallbackQuery):
        await cq.answer("Resmi kanal yakında eklenecek.", show_alert=True)

    @bot.on_message(filters.command(["play"], prefixes=["/", ".", "!", ""]) & filters.group)
    async def play_handler(_, message: Message):
        print(f"[Nova][HANDLER] /play from={getattr(message.from_user,'id',None)} chat={message.chat.id}")
        # 1) Reply ile gelen medya
        if message.reply_to_message and (
            message.reply_to_message.audio or message.reply_to_message.voice
        ):
            media = message.reply_to_message.audio or message.reply_to_message.voice
            file_path = await bot.download_media(media)
        # 2) /play <query> ile arama/indirme
        elif len(message.command) > 1:
            query = message.text.split(None, 1)[1].strip()
            await message.reply_chat_action("typing")
            try:
                title, url = await search_youtube(query)
            except Exception as e:
                return await message.reply_text(f"Arama hatası: {e}")
            await message.reply_text(f"🔎 Bulundu: {title}\n⬇️ İndiriliyor...")
            try:
                file_path = await download_audio(url)
            except Exception as e:
                return await message.reply_text(f"İndirme hatası: {e}")
        else:
            return await message.reply_text("Kullanım: Bir ses mesajına yanıt verin veya /play <şarkı adı> yazın.")
        await player.start()
        await player.play(message.chat.id, file_path)
        await add_served_chat(message.chat.id)
        await message.reply_text("▶️ Çalma kuyruğa alındı veya başlatıldı.")

    @bot.on_message(filters.command(["pause"], prefixes=["/", ".", "!", ""]) & filters.group)
    async def pause_handler(_, message: Message):
        print(f"[Nova][HANDLER] /pause from={getattr(message.from_user,'id',None)} chat={message.chat.id}")
        await player.pause(message.chat.id)
        await message.reply_text("⏸️ Duraklatıldı")

    @bot.on_message(filters.command(["resume"], prefixes=["/", ".", "!", ""]) & filters.group)
    async def resume_handler(_, message: Message):
        print(f"[Nova][HANDLER] /resume from={getattr(message.from_user,'id',None)} chat={message.chat.id}")
        await player.resume(message.chat.id)
        await message.reply_text("▶️ Devam ediyor")

    @bot.on_message(filters.command(["stop"], prefixes=["/", ".", "!", ""]) & filters.group)
    async def stop_handler(_, message: Message):
        print(f"[Nova][HANDLER] /stop from={getattr(message.from_user,'id',None)} chat={message.chat.id}")
        await player.stop(message.chat.id)
        await message.reply_text("🛑 Yayın bitti")

    @bot.on_message(filters.command(["queue"], prefixes=["/", ".", "!", ""]) & filters.group)
    async def queue_handler(_, message: Message):
        print(f"[Nova][HANDLER] /queue from={getattr(message.from_user,'id',None)} chat={message.chat.id}")
        q = player.queues.get(message.chat.id, [])
        if not q:
            return await message.reply_text("Kuyruk boş.")
        await message.reply_text("Kuyruk:\n" + "\n".join(f"- {os.path.basename(p)}" for p in q))

    @bot.on_message(filters.command(["broadcast"], prefixes=["/", ".", "!", ""]) & sudo)
    async def broadcast_handler(_, message: Message):
        print(f"[Nova][HANDLER] /broadcast from={getattr(message.from_user,'id',None)} chat={message.chat.id}")
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

