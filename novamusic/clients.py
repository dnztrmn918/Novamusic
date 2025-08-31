import os
from dotenv import load_dotenv
from hydrogram import Client
from hydrogram.enums import ParseMode

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
STRING_SESSION = os.getenv("STRING_SESSION", "")

bot = Client(
    name="NovaMusic",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    in_memory=True,
    no_updates=False,
)

assistant = Client(
    name="NovaAssistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION or None,
    parse_mode=ParseMode.HTML,
    in_memory=True,
    no_updates=False,
)

async def start_clients() -> None:
    await bot.start()
    await assistant.start()
    try:
        me_bot = await bot.get_me()
        me_assistant = await assistant.get_me()
        print(f"[Nova] Bot: @{getattr(me_bot, 'username', None)} id={me_bot.id}")
        print(f"[Nova] Assistant: @{getattr(me_assistant, 'username', None)} id={me_assistant.id}")
    except Exception as e:
        print(f"[Nova][WARN] Could not fetch identities: {e}")
